from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.videos.serializers import VideoSerializer
from .recommendation import RecommendationEngine
from apps.videos.models import Video


@login_required
def get_recommendations(request):
    """API endpoint to get personalized recommendations"""
    limit = int(request.GET.get('limit', 10))
    
    engine = RecommendationEngine(user=request.user)
    recommendations = engine.get_recommendations(limit=limit)
    
    serializer = VideoSerializer(recommendations, many=True)
    return JsonResponse({
        'recommendations': serializer.data
    })


def get_trending(request):
    """API endpoint to get trending videos"""
    limit = int(request.GET.get('limit', 10))
    
    engine = RecommendationEngine()
    trending = engine.get_trending_videos(limit=limit)
    
    serializer = VideoSerializer(trending, many=True)
    return JsonResponse({
        'trending': serializer.data
    })


def get_similar(request, video_id):
    """API endpoint to get similar videos"""
    limit = int(request.GET.get('limit', 10))
    
    try:
        video = Video.objects.get(id=video_id)
        engine = RecommendationEngine()
        similar = engine.get_similar_videos(video, limit=limit)
        
        serializer = VideoSerializer(similar, many=True)
        return JsonResponse({
            'similar': serializer.data
        })
    except Video.DoesNotExist:
        return JsonResponse({'error': 'Video not found'}, status=404)
