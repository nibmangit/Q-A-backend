from rest_framework import status,generics,filters 
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    UserRegisterSerializer,
    MyTokenObtainPairSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, UserPasswordUpdateSerializer,
    SetNewPasswordSerializer,PublicUserSerializer, BadgeSerializer
)
from rest_framework.response import Response 
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Badge
# For password Reset.
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes  
from django.db.models import Count
from .utils import check_active_user_badge
import resend
import os

#rest password view
User = get_user_model()
class PasswordResetRequestView(generics.GenericAPIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If this email exists, we sent a reset link."}, status=200)
         
        uid = urlsafe_base64_encode(force_bytes(user.pk)) 
        token = PasswordResetTokenGenerator().make_token(user) 

        reset_link = f"https://qand-a-platform.vercel.app/reset-password/{uid}/{token}/"

        subject = "Reset your Question and Answer Password"
        html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; border: 1px solid #eee; padding: 20px;">
                <h2 style="color: #003366;">Password Reset Request</h2>
                <p>You requested a password reset for your Bahir Dar University Student Question and Answer account.</p>
                <div style="margin: 30px 0;">
                    <a href="{reset_link}" 
                    style="background-color: #007BFF; color: #ffffff; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 5px;">
                    Reset My Password
                    </a>
                </div>
                <p style="font-size: 12px; color: #666;">If the button doesn't work, copy this link: {reset_link}</p>
            </div>
        """
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            print("CRITICAL ERROR: RESEND_API_KEY is not set in environment variables!")
            return Response({"error": "Email configuration missing"}, status=500)
            
        resend.api_key = api_key

        try:
            params = {
                "from": "onboarding@resend.dev", # Resend's default for unverified domains
                "to": [user.email],
                "subject": subject,
                "html": html_content,
            }

            resend.Emails.send(params) 
            return Response({"message": "Password reset link sent"}, status=200)
            
        except Exception as e:
            # Log the error to your terminal so you can see it
            print(f"RESEND ERROR: {str(e)}")
            return Response({"error": "Failed to send email via Resend."}, status=500)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password has been reset successfully"}, status=200)
        return Response(serializer.errors, status=400)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs): 
        response = super().post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
 
        check_active_user_badge(user) 
        return response


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = [AllowAny]

    lookup_field = "id"

class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user 
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UserPasswordUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserListView(generics.ListAPIView):
    queryset = User.objects.all().annotate(
        badges_count=Count("badges")
    )
    serializer_class = PublicUserSerializer 
    permission_classes = [AllowAny] 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['email']
    search_fields = ["name", "email"]
    ordering_fields = ["points", "badges_count", "id"]
    ordering = ["-points"]

class TopUsersView(generics.ListAPIView): 
    serializer_class = PublicUserSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return User.objects.filter(
            is_active=True,
            is_superuser=False,
            is_staff=False
        ).order_by('-points')[:10]
 

class BadgeListView(generics.ListAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [AllowAny]