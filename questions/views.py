from django.shortcuts import render
from rest_framework import generics,permissions
from .models import Question, Answer, Category, Tag
from .serializers import (QuestionSerializer, AnswerSerializer, 
                          CategorySerializer, TagSerializer)
from rest_framework.parsers import MultiPartParser, FormParser
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

class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # For image upload

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # Set author automatically

class AnswerListCreateView(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        question_id = self.request.data.get('question_id')
        serializer.save(author=self.request.user, question_id=question_id)