"""
Video processing utilities using FFmpeg
Handles thumbnail generation and metadata extraction
"""
import subprocess
import os
from pathlib import Path


def generate_thumbnail(video_path, output_path=None, timestamp='00:00:01'):
    """
    Generate a thumbnail from a video file using FFmpeg
    
    Args:
        video_path: Path to the video file
        output_path: Path where thumbnail should be saved (optional)
        timestamp: Timestamp to capture thumbnail from (default: 1 second)
    
    Returns:
        Path to generated thumbnail or None if failed
    """
    try:
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return None
        
        # Generate output path if not provided
        if not output_path:
            video_dir = os.path.dirname(video_path)
            video_name = Path(video_path).stem
            thumbnails_dir = os.path.join(os.path.dirname(video_dir), 'thumbnails')
            os.makedirs(thumbnails_dir, exist_ok=True)
            output_path = os.path.join(thumbnails_dir, f"{video_name}_thumb.jpg")
        
        # FFmpeg command to extract thumbnail
        command = [
            'ffmpeg',
            '-i', video_path,
            '-ss', timestamp,
            '-vframes', '1',
            '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease',
            '-y',  # Overwrite output file
            output_path
        ]
        
        # Run FFmpeg
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"Thumbnail generated: {output_path}")
            return output_path
        else:
            print(f"FFmpeg error: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg to generate thumbnails.")
        print("Download from: https://ffmpeg.org/download.html")
        return None
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None


def get_video_metadata(video_path):
    """
    Extract video metadata using FFmpeg
    
    Args:
        video_path: Path to the video file
    
    Returns:
        Dictionary with metadata (duration, size, resolution) or None if failed
    """
    try:
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return None
        
        # FFprobe command to get video info
        command = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            
            # Extract relevant information
            metadata = {
                'duration': 0,
                'size': 0,
                'width': 0,
                'height': 0,
                'codec': '',
            }
            
            # Get duration and size from format
            if 'format' in data:
                metadata['duration'] = int(float(data['format'].get('duration', 0)))
                metadata['size'] = int(data['format'].get('size', 0))
            
            # Get video stream info
            if 'streams' in data:
                for stream in data['streams']:
                    if stream.get('codec_type') == 'video':
                        metadata['width'] = stream.get('width', 0)
                        metadata['height'] = stream.get('height', 0)
                        metadata['codec'] = stream.get('codec_name', '')
                        break
            
            return metadata
        else:
            print(f"FFprobe error: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("FFprobe not found. Please install FFmpeg.")
        return None
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None


def validate_video_format(file_path):
    """
    Validate if file is a supported video format
    
    Args:
        file_path: Path to the file
    
    Returns:
        Boolean indicating if file is valid
    """
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
    ext = Path(file_path).suffix.lower()
    return ext in valid_extensions


def get_video_duration_formatted(seconds):
    """
    Convert seconds to formatted duration string
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (HH:MM:SS or MM:SS)
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
