from rest_framework import serializers
from .models import Video, Category, Comment, Like, View
from apps.users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class VideoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    
    class Meta:
        model = Video
        fields = [
            'id', 'user', 'title', 'description', 'video_file', 'thumbnail',
            'category', 'status', 'views_count', 'likes_count', 'dislikes_count',
            'duration', 'duration_display', 'file_size', 'created_at', 'updated_at'
        ]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'parent', 'likes_count', 'created_at', 'replies']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'video', 'comment', 'like_type', 'created_at']


class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = ['id', 'video', 'user', 'watch_time', 'created_at']
