from django.urls import path
from .views import (QuestionListCreateView, CategoryListCreateView,
                    TagListCreateView, QuestionDetailView,
                    AnswerListCreateView, AnswerDetailView,
                    TagDetailView,CategoryDetailView,
                    AnswerLikeToggleView, QuestionLikeToggleView,
                    AnswerCommentListCreateView, AnswerCommentDetailView
                    )

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('questions/', QuestionListCreateView.as_view(), name='question-list-create'), 
    path('answers/', AnswerListCreateView.as_view(), name='answer-list-create'),
    #update and delete url
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('answers/<int:pk>/', AnswerDetailView.as_view(), name='answer-detail'),

    #Like and Dislike 
    path('answers/<int:pk>/like-toggle/', AnswerLikeToggleView.as_view(), name='answer-like-toggle'),
    path('questions/<int:pk>/like-toggle/', QuestionLikeToggleView.as_view(), name='question-like-toggle'),

    #comments 
    path("answers/<int:answer_id>/comments/", AnswerCommentListCreateView.as_view(), name="comment-create"),
    path("answers/comments/<int:pk>/", AnswerCommentDetailView.as_view(), name="comment-detail"),
]
#http://127.0.0.1:8000/api/questions/answers/?question=6 get all answer for question 6