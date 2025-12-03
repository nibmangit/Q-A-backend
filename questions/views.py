from django.shortcuts import render
from rest_framework import generics,permissions
from .models import (Question, Answer, Category, Tag, AnswerLike, QuestionLike,
                     AnswerComment, QuestionBookmark)
from .serializers import (QuestionSerializer, AnswerSerializer, 
                          CategorySerializer, TagSerializer,
                          AnswerCommentSerializer, BookmarkSerializer)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .permissions import IsOwnerOrReadOnly
from notifications.utils import create_notification


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

            if question.author != request.user:
                create_notification(
                    user=question.author,
                    noti_type="answer",
                    message=f"{request.user.name} answerd your question: '{question.title}'",
                    related_object_id=answer.id,
                    related_object_type="Answer"
                )

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

            if answer.author != user:
                if is_like:
                    create_notification(
                        user=answer.author,
                        noti_type="like",
                        message=f"{user.name} liked your answer.",
                        related_object_id=answer.id,
                        related_object_type="Answer"
                    )
                else:
                    create_notification(
                        user=answer.author,
                        noti_type="dislike", 
                        message=f"{user.name} disliked your answer.",
                        related_object_id=answer.id,
                        related_object_type="Answer"
                    )

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
            if existing.is_like:
                question.likes -=1
            else:
                question.dislikes -=1
            existing.delete()
        else:
            QuestionLike.objects.create(question=question, user=request.user, is_like=is_like)
            if is_like:
                question.likes +=1
            else:
                question.dislikes +=1
            if question.author != request.user:
                if is_like:
                    create_notification(
                        user=question.author,
                        noti_type="like",
                        message=f"{request.user.name} liked your question: '{question.title}'",
                        related_object_id=question.id,
                        related_object_type="Question"
                    )
                else:
                    create_notification(
                        user=question.author,
                        noti_type="dislike",
                        message=f"{request.user.name} disliked your question: '{question.title}'",
                        related_object_id=question.id,
                        related_object_type="Question"
                    )
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

        if answer.author != self.request.user:
            create_notification(
                user=answer.author,
                noti_type="comment",
                message=f"{self.request.user.name} commented on your answer",
                related_object_id=answer.id,
                related_object_type="Comment"
            )

class AnswerCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AnswerComment.objects.all()
    serializer_class = AnswerCommentSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]

class ToggleBookmarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        question = Question.objects.get(id=pk)

        bookmark, created = QuestionBookmark.objects.get_or_create(
            user=request.user,
            question=question
        )

        if not created:
            bookmark.delete()
            return Response({"message": "Bookmark removed"}, status=200)

        return Response({"message": "Bookmarked successfully"}, status=201)

class UserBookmarksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookmarks = QuestionBookmark.objects.filter(user=request.user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)