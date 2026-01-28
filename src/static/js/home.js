/**
 * TechGuide - Home Page JavaScript
 * Handles all user interactions and API calls
 */

class TechGuideApp {
  constructor() {

    this.homeBtn = document.getElementById('homeBtn');
    this.downloadBtn = document.getElementById('downloadBtn');
    this.goBackBtn = document.getElementById('goBackBtn');
    
 
    this.searchBtn = document.getElementById('searchBtn'); 
    this.deviceInput = document.getElementById('deviceInput');
    
    
    this.searchSection = document.getElementById('searchSection');
    this.loadingSection = document.getElementById('loadingSection');
    this.resultsSection = document.getElementById('resultsSection');
    this.errorSection = document.getElementById('errorSection');
    
    
    this.manualContainer = document.getElementById('manualContainer');
    this.errorMessage = document.getElementById('errorMessage');
    
    
    this.currentDevice = '';
    
    this.init();

  }

  init() {
    this.addEventListeners();
    // Only call showHomeScreen if we're on home page (has deviceInput)
    if (this.deviceInput) {
      this.showHomeScreen();
      this.deviceInput.focus();
    }
  }

  addEventListeners() {
    
    if (this.homeBtn) {
      this.homeBtn.addEventListener('click', () => this.showHomeScreen());
    }
    if (this.downloadBtn) {
      this.downloadBtn.addEventListener('click', () => this.downloadPDF());
    }
    if (this.goBackBtn) {
      this.goBackBtn.addEventListener('click', () => this.showHomeScreen());
    }
    if (this.searchBtn) {
      this.searchBtn.addEventListener('click', () => this.searchManual());
    }

    
    if (this.deviceInput) {
      this.deviceInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this.searchManual();
        }
      });
    }

  }

  showHomeScreen() {
    this.hideAllSections();
    if (this.searchSection) {
      this.searchSection.classList.remove('hidden');
    }
    if (this.homeBtn) {
      this.homeBtn.classList.add('hidden');
    }
    if (this.deviceInput) {
      this.deviceInput.value = '';
      this.deviceInput.focus();
    }
    this.currentDevice = '';
  }

  hideAllSections() {
    if (this.searchSection) {
      this.searchSection.classList.add('hidden');
    }
    if (this.loadingSection) {
      this.loadingSection.classList.add('hidden');
    }
    if (this.resultsSection) {
      this.resultsSection.classList.add('hidden');
    }
    if (this.errorSection) {
      this.errorSection.classList.add('hidden');
    }
  }

  async searchManual() {
    const device = this.deviceInput.value.trim();
    
    if (!device) {
      this.showError('Please enter a device name');
      return;
    }

    this.currentDevice = device;
    this.showLoading();

    try {
      const response = await fetch('/api/manual-generation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ device: device })
      });

        const data = await response.json();

        if (!response.ok) {
          this.showError(data.error || `Server Error: ${response.status}`);
          return;
      } 

      if (data.success && data.manual_id) {
        // Verify the manual page exists before redirecting
        const manualUrl = `/api/manual/${encodeURIComponent(data.manual_id.split('/').pop())}`;
        
        try {
          const checkResponse = await fetch(manualUrl, { method: 'HEAD' });
          if (checkResponse.ok) {
            window.location.href = manualUrl;
          } else {
            this.showError('Manual was generated but could not be loaded. Please try again.');
          }
        } catch (err) {
          console.error('Error checking manual:', err);
          this.showError('Unable to verify manual. Please try again.');
        }
      }
      else {
        this.showError(data.error || 'Manual not found for this device');
      }

    } catch (error) {
      console.error('Search Network or unhandled error::', error);
      this.showError('Error fetching manual. ' + error.message);
    }
  }

  showLoading() {
    this.hideAllSections();
    this.loadingSection.classList.remove('hidden');
    this.homeBtn.classList.remove('hidden');
  }


  showError(message) {
    this.hideAllSections();
    this.errorSection.classList.remove('hidden');
    this.homeBtn.classList.remove('hidden');
    this.errorMessage.textContent = message;
  }

  async downloadPDF() {
    console.log('downloadPDF called');
    try {
      if (!this.manualContainer) {
        console.error('Manual container not found');
        alert('Unable to find manual content');
        return;
      }

      if (this.downloadBtn) {
        const originalText = this.downloadBtn.textContent;
        this.downloadBtn.textContent = 'Generating PDF...';
        this.downloadBtn.disabled = true;

        // Get device name from the page
        const deviceTitle = document.querySelector('h2')?.textContent || 'manual';
        const filename = deviceTitle.replace(/[^a-zA-Z0-9]/g, '_') + '.pdf';

        const opt = {
          margin: 10,
          filename: filename,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2 },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        await html2pdf().set(opt).from(this.manualContainer).save();

        this.downloadBtn.textContent = 'Downloaded!';
        setTimeout(() => {
          this.downloadBtn.textContent = originalText;
          this.downloadBtn.disabled = false;
        }, 2000);
      }
    } catch (error) {
      console.error('PDF generation error:', error);
      alert('PDF generation failed: ' + error.message);
      if (this.downloadBtn) {
        this.downloadBtn.textContent = 'Download PDF Manual';
        this.downloadBtn.disabled = false;
      }
    }
  }

  retrySearch() {
    if (this.currentDevice) {
      this.deviceInput.value = this.currentDevice;
      this.searchManual();
    } else {
      this.showHomeScreen();
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.techGuideApp = new TechGuideApp();
});
