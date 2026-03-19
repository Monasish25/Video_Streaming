from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
import uuid


class CustomUser(AbstractUser):
    """Custom user model with email authentication"""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """Extended user profile with additional information"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    channel_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    subscribers_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.channel_name or self.user.username)
            slug = base_slug
            counter = 1
            while UserProfile.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class Subscription(models.Model):
    """User subscription model"""
    subscriber = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
    )
    channel = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='subscribers'
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('subscriber', 'channel')
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.subscriber.username} -> {self.channel.username}"
