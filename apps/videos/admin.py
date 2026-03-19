from django.contrib import admin
from .models import Video, Category, Comment, Like, View


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'views_count', 'likes_count', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['id', 'views_count', 'likes_count', 'dislikes_count', 'created_at', 'updated_at']
    list_per_page = 20


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'text_preview', 'likes_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'user__username', 'video__title']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'comment', 'like_type', 'created_at']
    list_filter = ['like_type', 'created_at']
    search_fields = ['user__username']


@admin.register(View)
class ViewAdmin(admin.ModelAdmin):
    list_display = ['video', 'user', 'ip_address', 'watch_time', 'created_at']
    list_filter = ['created_at']
    search_fields = ['video__title', 'user__username', 'ip_address']
