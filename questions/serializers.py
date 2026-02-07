from rest_framework import serializers
from questions.models import (Question, Answer, Category, Tag,
                              AnswerComment, QuestionBookmark)
from user.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'count']

class AnswerCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AnswerComment
        fields = ["id", "answer", "author", "body", "created_at","updated_at"]
        read_only_fields = ["id", "author", "created_at","updated_at", "answer"]

class AnswerSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    author = serializers.EmailField(source="author.email", read_only=True)
    comments = AnswerCommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            "id", "question", "author", "body","is_liked", "is_disliked",
            "likes", "dislikes","comments", "comment_count",
            "created_at", "updated_at"
        ]
        read_only_fields = ("likes", "dislikes", "author")
    
    def get_is_liked(self, obj):
        user = self.context.get("request") and self.context.get("request").user
        if not user or user.is_anonymous:
            return False
        return obj.likes_users.filter(user=user, is_like=True).exists()

    def get_is_disliked(self, obj):
        user = self.context.get("request") and self.context.get("request").user
        if not user or user.is_anonymous:
            return False
        return obj.likes_users.filter(user=user, is_like=False).exists()

    def get_likes(self, obj):
        return obj.likes_users.filter(is_like=True).count()

    def get_dislikes(self, obj):
        return obj.likes_users.filter(is_like=False).count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBookmark
        fields = ['id', 'user', 'question', 'created_at']
        read_only_fields = ['user']

class QuestionSerializer(serializers.ModelSerializer): 
    is_bookmarked = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    author = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True )
    tags = serializers.PrimaryKeyRelatedField( queryset=Tag.objects.all(), many=True, required=False )
    answers = AnswerSerializer(many=True, read_only=True) 
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Question
        fields = [
            "id", "title", "body", "author",
            "category", "tags", "likes", "dislikes",'answers',
            "answers_count", "image", "created_at", "updated_at", "is_liked", "is_disliked", "is_bookmarked",
        ]
    
    def validate_image(self, value): 
        if value: 
            valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
            if value.content_type not in valid_mime_types:
                raise serializers.ValidationError("Unsupported file type. Allowed: jpg, png, gif.")
 
            max_size = 5 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError("Image file too large. Max size is 5MB.")

        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        question = Question.objects.create(**validated_data)
        question.tags.set(tags)
        return question
    def get_likes(self, obj):
        return obj.likes_users.filter(is_like=True).count()
    def get_dislikes(self, obj):
        return obj.likes_users.filter(is_like=False).count()
     
    def get_is_liked(self, obj):
        user = self.context.get("request") and self.context.get("request").user
        if not user or user.is_anonymous:
            return False
        return obj.likes_users.filter(user=user, is_like=True).exists()

    def get_is_disliked(self, obj):
        user = self.context.get("request") and self.context.get("request").user
        if not user or user.is_anonymous:
            return False
        return obj.likes_users.filter(user=user, is_like=False).exists()
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request or not request.user or request.user.is_anonymous:
            return False
        return obj.bookmarked_by.filter(user=request.user).exists()
