from django.shortcuts import render
from rest_framework import generics,permissions
from .models import Question, Answer, Category, Tag
from .serializers import (QuestionSerializer, AnswerSerializer, 
                          CategorySerializer, TagSerializer)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
# Create your views here.

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.all().order_by('-created_at')
    serializer_class = QuestionSerializer

class QuestionDetailView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # For image upload

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # Set author automatically

class AnswerListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request): 
        question_id = request.query_params.get("question")

        if not question_id:
            return Response({"error": "question query parameter is required"}, status=400)

        answers = Answer.objects.filter(question_id=question_id).order_by('-created_at')
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["author"] = request.user.id

        serializer = AnswerSerializer(data=data)
        if serializer.is_valid():
            answer = serializer.save(author=request.user)

            # update answers_count
            question = answer.question
            question.answers_count += 1
            question.save(update_fields=['answers_count'])

            return Response(AnswerSerializer(answer).data, status=201)

        return Response(serializer.errors, status=400)

# class QuestionLikeView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, pk):
#         q = get_object_or_404(Question, pk=pk)
#         q.likes = q.likes +1
#         q.save(update_fields=['likes'])
#         return Response({'likes':q.likes}, status=status.HTTP_200_OK)
    
# class QuestionDislikeView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def pest(self, request, pk):
#         q = get_object_or_404(Question, pk = pk)
#         q.dislikes = q.dislikes + 1
#         q.save(update_fields=['dislikes'])

#         return Response({'dislikes':q.dislikes}, status=status.HTTP_200_OK)