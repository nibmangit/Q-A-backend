from django.urls import path
from .views import (QuestionListCreateView, CategoryListCreateView,
                    TagListCreateView, AnswerListCreateView)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('answers/', AnswerListCreateView.as_view(), name='answer-list-create'),
]