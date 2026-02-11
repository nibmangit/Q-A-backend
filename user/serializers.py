from rest_framework import serializers
from .models import User, Badge
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# rest of password import
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

User = get_user_model()
class SetNewPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        try:
            uid = attrs.get('uid')
            token = attrs.get('token')
            new_password = attrs.get('new_password')

            # Decode UID
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)

            # Check token
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Invalid or expired token")

            attrs['user'] = user
            return attrs

        except Exception:
            raise serializers.ValidationError("Invalid data")

    def save(self, **kwargs):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'name', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('name', '').lower().replace(' ', '_'),
            name=validated_data.get('name', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'student')
        )
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'points', 'bio','is_superuser', 'badges', 'avatar']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = User 
        fields = ['name', 'bio', 'avatar']
        extra_kwargs = {
            'avatar': {'required': False},  # optional
            'bio': {'required': False},
            'name': {'required': False},
        }
        def validate_avatar(self, value): 
            if value: 
                valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
                if value.content_type not in valid_mime_types:
                    raise serializers.ValidationError("Unsupported file type. Allowed: jpg, png, gif.")
 
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError("Avatar file too large. Max size is 5MB.")

            return value



class UserPasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate_new_password(self, value):
        # optional: add password strength validation here
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
class PublicUserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)
    class Meta:
        model = User
        fields = [ "id","email", "name", "avatar", "bio", "points", "badges", "date_joined"]
        read_only_fields = fields
        
class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'icon', 'description']