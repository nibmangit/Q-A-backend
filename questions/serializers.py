from rest_framework import serializers
from questions.models import (Question, Answer, Category, Tag,
                              QuestionLike)
from user.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'count']

class AnswerSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    author = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = Answer
        fields = [
            "id", "question", "author", "body",
            "likes", "dislikes",
            "created_at", "updated_at"
        ]
        read_only_fields = ("likes", "dislikes", "author")

    def get_likes(self, obj):
        return obj.likes_users.filter(is_like=True).count()

    def get_dislikes(self, obj):
        return obj.likes_users.filter(is_like=False).count()


class QuestionSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
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
    answers = AnswerSerializer(many=True, read_only=True)  # or source='answer_list' depending on related_name
    image = serializers.ImageField(required=False)

    class Meta:
        model = Question
        fields = [
            "id", "title", "body", "author",
            "category", "tags", "likes", "dislikes",'answers',
            "answers_count", "image", "created_at", "updated_at"
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        question = Question.objects.create(**validated_data)
        question.tags.set(tags)
        return question
    def get_likes(self, obj):
        return obj.likes_users.filter(is_like=True).count()

    def get_dislikes(self, obj):
        return obj.likes_users.filter(is_like=False).count()
