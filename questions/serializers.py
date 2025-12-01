from rest_framework import serializers
from questions.models import Question, Answer, Category, Tag
from user.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'count']

class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Question
        fields = [
            "id", "title", "body", "author",
            "category", "tags", "likes", "dislikes",
            "answers_count", "image", "created_at", "updated_at"
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        question = Question.objects.create(**validated_data)
        question.tags.set(tags)
        return question

class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  # shows user email
    question = serializers.PrimaryKeyRelatedField(read_only=True)  # we set question in view

    class Meta:
        model = Answer
        fields = ['id', 'question', 'author', 'body', 'likes', 'dislikes', 'created_at', 'updated_at']