from django.shortcuts import render
from rest_framework import generics,permissions
from .models import (Question, Answer, Category, Tag, AnswerLike, QuestionLike,
                     AnswerComment)
from .serializers import (QuestionSerializer, AnswerSerializer, 
                          CategorySerializer, TagSerializer,
                          AnswerCommentSerializer)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .permissions import IsOwnerOrReadOnly

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

 
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

# UPDATE OR DELETE VIEWS
class TagDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permissions_class = [permissions.IsAuthenticated]

class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

class QuestionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_update(self, serializer): 
        serializer.save()

class AnswerDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save()

#Likes and Dislikes

class AnswerLikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            answer = Answer.objects.get(pk=pk)
        except Answer.DoesNotExist:
            return Response({"error": "Answer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        is_like = request.data.get('is_like', True)  # default True if not provided
        user = request.user
 
        existing = AnswerLike.objects.filter(answer=answer, user=user).first()

        if existing: 
            existing.delete()
            if existing.is_like:
                answer.likes -= 1
            else:
                answer.dislikes -= 1
        else: 
            AnswerLike.objects.create(answer=answer, user=user, is_like=is_like)
            if is_like:
                answer.likes += 1
            else:
                answer.dislikes += 1

        answer.save()
        return Response({ "likes": answer.likes, "dislikes": answer.dislikes }, status=status.HTTP_200_OK)
 
class QuestionLikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        is_like = request.data.get('is_like', True)
 
        existing = QuestionLike.objects.filter(question=question, user=request.user).first()
        if existing:
            existing.delete()
            if existing.is_like:
                question.likes -=1
            else:
                question.dislikes -=1
        else:
            QuestionLike.objects.create(question=question, user=request.user, is_like=is_like)
            if is_like:
                question.likes +=1
            else:
                question.dislikes +=1
        
        question.save()
        return Response({"likes": question.likes, "dislikes":question.dislikes}, status=status.HTTP_200_OK)
    
# comments for answers

class AnswerCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = AnswerCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        answer_id = self.kwargs["answer_id"]
        return AnswerComment.objects.filter(answer_id=answer_id)

    def perform_create(self, serializer):
        answer = get_object_or_404(Answer, id=self.kwargs["answer_id"])
        serializer.save(author=self.request.user, answer=answer)

class AnswerCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AnswerComment.objects.all()
    serializer_class = AnswerCommentSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]