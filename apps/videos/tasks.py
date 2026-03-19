import os
import logging
from celery import shared_task
from django.conf import settings
from .models import Video
from scripts.video_processor import generate_thumbnail, get_video_metadata

logger = logging.getLogger(__name__)

@shared_task
def process_video_task(video_id):
    """Process video via Celery task: generate thumbnail and extract metadata."""
    try:
        video = Video.objects.get(id=video_id)
        if not video.video_file:
            return "No video file"
            
        updated_fields = {}
        
        # Generate thumbnail if not exists
        if not video.thumbnail:
            thumbnail_abs_path = generate_thumbnail(video.video_file.path)
            if thumbnail_abs_path:
                media_root = str(settings.MEDIA_ROOT)
                if thumbnail_abs_path.startswith(media_root):
                    # Get relative path from MEDIA_ROOT
                    thumbnail_rel_path = os.path.relpath(thumbnail_abs_path, media_root)
                    # For windows safety replace backslashes (though Django handles it, standard is forward)
                    thumbnail_rel_path = thumbnail_rel_path.replace('\\', '/')
                    video.thumbnail = thumbnail_rel_path
                    updated_fields['thumbnail'] = thumbnail_rel_path
                    logger.info(f"Auto-generated thumbnail for video {video.id}: {thumbnail_rel_path}")
                else:
                    logger.warning(f"Thumbnail path not in MEDIA_ROOT: {thumbnail_abs_path}")
        
        # Extract video metadata
        metadata = get_video_metadata(video.video_file.path)
        if metadata:
            video.duration = metadata.get('duration', 0)
            video.file_size = metadata.get('size', 0)
            updated_fields['duration'] = video.duration
            updated_fields['file_size'] = video.file_size
            
        if updated_fields:
            # Use update to avoid triggering post_save signals again
            Video.objects.filter(pk=video.pk).update(**updated_fields)
            
        return f"Successfully processed video {video.id}"
    except Video.DoesNotExist:
        logger.error(f"Video {video_id} does not exist.")
        return f"Failed: video {video_id} missing"
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}", exc_info=True)
        return f"Failed: exception occurred for {video_id}"
