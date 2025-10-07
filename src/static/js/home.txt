/**
 * TechGuide - Home Page JavaScript
 * Handles all user interactions and API calls
 */

class TechGuideApp {
    constructor() {
        // Get references to DOM elements
        this.homeBtn = document.getElementById('homeBtn');
        this.searchBtn = document.getElementById('searchBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.retryBtn = document.getElementById('retryBtn');
        this.deviceInput = document.getElementById('deviceInput');
        
        // Sections
        this.searchSection = document.getElementById('searchSection');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        
        // Content containers
        this.manualContainer = document.getElementById('manualContainer');
        this.errorMessage = document.getElementById('errorMessage');
        
        // Current state
        this.currentDevice = '';
        
        // Initialize app
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.addEventListeners();
        this.showHomeScreen();
        //Simply puts the cursor directly into the input field
        this.deviceInput.focus();
    }

    /**
     * Add event listeners to all buttons and inputs
     */
    addEventListeners() {
        // Home button - return to search screen
        this.homeBtn.addEventListener('click', () => {
            this.showHomeScreen();
        });

        // Search button - search for device manual
        this.searchBtn.addEventListener('click', () => {
            this.searchManual();
        });

        // Download button - download PDF manual
        this.downloadBtn.addEventListener('click', () => {
            this.downloadPDF();
        });

        // Retry button - retry the search
        this.retryBtn.addEventListener('click', () => {
            this.retrySearch();
        });

        // Enter key on input field - trigger search
        this.deviceInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchManual();
            }
        });

        // Input validation - enable/disable search button
        this.deviceInput.addEventListener('input', () => {
            this.validateInput();
        });
    }

    /**
     * Show home screen (search section)
     */
    showHomeScreen() {
        this.hideAllSections();
        this.searchSection.classList.remove('hidden');
        this.homeBtn.classList.add('hidden');
        this.deviceInput.value = '';
        this.deviceInput.focus();
        this.currentDevice = '';
    }

    /**
     * Hide all sections
     */
    hideAllSections() {
        this.searchSection.classList.add('hidden');
        this.loadingSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
        this.errorSection.classList.add('hidden');
    }

    /**
     * Validate input field
     */
    validateInput() {
        const value = this.deviceInput.value.trim();
        
        if (value.length === 0) {
            this.searchBtn.disabled = true;
            this.searchBtn.classList.add('disabled');
        } else {
            this.searchBtn.disabled = false;
            this.searchBtn.classList.remove('disabled');
        }
    }

    /**
     * Search for device manual
     */
    async searchManual() {
        const device = this.deviceInput.value.trim();
        
        if (!device) {
            this.showError('Please enter a device name');
            return;
        }

        this.currentDevice = device;
        this.showLoading();

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ device: device })
            });

            const data = await response.json();

            if (data.success) {
                // Server returns pre-rendered HTML
                this.showResults(data.html);
            } else {
                this.showError(data.error || 'Manual not found for this device');
            }

        } catch (error) {
            console.error('Search error:', error);
            this.showError('Connection error. Please check your internet connection.');
        }
    }

    /**
     * Show loading screen
     */
    showLoading() {
        this.hideAllSections();
        this.loadingSection.classList.remove('hidden');
        this.homeBtn.classList.remove('hidden');
    }

    /**
     * Show search results
     */
    showResults(html) {
        this.hideAllSections();
        this.resultsSection.classList.remove('hidden');
        this.homeBtn.classList.remove('hidden');
        
        // Simply insert the pre-rendered HTML from server
        this.manualContainer.innerHTML = html;
    }

    /**
     * Show error screen
     */
    showError(message) {
        this.hideAllSections();
        this.errorSection.classList.remove('hidden');
        this.homeBtn.classList.remove('hidden');
        
        this.errorMessage.textContent = message;
    }


    /**
     * Download PDF manual
     */
    async downloadPDF() {
        if (!this.currentDevice) {
            this.showError('No device selected for download');
            return;
        }

        try {
            // Show loading state on download button
            const originalText = this.downloadBtn.textContent;
            this.downloadBtn.textContent = 'Generating PDF...';
            this.downloadBtn.disabled = true;

            // Simple approach: create direct download link
            const downloadUrl = `/api/download-pdf?device=${encodeURIComponent(this.currentDevice)}`;
            
            // Create temporary link and trigger download
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `${this.currentDevice}_manual.pdf`;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            // Show success feedback
            this.downloadBtn.textContent = '✓ Downloaded';
            setTimeout(() => {
                this.downloadBtn.textContent = originalText;
                this.downloadBtn.disabled = false;
            }, 2000);

        } catch (error) {
            console.error('Download error:', error);
            alert(`PDF download failed: ${error.message}`);
            
            // Reset button
            this.downloadBtn.textContent = 'Download PDF Manual';
            this.downloadBtn.disabled = false;
        }
    }

    /**
     * Retry search with current device
     */
    retrySearch() {
        if (this.currentDevice) {
            this.deviceInput.value = this.currentDevice;
            this.searchManual();
        } else {
            this.showHomeScreen();
        }
    }


}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TechGuideApp();
});
