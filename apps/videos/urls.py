from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    path('browse/', views.browse_view, name='browse'),
    
    # TMDB Movie/TV detail pages
    path('movie/<int:movie_id>/', views.movie_detail_view, name='movie_detail'),
    path('tv/<int:tv_id>/', views.tv_detail_view, name='tv_detail'),
    
    # User uploaded videos
    path('watch/<uuid:video_id>/', views.watch_view, name='watch'),
    path('stream/<uuid:video_id>/', views.serve_video, name='serve_video'),
    path('upload/', views.upload_view, name='upload'),
    path('edit/<uuid:video_id>/', views.video_edit_view, name='edit'),
    path('delete/<uuid:video_id>/', views.video_delete_view, name='delete'),
    path('search/', views.search_view, name='search'),
    
    # AJAX endpoints for TMDB content
    path('api/search/', views.api_search_view, name='api_search'),
    path('api/genre/<int:genre_id>/', views.api_genre_content, name='api_genre'),
    path('api/network/<int:network_id>/', views.api_network_content, name='api_network'),
    
    # Comment/Like AJAX endpoints
    path('comment/add/<uuid:video_id>/', views.add_comment, name='add_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('like/<uuid:video_id>/', views.like_video, name='like_video'),
    path('like/comment/<int:comment_id>/', views.like_comment, name='like_comment'),
]

