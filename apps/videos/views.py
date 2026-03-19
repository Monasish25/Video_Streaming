from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse, FileResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Video, Comment, Like, View, Category
from .forms import VideoUploadForm, CommentForm
from .tmdb_service import tmdb_service, NETWORK_IDS, GENRE_IDS
import os
import mimetypes
import random


def home_view(request):
    """Homepage with TMDB movies and TV shows in Cineby style"""
    
    # Get trending movies for hero section (pick random featured movie)
    trending_movies = tmdb_service.get_trending_movies('day')
    featured_movie = trending_movies[0] if trending_movies else None
    
    # Get more data if we have a featured movie
    if featured_movie:
        featured_details = tmdb_service.get_movie_details(featured_movie['id'])
        if featured_details:
            featured_movie = featured_details
    
    # Top 10 content (mix of trending movies)
    top_10_movies = trending_movies[:10] if trending_movies else []
    
    # Trending today (movies and series)
    trending_tv = tmdb_service.get_trending_tv('day')
    
    # Series by network (Netflix)
    netflix_series = tmdb_service.get_tv_by_network(NETWORK_IDS['netflix'])
    
    # Top rated movies
    top_rated_movies = tmdb_service.get_top_rated_movies()
    
    # Top rated TV
    top_rated_tv = tmdb_service.get_top_rated_tv()
    
    # Movies by genre (Comedy for default)
    comedy_movies = tmdb_service.get_movies_by_genre(GENRE_IDS['comedy'])
    action_movies = tmdb_service.get_movies_by_genre(GENRE_IDS['action'])
    
    # Get all genres for filtering
    movie_genres = tmdb_service.get_movie_genres()
    
    # Also get user-uploaded videos (keep existing functionality)
    user_videos = Video.objects.filter(status='published').select_related('user__profile', 'category')[:12]
    categories = Category.objects.all()
    
    context = {
        # TMDB Content
        'featured_movie': featured_movie,
        'top_10_movies': top_10_movies,
        'trending_movies': trending_movies[:12] if trending_movies else [],
        'trending_tv': trending_tv[:12] if trending_tv else [],
        'netflix_series': netflix_series[:12] if netflix_series else [],
        'top_rated_movies': top_rated_movies[:12] if top_rated_movies else [],
        'top_rated_tv': top_rated_tv[:12] if top_rated_tv else [],
        'comedy_movies': comedy_movies[:12] if comedy_movies else [],
        'action_movies': action_movies[:12] if action_movies else [],
        'movie_genres': movie_genres,
        
        # User uploaded videos (existing)
        'videos': user_videos,
        'categories': categories,
    }
    return render(request, 'videos/home.html', context)


def movie_detail_view(request, movie_id):
    """Movie detail page with trailer and streaming embed"""
    movie = tmdb_service.get_movie_details(movie_id)
    
    if not movie:
        messages.error(request, 'Movie not found.')
        return redirect('videos:home')
    
    context = {
        'movie': movie,
        'media_type': 'movie',
    }
    return render(request, 'videos/movie_detail.html', context)


def tv_detail_view(request, tv_id):
    """TV show detail page with trailer and streaming embed"""
    show = tmdb_service.get_tv_details(tv_id)
    
    if not show:
        messages.error(request, 'TV show not found.')
        return redirect('videos:home')
    
    context = {
        'movie': show,  # Using 'movie' for template consistency
        'media_type': 'tv',
    }
    return render(request, 'videos/movie_detail.html', context)


