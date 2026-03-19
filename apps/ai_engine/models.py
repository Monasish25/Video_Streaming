from django.db import models
from django.conf import settings
from apps.videos.models import Video


class UserInteraction(models.Model):
    """Track user interactions with videos for recommendations"""
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('comment', 'Comment'),
        ('share', 'Share'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    weight = models.FloatField(default=1.0)  # Different interactions have different weights
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'video']),
            models.Index(fields=['interaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.interaction_type} {self.video.title}"


class VideoFeatures(models.Model):
    """Store computed features for videos (for content-based filtering)"""
    video = models.OneToOneField(Video, on_delete=models.CASCADE, related_name='features')
    category_vector = models.JSONField(default=dict)  # Category encoding
    tag_vector = models.JSONField(default=dict)  # Tag encoding
    popularity_score = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Features for {self.video.title}"
