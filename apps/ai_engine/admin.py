from django.contrib import admin
from .models import UserInteraction, VideoFeatures


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'interaction_type', 'weight', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'video__title']
    readonly_fields = ['created_at']


@admin.register(VideoFeatures)
class VideoFeaturesAdmin(admin.ModelAdmin):
    list_display = ['video', 'popularity_score', 'engagement_score', 'updated_at']
    search_fields = ['video__title']
    readonly_fields = ['updated_at']
