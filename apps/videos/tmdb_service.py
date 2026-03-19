"""
TMDB API Service
Provides methods to fetch movies, TV shows, and related content from The Movie Database API.
"""
import os
import requests
from django.conf import settings
from functools import lru_cache

class TMDBService:
    """Service class for interacting with TMDB API"""
    
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY', '')
        self.base_url = os.getenv('TMDB_BASE_URL', 'https://api.themoviedb.org/3')
        self.image_base_url = os.getenv('TMDB_IMAGE_BASE_URL', 'https://image.tmdb.org/t/p')
        
    def _make_request(self, endpoint, params=None):
        """Make a request to TMDB API"""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"TMDB API Error: {e}")
            return None
    
    def get_image_url(self, path, size='w500'):
        """Get full image URL from path"""
        if not path:
            return None
        return f"{self.image_base_url}/{size}{path}"
    
    def get_backdrop_url(self, path, size='original'):
        """Get backdrop image URL"""
        return self.get_image_url(path, size)
    
    # ==================== MOVIES ====================
    
    def get_trending_movies(self, time_window='day'):
        """Get trending movies (day or week)"""
        data = self._make_request(f'/trending/movie/{time_window}')
        return self._process_movies(data.get('results', [])) if data else []
    
    def get_popular_movies(self, page=1):
        """Get popular movies"""
        data = self._make_request('/movie/popular', {'page': page})
        return self._process_movies(data.get('results', [])) if data else []
    
    def get_top_rated_movies(self, page=1):
        """Get top rated movies"""
        data = self._make_request('/movie/top_rated', {'page': page})
        return self._process_movies(data.get('results', [])) if data else []
    
    def get_now_playing_movies(self, page=1):
        """Get now playing movies"""
        data = self._make_request('/movie/now_playing', {'page': page})
        return self._process_movies(data.get('results', [])) if data else []
    
    def get_upcoming_movies(self, page=1):
        """Get upcoming movies"""
        data = self._make_request('/movie/upcoming', {'page': page})
        return self._process_movies(data.get('results', [])) if data else []
    
    def get_movie_details(self, movie_id):
        """Get detailed info about a movie"""
        data = self._make_request(f'/movie/{movie_id}', {
            'append_to_response': 'videos,credits,similar,recommendations'
        })
        if data:
            return self._process_movie_details(data)
        return None
    
    def get_movies_by_genre(self, genre_id, page=1):
        """Get movies by genre ID"""
        data = self._make_request('/discover/movie', {
            'with_genres': genre_id,
            'page': page,
            'sort_by': 'popularity.desc'
        })
        return self._process_movies(data.get('results', [])) if data else []
    
    # ==================== TV SHOWS ====================
    
    def get_trending_tv(self, time_window='day'):
        """Get trending TV shows"""
        data = self._make_request(f'/trending/tv/{time_window}')
        return self._process_tv_shows(data.get('results', [])) if data else []
    
    def get_popular_tv(self, page=1):
        """Get popular TV shows"""
        data = self._make_request('/tv/popular', {'page': page})
        return self._process_tv_shows(data.get('results', [])) if data else []
    
    def get_top_rated_tv(self, page=1):
        """Get top rated TV shows"""
        data = self._make_request('/tv/top_rated', {'page': page})
        return self._process_tv_shows(data.get('results', [])) if data else []
    
    def get_tv_details(self, tv_id):
        """Get detailed info about a TV show"""
        data = self._make_request(f'/tv/{tv_id}', {
            'append_to_response': 'videos,credits,similar,recommendations'
        })
        if data:
            return self._process_tv_details(data)
        return None
    
    def get_tv_by_network(self, network_id, page=1):
        """Get TV shows by network (Netflix=213, Prime=1024, HBO=49, Disney+=2739, Apple TV+=2552)"""
        data = self._make_request('/discover/tv', {
            'with_networks': network_id,
            'page': page,
            'sort_by': 'popularity.desc'
        })
        return self._process_tv_shows(data.get('results', [])) if data else []
    
    # ==================== GENRES ====================
    
    def get_movie_genres(self):
        """Get list of movie genres"""
        data = self._make_request('/genre/movie/list')
        return data.get('genres', []) if data else []
    
    def get_tv_genres(self):
        """Get list of TV genres"""
        data = self._make_request('/genre/tv/list')
        return data.get('genres', []) if data else []
    
    # ==================== SEARCH ====================
    
    def search_multi(self, query, page=1):
        """Search for movies, TV shows, and people"""
        data = self._make_request('/search/multi', {'query': query, 'page': page})
        if data:
            results = []
            for item in data.get('results', []):
                if item.get('media_type') == 'movie':
                    results.append(self._process_single_movie(item))
                elif item.get('media_type') == 'tv':
                    results.append(self._process_single_tv(item))
            return results
        return []
    
    def search_movies(self, query, page=1):
        """Search for movies"""
        data = self._make_request('/search/movie', {'query': query, 'page': page})
        return self._process_movies(data.get('results', [])) if data else []
    
    def search_tv(self, query, page=1):
        """Search for TV shows"""
        data = self._make_request('/search/tv', {'query': query, 'page': page})
        return self._process_tv_shows(data.get('results', [])) if data else []
    
    # ==================== PROCESSING HELPERS ====================
    
    def _process_movies(self, movies):
        """Process list of movies"""
        return [self._process_single_movie(m) for m in movies if m.get('poster_path')]
    
    def _process_single_movie(self, movie):
        """Process single movie data"""
        return {
            'id': movie.get('id'),
            'title': movie.get('title', ''),
            'overview': movie.get('overview', '')[:200] + '...' if len(movie.get('overview', '')) > 200 else movie.get('overview', ''),
            'poster_url': self.get_image_url(movie.get('poster_path'), 'w342'),
            'backdrop_url': self.get_backdrop_url(movie.get('backdrop_path')),
            'release_date': movie.get('release_date', ''),
            'year': movie.get('release_date', '')[:4] if movie.get('release_date') else '',
            'vote_average': round(movie.get('vote_average', 0), 1),
            'vote_count': movie.get('vote_count', 0),
            'genre_ids': movie.get('genre_ids', []),
            'media_type': 'movie',
            'popularity': movie.get('popularity', 0),
        }
    
    def _process_movie_details(self, movie):
        """Process detailed movie data"""
        # Get trailer
        trailer = None
        videos = movie.get('videos', {}).get('results', [])
        for video in videos:
            if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                trailer = {
                    'key': video.get('key'),
                    'url': f"https://www.youtube.com/embed/{video.get('key')}",
                    'name': video.get('name')
                }
                break
        
        # Get cast
        cast = []
        for person in movie.get('credits', {}).get('cast', [])[:10]:
            cast.append({
                'id': person.get('id'),
                'name': person.get('name'),
                'character': person.get('character'),
                'profile_url': self.get_image_url(person.get('profile_path'), 'w185')
            })
        
        return {
            'id': movie.get('id'),
            'title': movie.get('title', ''),
            'tagline': movie.get('tagline', ''),
            'overview': movie.get('overview', ''),
            'poster_url': self.get_image_url(movie.get('poster_path'), 'w500'),
            'backdrop_url': self.get_backdrop_url(movie.get('backdrop_path')),
            'release_date': movie.get('release_date', ''),
            'year': movie.get('release_date', '')[:4] if movie.get('release_date') else '',
            'runtime': movie.get('runtime', 0),
            'vote_average': round(movie.get('vote_average', 0), 1),
            'vote_count': movie.get('vote_count', 0),
            'genres': [g.get('name') for g in movie.get('genres', [])],
            'trailer': trailer,
            'cast': cast,
            'similar': self._process_movies(movie.get('similar', {}).get('results', [])[:8]),
            'recommendations': self._process_movies(movie.get('recommendations', {}).get('results', [])[:8]),
            'media_type': 'movie',
            # Embed URL for streaming (using vidsrc)
            'embed_url': f"https://vidsrc.xyz/embed/movie/{movie.get('id')}",
        }
    
    def _process_tv_shows(self, shows):
        """Process list of TV shows"""
        return [self._process_single_tv(s) for s in shows if s.get('poster_path')]
    
    def _process_single_tv(self, show):
        """Process single TV show data"""
        return {
            'id': show.get('id'),
            'title': show.get('name', ''),
            'overview': show.get('overview', '')[:200] + '...' if len(show.get('overview', '')) > 200 else show.get('overview', ''),
            'poster_url': self.get_image_url(show.get('poster_path'), 'w342'),
            'backdrop_url': self.get_backdrop_url(show.get('backdrop_path')),
            'first_air_date': show.get('first_air_date', ''),
            'year': show.get('first_air_date', '')[:4] if show.get('first_air_date') else '',
            'vote_average': round(show.get('vote_average', 0), 1),
            'vote_count': show.get('vote_count', 0),
            'genre_ids': show.get('genre_ids', []),
            'media_type': 'tv',
            'popularity': show.get('popularity', 0),
        }
    
    def _process_tv_details(self, show):
        """Process detailed TV show data"""
        # Get trailer
        trailer = None
        videos = show.get('videos', {}).get('results', [])
        for video in videos:
            if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                trailer = {
                    'key': video.get('key'),
                    'url': f"https://www.youtube.com/embed/{video.get('key')}",
                    'name': video.get('name')
                }
                break
        
        # Get cast
        cast = []
        for person in show.get('credits', {}).get('cast', [])[:10]:
            cast.append({
                'id': person.get('id'),
                'name': person.get('name'),
                'character': person.get('character'),
                'profile_url': self.get_image_url(person.get('profile_path'), 'w185')
            })
        
        return {
            'id': show.get('id'),
            'title': show.get('name', ''),
            'tagline': show.get('tagline', ''),
            'overview': show.get('overview', ''),
            'poster_url': self.get_image_url(show.get('poster_path'), 'w500'),
            'backdrop_url': self.get_backdrop_url(show.get('backdrop_path')),
            'first_air_date': show.get('first_air_date', ''),
            'year': show.get('first_air_date', '')[:4] if show.get('first_air_date') else '',
            'number_of_seasons': show.get('number_of_seasons', 0),
            'number_of_episodes': show.get('number_of_episodes', 0),
            'episode_run_time': show.get('episode_run_time', [0])[0] if show.get('episode_run_time') else 0,
            'vote_average': round(show.get('vote_average', 0), 1),
            'vote_count': show.get('vote_count', 0),
            'genres': [g.get('name') for g in show.get('genres', [])],
            'trailer': trailer,
            'cast': cast,
            'similar': self._process_tv_shows(show.get('similar', {}).get('results', [])[:8]),
            'recommendations': self._process_tv_shows(show.get('recommendations', {}).get('results', [])[:8]),
            'media_type': 'tv',
            'status': show.get('status', ''),
            # Embed URL for streaming (using vidsrc)
            'embed_url': f"https://vidsrc.xyz/embed/tv/{show.get('id')}",
        }


# Singleton instance
tmdb_service = TMDBService()


# Network IDs for popular streaming platforms
NETWORK_IDS = {
    'netflix': 213,
    'prime': 1024,
    'hbo': 49,
    'disney': 2739,
    'apple': 2552,
    'paramount': 4330,
    'hulu': 453,
}

# Genre IDs for common genres
GENRE_IDS = {
    'action': 28,
    'adventure': 12,
    'animation': 16,
    'comedy': 35,
    'crime': 80,
    'documentary': 99,
    'drama': 18,
    'family': 10751,
    'fantasy': 14,
    'history': 36,
    'horror': 27,
    'music': 10402,
    'mystery': 9648,
    'romance': 10749,
    'science_fiction': 878,
    'thriller': 53,
    'war': 10752,
    'western': 37,
}
