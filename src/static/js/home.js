/**
 * TechGuide - Home Page JavaScript
 * Handles all user interactions and API calls for search
 */

class TechGuideApp {
    constructor() {
        // Get references to DOM elements
        this.searchBtn = document.getElementById('searchBtn');
        this.deviceInput = document.getElementById('deviceInput');
        
        this.init();
    }

    init() {
        this.searchBtn.addEventListener('click', () => this.handleSubtitleSearch());
        this.deviceInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSubtitleSearch();
            }
        });
    }

    async handleSubtitleSearch() {
        const device = this.deviceInput.value.trim();
        
        if (!device) {
            alert('Please enter a device name');
            return;
        }

        this.searchBtn.disabled = true;
        this.searchBtn.innerHTML = '<span class="btn-text">Searching...</span>';

        try {
            const response = await fetch('/api/search-subtitles', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device: device
                })
            });

            const result = await response.json();
            //Debug code
            if (result.success) {
                alert(`${result.message}\n\n${result.info}`);
                console.log('Subtitle search completed:', result);
            } else {
                alert(`Error: ${result.error}`);
                console.error('Subtitle search error:', result);
            }

        } catch (error) {
            console.error('Network error:', error);
            alert('Network error occurred. Please try again.');
        } finally {
            this.searchBtn.disabled = false;
            this.searchBtn.innerHTML = '<span class="btn-text">Search</span>';
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TechGuideApp();
});