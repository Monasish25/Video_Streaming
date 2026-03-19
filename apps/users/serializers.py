from rest_framework import serializers
from .models import CustomUser, UserProfile, Subscription


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['channel_name', 'bio', 'avatar', 'subscribers_count', 'slug']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile']


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = UserSerializer(read_only=True)
    channel = UserSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'subscriber', 'channel', 'subscribed_at']
