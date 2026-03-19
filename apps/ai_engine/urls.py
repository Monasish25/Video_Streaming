from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('trending/', views.get_trending, name='trending'),
    path('similar/<uuid:video_id>/', views.get_similar, name='similar'),
]