def browse_view(request):
    """Browse movies and TV shows by genre/category"""
    media_type = request.GET.get('type', 'movie')  # 'movie' or 'tv'
    genre_id = request.GET.get('genre')
    network_id = request.GET.get('network')
    page = int(request.GET.get('page', 1))
    
    content = []
    title = "Browse"
    
    if genre_id:
        content = tmdb_service.get_movies_by_genre(genre_id, page)
        # Find genre name
        genres = tmdb_service.get_movie_genres()
        for g in genres:
            if str(g['id']) == genre_id:
                title = f"{g['name']} Movies"
                break
    elif network_id:
        content = tmdb_service.get_tv_by_network(network_id, page)
        # Find network name
        network_names = {v: k.title() for k, v in NETWORK_IDS.items()}
        title = f"Series on {network_names.get(int(network_id), 'Streaming')}"
    elif media_type == 'tv':
        content = tmdb_service.get_popular_tv(page)
        title = "Popular TV Shows"
    else:
        content = tmdb_service.get_popular_movies(page)
        title = "Popular Movies"
    
    movie_genres = tmdb_service.get_movie_genres()
    
    context = {
        'content': content,
        'title': title,
        'media_type': media_type,
        'movie_genres': movie_genres,
        'network_ids': NETWORK_IDS,
        'current_page': page,
    }
    return render(request, 'videos/browse.html', context)


def api_search_view(request):
    """AJAX search endpoint for TMDB content"""
    query = request.GET.get('q', '')
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    results = tmdb_service.search_multi(query)
    
    return JsonResponse({
        'results': results[:10],
        'query': query,
    })


def api_genre_content(request, genre_id):
    """AJAX endpoint to get movies by genre"""
    movies = tmdb_service.get_movies_by_genre(genre_id)
    return JsonResponse({'movies': movies[:12]})


def api_network_content(request, network_id):
    """AJAX endpoint to get TV shows by network"""
    shows = tmdb_service.get_tv_by_network(network_id)
    return JsonResponse({'shows': shows[:12]})




def watch_view(request, video_id):
    """Video watch page"""
    video = get_object_or_404(
        Video.objects.select_related('user__profile', 'category'),
        id=video_id
    )
    
    # Check if user can view the video
    if video.status != 'published':
        if not request.user.is_authenticated or video.user != request.user:
            messages.error(request, 'This video is not available.')
            return redirect('videos:home')
    
    # Track view
    ip_address = request.META.get('REMOTE_ADDR')
    View.objects.create(
        video=video,
        user=request.user if request.user.is_authenticated else None,
        ip_address=ip_address
    )
    video.views_count += 1
    video.save()
    
    # Get comments
    comments = video.comments.filter(parent=None).select_related('user__profile').prefetch_related('replies')
    
    # Check if user liked/disliked
    user_like = None
    if request.user.is_authenticated:
        try:
            user_like = Like.objects.get(user=request.user, video=video)
        except Like.DoesNotExist:
            pass
    
    # Check if user is subscribed to the video owner
    is_subscribed = False
    if request.user.is_authenticated and request.user != video.user:
        from apps.users.models import Subscription
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user,
            channel=video.user
        ).exists()
    
    # Get recommended videos (same category, or random if no category)
    recommended_query = Video.objects.filter(
        status='published'
    ).exclude(id=video.id).select_related('user__profile')
    
    if video.category:
        recommended_query = recommended_query.filter(category=video.category)
    
    recommended = recommended_query[:10]
    
    context = {
        'video': video,
        'comments': comments,
        'comment_form': CommentForm(),
        'user_like': user_like,
        'recommended': recommended,
        'is_subscribed': is_subscribed,
    }
    return render(request, 'videos/watch.html', context)


@login_required
def upload_view(request):
    """Video upload page"""
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            messages.success(request, 'Video uploaded successfully!')
            return redirect('videos:watch', video_id=video.id)
    else:
        form = VideoUploadForm()
    
    return render(request, 'videos/upload.html', {'form': form})


@login_required
def video_edit_view(request, video_id):
    """Edit video details"""
    video = get_object_or_404(Video, id=video_id, user=request.user)
    
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video updated successfully!')
            return redirect('videos:watch', video_id=video.id)
    else:
        form = VideoUploadForm(instance=video)
    
    return render(request, 'videos/edit.html', {'form': form, 'video': video})


