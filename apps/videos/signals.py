from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video, Like
from scripts.video_processor import generate_thumbnail, get_video_metadata
import os
import logging

logger = logging.getLogger(__name__)
from .tasks import process_video_task

@receiver(post_save, sender=Video)
def process_video(sender, instance, created, **kwargs):
    """Queue video for processing after upload"""
    if created and instance.video_file:
        try:
            # Trigger celery task asynchronously
            process_video_task.delay(str(instance.id))
            logger.info(f"Queued celery task to process video {instance.id}")
        except Exception as e:
            logger.error(f"Failed to queue celery task for video {instance.id}: {e}", exc_info=True)


@receiver(post_save, sender=Like)
def update_like_counts(sender, instance, created, **kwargs):
    """Update like/dislike counts when a like is created or updated"""
    if instance.video:
        video = instance.video
        likes_count = Like.objects.filter(video=video, like_type='like').count()
        dislikes_count = Like.objects.filter(video=video, like_type='dislike').count()
        # Use update to avoid triggering signals
        Video.objects.filter(pk=video.pk).update(
            likes_count=likes_count,
            dislikes_count=dislikes_count
        )
    elif instance.comment:
        comment = instance.comment
        likes_count = Like.objects.filter(comment=comment, like_type='like').count()
        # Use update to avoid triggering signals
        from .models import Comment
        Comment.objects.filter(pk=comment.pk).update(likes_count=likes_count)


@receiver(post_delete, sender=Like)
def update_like_counts_on_delete(sender, instance, **kwargs):
    """Update like/dislike counts when a like is deleted"""
    if instance.video:
        video = instance.video
        likes_count = Like.objects.filter(video=video, like_type='like').count()
        dislikes_count = Like.objects.filter(video=video, like_type='dislike').count()
        # Use update to avoid triggering signals
        Video.objects.filter(pk=video.pk).update(
            likes_count=likes_count,
            dislikes_count=dislikes_count
        )
    elif instance.comment:
        comment = instance.comment
        likes_count = Like.objects.filter(comment=comment, like_type='like').count()
        # Use update to avoid triggering signals
        from .models import Comment
        Comment.objects.filter(pk=comment.pk).update(likes_count=likes_count)
