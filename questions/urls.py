from django.urls import path
from .views import (QuestionListCreateView, CategoryListCreateView,
                    TagListCreateView, QuestionListView, QuestionDetailView,
                    AnswerListCreateView,
                    # QuestionLikeView,QuestionDislikeView
                    )

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/list/', QuestionListView.as_view(), name='question-list-create-list'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    # path('questions/<int:pk>/like/', QuestionLikeView.as_view(), name='question-like'),
    # path('questions/<int:pk>/dislike/', QuestionDislikeView.as_view(), name='question-dislike'),
    path('answers/', AnswerListCreateView.as_view(), name='answer-list-create'),
]

#http://127.0.0.1:8000/api/questions/answers/?question=6 get all answer for question 6