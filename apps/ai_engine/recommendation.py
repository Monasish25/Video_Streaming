"""
AI-powered recommendation engine for video platform
Uses content-based and collaborative filtering
"""
from django.db.models import Count, Q, F
from apps.videos.models import Video, Like, View
from .models import UserInteraction
import numpy as np
from collections import defaultdict


class RecommendationEngine:
    """Main recommendation engine class"""
    
    def __init__(self, user=None):
        self.user = user
    
    def get_recommendations(self, limit=10):
        """Get personalized recommendations for user"""
        if self.user and self.user.is_authenticated:
            # Combine collaborative and content-based filtering
            collab_recs = self.collaborative_filtering(limit=limit*2)
            content_recs = self.content_based_filtering(limit=limit*2)
            
            # Merge and deduplicate
            recommendations = self._merge_recommendations(collab_recs, content_recs, limit)
        else:
            # For anonymous users, show trending videos
            recommendations = self.get_trending_videos(limit)
        
        return recommendations
    
    def collaborative_filtering(self, limit=10):
        """Collaborative filtering based on user interactions"""
        if not self.user or not self.user.is_authenticated:
            return []
        
        # Get videos the user has interacted with
        user_videos = View.objects.filter(user=self.user).values_list('video_id', flat=True)
        user_liked = Like.objects.filter(user=self.user, like_type='like').values_list('video_id', flat=True)
        
        # Find similar users (users who liked the same videos)
        similar_users = Like.objects.filter(
            video_id__in=user_liked,
            like_type='like'
        ).exclude(user=self.user).values('user').annotate(
            common_likes=Count('video')
        ).order_by('-common_likes')[:20]
        
        similar_user_ids = [u['user'] for u in similar_users]
        
        # Get videos liked by similar users that current user hasn't seen
        recommended_videos = Video.objects.filter(
            likes__user_id__in=similar_user_ids,
            likes__like_type='like',
            status='published'
        ).exclude(
            id__in=user_videos
        ).annotate(
            recommendation_score=Count('likes')
        ).order_by('-recommendation_score')[:limit]
        
        return list(recommended_videos)
    
    def content_based_filtering(self, limit=10):
        """Content-based filtering based on video attributes"""
        if not self.user or not self.user.is_authenticated:
            return []
        
        # Get user's liked videos
        liked_videos = Video.objects.filter(
            likes__user=self.user,
            likes__like_type='like'
        )
        
        if not liked_videos.exists():
            return []
        
        # Get categories user likes
        liked_categories = liked_videos.values_list('category', flat=True).distinct()
        
        # Get videos the user has already seen
        seen_videos = View.objects.filter(user=self.user).values_list('video_id', flat=True)
        
        # Recommend videos from same categories
        recommended_videos = Video.objects.filter(
            category__in=liked_categories,
            status='published'
        ).exclude(
            id__in=seen_videos
        ).order_by('-views_count', '-likes_count')[:limit]
        
        return list(recommended_videos)
    
    def get_trending_videos(self, limit=10):
        """Get trending videos (for anonymous users or fallback)"""
        # Calculate trending score based on recent views and likes
        trending = Video.objects.filter(
            status='published'
        ).annotate(
            trending_score=F('views_count') + (F('likes_count') * 2)
        ).order_by('-trending_score', '-created_at')[:limit]
        
        return list(trending)
    
    def get_similar_videos(self, video, limit=10):
        """Get videos similar to a given video"""
        # Get videos from same category
        similar = Video.objects.filter(
            category=video.category,
            status='published'
        ).exclude(id=video.id).order_by('-views_count')[:limit]
        
        # If not enough, add popular videos
        if similar.count() < limit:
            additional = Video.objects.filter(
                status='published'
            ).exclude(
                Q(id=video.id) | Q(id__in=similar)
            ).order_by('-views_count')[:limit - similar.count()]
            
            similar = list(similar) + list(additional)
        
        return similar
    
    def _merge_recommendations(self, list1, list2, limit):
        """Merge two recommendation lists and remove duplicates"""
        seen_ids = set()
        merged = []
        
        # Interleave results from both lists
        for i in range(max(len(list1), len(list2))):
            if i < len(list1) and list1[i].id not in seen_ids:
                merged.append(list1[i])
                seen_ids.add(list1[i].id)
            
            if i < len(list2) and list2[i].id not in seen_ids:
                merged.append(list2[i])
                seen_ids.add(list2[i].id)
            
            if len(merged) >= limit:
                break
        
        return merged[:limit]


def track_interaction(user, video, interaction_type):
    """Helper function to track user interactions"""
    if not user.is_authenticated:
        return
    
    # Define weights for different interactions
    weights = {
        'view': 1.0,
        'like': 3.0,
        'dislike': -2.0,
        'comment': 2.0,
        'share': 4.0,
    }
    
    UserInteraction.objects.create(
        user=user,
        video=video,
        interaction_type=interaction_type,
        weight=weights.get(interaction_type, 1.0)
    )
