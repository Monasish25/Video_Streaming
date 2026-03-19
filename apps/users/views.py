from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from .models import CustomUser, UserProfile, Subscription
from apps.videos.models import Video


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('videos:home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('videos:home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('videos:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'videos:home')
                return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('videos:home')


@login_required
def profile_view(request):
    """User profile edit view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'users/profile.html', {'form': form})


def channel_view(request, slug):
    """Public channel view"""
    profile = get_object_or_404(UserProfile, slug=slug)
    videos = Video.objects.filter(user=profile.user, status='published').order_by('-created_at')
    
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user,
            channel=profile.user
        ).exists()
    
    context = {
        'profile': profile,
        'videos': videos,
        'is_subscribed': is_subscribed,
    }
    return render(request, 'users/channel.html', context)


@login_required
def subscribe_toggle(request, user_id):
    """Toggle subscription to a channel (AJAX)"""
    if request.method == 'POST':
        channel = get_object_or_404(CustomUser, id=user_id)
        
        if channel == request.user:
            return JsonResponse({'error': 'Cannot subscribe to yourself'}, status=400)
        
        subscription = Subscription.objects.filter(
            subscriber=request.user,
            channel=channel
        )
        
        if subscription.exists():
            subscription.delete()
            channel.profile.subscribers_count -= 1
            channel.profile.save()
            subscribed = False
        else:
            Subscription.objects.create(
                subscriber=request.user,
                channel=channel
            )
            channel.profile.subscribers_count += 1
            channel.profile.save()
            subscribed = True
        
        return JsonResponse({
            'subscribed': subscribed,
            'subscribers_count': channel.profile.subscribers_count
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