@login_required
def video_delete_view(request, video_id):
    """Delete video"""
    video = get_object_or_404(Video, id=video_id, user=request.user)
    
    if request.method == 'POST':
        video.delete()
        messages.success(request, 'Video deleted successfully!')
        return redirect('videos:home')
    
    return render(request, 'videos/delete_confirm.html', {'video': video})


@login_required
def add_comment(request, video_id):
    """Add comment to video (AJAX)"""
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.video = video
            comment.user = request.user
            
            # Check for parent comment (reply)
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
            
            comment.save()
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'text': comment.text,
                    'user': comment.user.username,
                    'avatar': comment.user.profile.avatar.url if comment.user.profile.avatar else None,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                }
            })
        
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def delete_comment(request, comment_id):
    """Delete comment (AJAX)"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Check if user owns the comment or the video
        if comment.user == request.user or comment.video.user == request.user:
            comment.delete()
            return JsonResponse({'success': True})
        
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def like_video(request, video_id):
    """Like/dislike video (AJAX)"""
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id)
        like_type = request.POST.get('type', 'like')  # 'like' or 'dislike'
        
        # Check if user already liked/disliked
        existing_like = Like.objects.filter(user=request.user, video=video).first()
        
        if existing_like:
            if existing_like.like_type == like_type:
                # Remove like/dislike
                existing_like.delete()
                action = 'removed'
            else:
                # Change like to dislike or vice versa
                existing_like.like_type = like_type
                existing_like.save()
                action = 'changed'
        else:
            # Create new like/dislike
            Like.objects.create(user=request.user, video=video, like_type=like_type)
            action = 'added'
        
        # Get updated counts
        video.refresh_from_db()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'likes_count': video.likes_count,
            'dislikes_count': video.dislikes_count,
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def like_comment(request, comment_id):
    """Like comment (AJAX)"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Check if user already liked
        existing_like = Like.objects.filter(user=request.user, comment=comment).first()
        
        if existing_like:
            existing_like.delete()
            action = 'removed'
        else:
            Like.objects.create(user=request.user, comment=comment, like_type='like')
            action = 'added'
        
        # Get updated count
        comment.refresh_from_db()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'likes_count': comment.likes_count,
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def search_view(request):
    """Search results page"""
    search_query = request.GET.get('q', '')
    
    videos = Video.objects.filter(
        status='published'
    ).select_related('user__profile', 'category')
    
    if search_query:
        videos = videos.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(videos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'videos': page_obj,
        'search_query': search_query,
    }
    return render(request, 'videos/search.html', context)


def serve_video(request, video_id):
    """Serve video file with HTTP Range Request support for seeking"""
    video = get_object_or_404(Video, id=video_id)
    
    # Check if user can view the video
    if video.status != 'published':
        if not request.user.is_authenticated or video.user != request.user:
            return HttpResponse('Video not available', status=403)
    
    video_path = video.video_file.path
    
    if not os.path.exists(video_path):
        return HttpResponse('Video file not found', status=404)
    
    # Get file size and content type
    file_size = os.path.getsize(video_path)
    content_type, _ = mimetypes.guess_type(video_path)
    content_type = content_type or 'video/mp4'
    
    # Get Range header
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = None
    
    if range_header:
        import re
        range_match = re.search(r'bytes=(\d+)-(\d*)', range_header)
    
    # Handle Range Request
    if range_match:
        start = int(range_match.group(1))
        end = range_match.group(2)
        end = int(end) if end else file_size - 1
        
        # Ensure valid range
        if start >= file_size or end >= file_size or start > end:
            return HttpResponse('Invalid range', status=416)
        
        length = end - start + 1
        
        # Open file and seek to start position
        with open(video_path, 'rb') as video_file:
            video_file.seek(start)
            data = video_file.read(length)
        
        response = HttpResponse(data, status=206, content_type=content_type)
        response['Content-Length'] = str(length)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        
        return response
    
    # Serve full file if no Range header
    response = FileResponse(open(video_path, 'rb'), content_type=content_type)
    response['Content-Length'] = str(file_size)
    response['Accept-Ranges'] = 'bytes'
    
    return response
