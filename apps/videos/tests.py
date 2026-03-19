from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Category, Video, Comment, Like, View
from unittest.mock import patch

User = get_user_model()

@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_STORE_EAGERS=True)
class VideoModelTest(TestCase):
    def setUp(self):
        # Prevent actual celery task execution for video processing during test
        patcher = patch('apps.videos.signals.process_video_task.delay')
        self.mock_delay = patcher.start()
        self.addCleanup(patcher.stop)

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        # Create a dummy video file
        mock_video_content = b"fake_video_content"
        self.video_file = SimpleUploadedFile("test_video.mp4", mock_video_content, content_type="video/mp4")

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertEqual(str(self.category), 'Test Category')

    def test_video_creation(self):
        video = Video.objects.create(
            user=self.user,
            title='Test Video',
            description='This is a test video',
            category=self.category,
            video_file=self.video_file,
            status='public'
        )
        self.assertEqual(video.title, 'Test Video')
        self.assertEqual(video.user.username, 'testuser')
        self.assertEqual(video.category.name, 'Test Category')
        self.assertEqual(video.status, 'public')
        self.assertEqual(str(video), 'Test Video')

    def test_comment_creation(self):
        video = Video.objects.create(
            user=self.user,
            title='Test Video',
            video_file=self.video_file,
            category=self.category
        )
        comment = Comment.objects.create(
            video=video,
            user=self.user,
            text='Nice video!'
        )
        self.assertEqual(comment.text, 'Nice video!')
        self.assertEqual(comment.video, video)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(str(comment), f"{self.user.username} on {video.title}")

    def test_like_creation(self):
        video = Video.objects.create(
            user=self.user,
            title='Test Video',
            video_file=self.video_file,
            category=self.category
        )
        like = Like.objects.create(
            video=video,
            user=self.user,
            like_type='like'
        )
        self.assertEqual(like.like_type, 'like')
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.video, video)

    def test_view_creation(self):
        video = Video.objects.create(
            user=self.user,
            title='Test Video',
            video_file=self.video_file,
            category=self.category
        )
        view = View.objects.create(
            video=video,
            user=self.user,
            watch_time=10
        )
        self.assertEqual(view.watch_time, 10)
        self.assertEqual(view.user, self.user)
        self.assertEqual(view.video, video)
