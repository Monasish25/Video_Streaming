/**
 * CINEBY - Main JavaScript
 * Handles carousels, search, user menu, and other interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    initCarousels();
    initSearchModal();
    initUserMenu();
    initAlerts();
    initAIRecommendations();
});

// ===== Carousel Navigation =====
function initCarousels() {
    const carousels = document.querySelectorAll('.carousel');

    carousels.forEach(carousel => {
        const track = carousel.querySelector('.carousel-track');
        const prevBtn = carousel.querySelector('.carousel-btn.prev');
        const nextBtn = carousel.querySelector('.carousel-btn.next');

        if (!track) return;

        const scrollAmount = 400;

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                track.scrollBy({
                    left: -scrollAmount,
                    behavior: 'smooth'
                });
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                track.scrollBy({
                    left: scrollAmount,
                    behavior: 'smooth'
                });
            });
        }

        // Update button visibility based on scroll position
        const updateButtons = () => {
            if (prevBtn) {
                prevBtn.style.opacity = track.scrollLeft > 0 ? '1' : '0';
            }
            if (nextBtn) {
                const maxScroll = track.scrollWidth - track.clientWidth;
                nextBtn.style.opacity = track.scrollLeft < maxScroll - 10 ? '1' : '0';
            }
        };

        track.addEventListener('scroll', updateButtons);
        updateButtons();
    });
}

// ===== Search Modal =====
function initSearchModal() {
    const searchToggle = document.getElementById('searchToggle');
    const searchModal = document.getElementById('searchModal');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    if (!searchToggle || !searchModal) return;

    // Open search modal
    searchToggle.addEventListener('click', () => {
        searchModal.classList.add('active');
        if (searchInput) {
            setTimeout(() => searchInput.focus(), 100);
        }
    });

    // Close search modal
    if (searchClose) {
        searchClose.addEventListener('click', () => {
            searchModal.classList.remove('active');
        });
    }

    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchModal.classList.contains('active')) {
            searchModal.classList.remove('active');
        }
    });

    // Close on backdrop click
    searchModal.addEventListener('click', (e) => {
        if (e.target === searchModal) {
            searchModal.classList.remove('active');
        }
    });

    // Live search functionality
    if (searchInput && searchResults) {
        let searchTimeout;

        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            const query = searchInput.value.trim();

            if (query.length < 2) {
                searchResults.innerHTML = '';
                return;
            }

            searchTimeout = setTimeout(async () => {
                try {
                    const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
                    const data = await response.json();

                    if (data.results && data.results.length > 0) {
                        searchResults.innerHTML = data.results.map(item => `
                            <a href="/${item.media_type}/${item.id}/" class="search-result-item">
                                <img src="${item.poster_url || ''}" alt="${item.title}" class="search-result-poster">
                                <div class="search-result-info">
                                    <h4>${item.title}</h4>
                                    <span class="search-result-meta">
                                        ${item.year || ''} • ${item.media_type === 'tv' ? 'TV Show' : 'Movie'}
                                        ${item.vote_average ? `• ★ ${item.vote_average}` : ''}
                                    </span>
                                </div>
                            </a>
                        `).join('');
                    } else {
                        searchResults.innerHTML = `
                            <div class="search-no-results">
                                <p>No results found for "${query}"</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    console.error('Search error:', error);
                }
            }, 300);
        });
    }
}

// ===== User Menu =====
function initUserMenu() {
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userDropdown = document.getElementById('userDropdown');

    if (!userMenuToggle || !userDropdown) return;

    userMenuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('active');
    });

    // Close on outside click
    document.addEventListener('click', () => {
        userDropdown.classList.remove('active');
    });
}

// ===== Alert Messages =====
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => alert.remove(), 300);
            });
        }

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

// ===== Video Player Controls =====
function initVideoPlayer(videoElement) {
    if (!videoElement) return;

    const container = videoElement.closest('.video-player');
    const playBtn = container.querySelector('.play-btn');
    const progressBar = container.querySelector('.progress-bar');
    const progressContainer = container.querySelector('.progress-container');
    const timeDisplay = container.querySelector('.time-display');
    const volumeSlider = container.querySelector('.volume-slider');
    const volumeBtn = container.querySelector('.volume-btn');
    const fullscreenBtn = container.querySelector('.fullscreen-btn');

    // Play/Pause
    if (playBtn) {
        playBtn.addEventListener('click', () => {
            if (videoElement.paused) {
                videoElement.play();
                playBtn.innerHTML = '<span class="material-icons-outlined">pause</span>';
            } else {
                videoElement.pause();
                playBtn.innerHTML = '<span class="material-icons-outlined">play_arrow</span>';
            }
        });
    }

    // Progress bar
    if (progressContainer && progressBar) {
        videoElement.addEventListener('timeupdate', () => {
            const progress = (videoElement.currentTime / videoElement.duration) * 100;
            progressBar.style.width = `${progress}%`;
        });

        progressContainer.addEventListener('click', (e) => {
            const rect = progressContainer.getBoundingClientRect();
            const pos = (e.clientX - rect.left) / rect.width;
            videoElement.currentTime = pos * videoElement.duration;
        });
    }

    // Time display
    if (timeDisplay) {
        videoElement.addEventListener('timeupdate', () => {
            const current = formatTime(videoElement.currentTime);
            const duration = formatTime(videoElement.duration);
            timeDisplay.textContent = `${current} / ${duration}`;
        });
    }

    // Volume
    if (volumeSlider) {
        volumeSlider.addEventListener('input', () => {
            videoElement.volume = volumeSlider.value;
        });
    }

    if (volumeBtn) {
        volumeBtn.addEventListener('click', () => {
            videoElement.muted = !videoElement.muted;
            volumeBtn.innerHTML = videoElement.muted
                ? '<span class="material-icons-outlined">volume_off</span>'
                : '<span class="material-icons-outlined">volume_up</span>';
        });
    }

    // Fullscreen
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', () => {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                container.requestFullscreen();
            }
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch (e.key) {
            case ' ':
            case 'k':
                e.preventDefault();
                playBtn?.click();
                break;
            case 'ArrowLeft':
                videoElement.currentTime -= 10;
                break;
            case 'ArrowRight':
                videoElement.currentTime += 10;
                break;
            case 'ArrowUp':
                videoElement.volume = Math.min(1, videoElement.volume + 0.1);
                break;
            case 'ArrowDown':
                videoElement.volume = Math.max(0, videoElement.volume - 0.1);
                break;
            case 'f':
                fullscreenBtn?.click();
                break;
            case 'm':
                volumeBtn?.click();
                break;
        }
    });
}

// ===== Utility Functions =====
function formatTime(seconds) {
    if (isNaN(seconds)) return '0:00';

    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hrs > 0) {
        return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ===== Lazy Loading Images =====
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.01
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// Add CSS for search results
const searchStyles = document.createElement('style');
searchStyles.textContent = `
    .search-result-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: background 0.2s ease;
    }
    
    .search-result-item:hover {
        background: var(--bg-hover);
    }
    
    .search-result-poster {
        width: 50px;
        height: 75px;
        object-fit: cover;
        border-radius: 4px;
        background: var(--bg-tertiary);
    }
    
    .search-result-info h4 {
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    
    .search-result-meta {
        font-size: 0.8rem;
        color: var(--text-secondary);
    }
    
    .search-no-results {
        text-align: center;
        padding: 2rem;
        color: var(--text-muted);
    }
    
    @keyframes slideOut {
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(searchStyles);

// ===== AI Recommendations =====
async function initAIRecommendations() {
    const section = document.getElementById('ai-recommendations-section');
    const grid = document.getElementById('ai-recommendations-grid');
    
    if (!section || !grid) return;

    try {
        const response = await fetch('/api/ai/recommendations/');
        
        if (!response.ok) {
            console.error('Failed to fetch recommendations:', response.statusText);
            return;
        }

        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            grid.innerHTML = data.results.map(video => `
                <a href="/videos/watch/${video.id}/" class="video-card">
                    ${video.thumbnail ? 
                        `<img src="${video.thumbnail}" alt="${video.title}" class="video-thumbnail">` : 
                        `<div class="video-thumbnail placeholder">
                            <span class="material-icons-outlined">movie</span>
                        </div>`
                    }
                    <div class="video-info">
                        <h3 class="video-title">${video.title}</h3>
                        <div class="video-meta">
                            <span>${escapeHtml(video.user.username)}</span>
                            <span>•</span>
                            <span>${video.views_count} views</span>
                            <span>•</span>
                            <span>${timeSince(video.created_at)}</span>
                        </div>
                    </div>
                </a>
            `).join('');
            
            // Show the section since we have results
            section.style.display = 'block';
        }
    } catch (error) {
        console.error('Error fetching AI recommendations:', error);
    }
}

// Helper to escape HTML and prevent XSS
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function timeSince(dateString) {
    const date = new Date(dateString);
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " years ago";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " months ago";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " days ago";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " hours ago";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " minutes ago";
    return Math.floor(seconds) + " seconds ago";
}

