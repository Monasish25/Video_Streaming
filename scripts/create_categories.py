# Create initial video categories
from apps.videos.models import Category

categories = [
    'Music',
    'Gaming',
    'Education',
    'Entertainment',
    'Sports',
    'Technology',
    'News',
    'Comedy',
    'Film & Animation',
    'Science & Tech'
]

for cat_name in categories:
    Category.objects.get_or_create(name=cat_name)
    print(f"Created category: {cat_name}")

print(f"\nTotal categories: {Category.objects.count()}")
