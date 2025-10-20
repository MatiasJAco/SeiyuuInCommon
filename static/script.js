// Anime search functionality
function searchAnime() {
    const searchTerm = document.getElementById('animeSearch').value.trim();
    const resultsContainer = document.getElementById('searchResults');
    
    if (!searchTerm) {
        resultsContainer.innerHTML = '<p>Please enter a search term.</p>';
        return;
    }
    
    // Show loading state
    resultsContainer.innerHTML = '<p>Searching...</p>';
    
    // Make request to Flask backend
    fetch(`/search?term=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            resultsContainer.innerHTML = '<p>Error searching for anime. Please try again.</p>';
        });
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<p>No anime found. Try a different search term.</p>';
        return;
    }
    
    let html = '<div class="anime-results">';
    results.forEach(anime => {
        html += `
            <div class="anime-card" onclick="selectAnime('${anime.url}')">
                <div class="anime-image">
                    <img src="${anime.image_url || '/static/placeholder.png'}" alt="${anime.title}" />
                </div>
                <div class="anime-info">
                    <h3>${anime.title}</h3>
                    <p class="anime-type">${anime.type || 'Unknown'}</p>
                    ${anime.score ? `<p class="anime-score">Score: ${anime.score}</p>` : ''}
                    <p class="anime-url">Click to select</p>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    resultsContainer.innerHTML = html;
}

// Global variable to track which input field to fill
let targetInputField = null;

function selectAnime(url) {
    // Fill the target URL input field
    if (targetInputField) {
        targetInputField.value = url;
        
        // Show feedback
        const fieldName = targetInputField.id === 'text1' ? 'Anime MAL url 1' : 'Anime MAL url 2';
        const feedback = document.createElement('div');
        feedback.textContent = `URL added to ${fieldName}!`;
        feedback.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #4CAF50; color: white; padding: 10px; border-radius: 4px; z-index: 1000;';
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            document.body.removeChild(feedback);
        }, 2000);
        
        // Hide search section
        const searchSection = document.getElementById('searchSection');
        if (searchSection) {
            searchSection.style.display = 'none';
        }
        
        // Clear search results
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            searchResults.innerHTML = '';
        }
        
        // Clear search input
        const searchInput = document.getElementById('animeSearch');
        if (searchInput) {
            searchInput.value = '';
        }
        
        // Reset target field
        targetInputField = null;
    }
}

// Allow Enter key to trigger search and button click
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('animeSearch');
    const searchButton = document.getElementById('searchButton');
    const urlInput1 = document.getElementById('text1');
    const urlInput2 = document.getElementById('text2');
    const searchSection = document.getElementById('searchSection');
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchAnime();
            }
        });
    }
    
    if (searchButton) {
        searchButton.addEventListener('click', function(e) {
            e.preventDefault();
            searchAnime();
        });
    }
    
    // Show search section when clicking on URL input 1
    if (urlInput1) {
        urlInput1.addEventListener('focus', function() {
            targetInputField = urlInput1;
            if (searchSection) {
                searchSection.style.display = 'block';
                searchSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // Show search section when clicking on URL input 2
    if (urlInput2) {
        urlInput2.addEventListener('focus', function() {
            targetInputField = urlInput2;
            if (searchSection) {
                searchSection.style.display = 'block';
                searchSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
});

// Carousel functionality (keeping existing code)
const carousel = document.querySelector('.carousel');
if (carousel) {
    const slides = carousel.querySelector('.slides');
    const slideWidth = carousel.offsetWidth;
    let position = 0;

    carousel.addEventListener('mousedown', dragStart);
    carousel.addEventListener('touchstart', dragStart);
    carousel.addEventListener('mouseup', dragEnd);
    carousel.addEventListener('touchend', dragEnd);
    carousel.addEventListener('mousemove', dragMove);
    carousel.addEventListener('touchmove', dragMove);

    function dragStart(event) {
        if (event.type === 'touchstart') {
            position = event.touches[0].clientX;
        } else {
            position = event.clientX;
            event.preventDefault();
        }
    }

    function dragMove(event) {
        const currentPosition = event.type === 'touchmove' ? event.touches[0].clientX : event.clientX;
        const diff = currentPosition - position;
        slides.style.transform = `translateX(${diff}px)`;
    }

    function dragEnd(event) {
        const currentPosition = event.type === 'touchend' ? event.changedTouches[0].clientX : event.clientX;
        const diff = currentPosition - position;

        if (diff > slideWidth / 4) {
            position += slideWidth;
        } else if (diff < -slideWidth / 4) {
            position -= slideWidth;
        }

        slides.style.transform = `translateX(${position}px)`;
    }
}
