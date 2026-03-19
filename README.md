# 🎥 VideoStream - Video Streaming Platform

A modern, feature-rich video streaming platform built with Django, similar to YouTube. Features include video upload/streaming, user authentication, AI-powered recommendations, comments, likes, and subscriptions.

## ✨ Features

- **User Authentication**: Register, login, and manage user profiles
- **Video Upload & Streaming**: Upload videos with automatic thumbnail generation
- **AI-Powered Recommendations**: Personalized video recommendations using collaborative and content-based filtering
- **Social Features**: Comments, likes/dislikes, subscriptions
- **Search & Discovery**: Search videos by title, description, or creator
- **Category Filtering**: Browse videos by category
- **Responsive Design**: Modern dark theme that works on all devices
- **Admin Panel**: Comprehensive Django admin for content management

## 🛠️ Technologies Used

- **Backend**: Django 5.0, Django REST Framework
- **Database**: SQLite (development), PostgreSQL-ready (production)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Media Processing**: FFmpeg for video thumbnails and metadata
- **AI/ML**: NumPy, Pandas, Scikit-learn for recommendations

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10 or higher
- pip (Python package manager)
- FFmpeg (for video processing)

### Installing FFmpeg

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and add to PATH
3. Verify: `ffmpeg -version`

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
cd "c:\Users\monas\OneDrive\Desktop\Projects\Video streaming\video_platform"
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

Edit `.env` and set your configuration:

```env
SECRET_KEY=your-secret-key-here-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generate a secure SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Database Setup

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### 6. Create Initial Categories (Optional)

```bash
python manage.py shell
```

Then in the Python shell:
```python
from apps.videos.models import Category

categories = ['Music', 'Gaming', 'Education', 'Entertainment', 'Sports', 'Technology', 'News']
for cat in categories:
    Category.objects.get_or_create(name=cat)
exit()
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## 📁 Project Structure

```
video_platform/
├── apps/
│   ├── users/          # User authentication & profiles
│   ├── videos/         # Video upload, streaming, comments
│   └── ai_engine/      # AI recommendations
├── config/             # Django settings & URLs
├── media/              # User-uploaded files
├── static/             # CSS, JavaScript, images
│   ├── css/
│   └── js/
├── templates/          # HTML templates
│   ├── base.html
│   ├── users/
│   └── videos/
├── scripts/            # Utility scripts
├── manage.py
└── requirements.txt
```

## 🎯 Usage

### For Users

1. **Register**: Create an account at `/users/register/`
2. **Upload Video**: Click "Upload" button (requires login)
3. **Watch Videos**: Browse homepage or search for videos
4. **Interact**: Like, comment, and subscribe to channels
5. **Manage Profile**: Edit your profile and channel settings

### For Administrators

1. Access admin panel: **http://127.0.0.1:8000/admin/**
2. Manage users, videos, categories, and comments
3. Monitor user interactions and recommendations

## 🔧 Configuration

### Database (Production)

To use PostgreSQL in production, update `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/video_platform
```

And uncomment the PostgreSQL configuration in `config/settings.py`.

### File Upload Limits

Current limits (can be changed in `config/settings.py`):
- Max video size: 500 MB
- Allowed formats: MP4, AVI, MOV, MKV, WEBM

### Security Settings

For production deployment:
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Enable HTTPS and security middleware
- Use a strong `SECRET_KEY`

## 🤖 AI Recommendations

The platform uses a hybrid recommendation system:

1. **Collaborative Filtering**: Recommends videos based on similar users' preferences
2. **Content-Based Filtering**: Recommends videos from categories you like
3. **Trending Algorithm**: Shows popular videos to new/anonymous users

## 🐛 Troubleshooting

### FFmpeg Not Found

If thumbnail generation fails:
- Ensure FFmpeg is installed and in PATH
- Restart your terminal/IDE after installation
- Test: `ffmpeg -version`

### Database Errors

```bash
# Reset database (WARNING: Deletes all data)
python manage.py flush
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading

```bash
python manage.py collectstatic
```

## 📝 API Endpoints

The platform includes REST API endpoints:

- `GET /api/ai/recommendations/` - Get personalized recommendations
- `GET /api/ai/trending/` - Get trending videos
- `GET /api/ai/similar/<video_id>/` - Get similar videos

## 🚀 Deployment

### Collect Static Files

```bash
python manage.py collectstatic
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure production database (PostgreSQL)
- [ ] Set up proper `ALLOWED_HOSTS`
- [ ] Configure static/media file serving (AWS S3, CDN)
- [ ] Set up HTTPS
- [ ] Configure email backend
- [ ] Set up logging
- [ ] Use environment variables for secrets

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

## 📄 License

This project is for educational purposes.

## 👨‍💻 Author

Built with ❤️ using Django

## 🙏 Acknowledgments

- Django framework
- FFmpeg for video processing
- Modern web design inspiration from YouTube
