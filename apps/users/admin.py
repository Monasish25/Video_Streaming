from django.contrib import admin
from .models import CustomUser, UserProfile, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff', 'date_joined']
    search_fields = ['username', 'email']
    list_filter = ['is_staff', 'is_active', 'date_joined']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel_name', 'subscribers_count', 'created_at']
    search_fields = ['user__username', 'channel_name']
    list_filter = ['created_at']
    readonly_fields = ['slug', 'created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'channel', 'subscribed_at']
    search_fields = ['subscriber__username', 'channel__username']
    list_filter = ['subscribed_at']
