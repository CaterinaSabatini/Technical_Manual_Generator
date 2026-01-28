/**
 * TechGuide - Home Page JavaScript
 */

class TechGuideApp {
  constructor() {

    this.homeBtn = document.getElementById('homeBtn');
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
    if (this.deviceInput) {
      this.showHomeScreen();
      this.deviceInput.focus();
    }
    if (document.querySelector('.manual-content-body')) {
      this.formatManualContent();
    }
  }

  formatManualContent() {
    const contentBody = document.querySelector('.manual-content-body');
    if (!contentBody) return;

    let rawText = contentBody.innerHTML;

    rawText = rawText.replace(/\*\*(.*?)\*\*/g, '<br><h3 class="manual-section-title"> • $1</h3>');

    if (rawText.includes('<li class="manual-item">')) {
        rawText = rawText.replace(/(<li class="manual-item">.*?<\/li>(?:\s*<li class="manual-item">.*?<\/li>)*)/gs, '<ul class="manual-list">$1</ul>');
    }
    contentBody.innerHTML = rawText;
  }

  addEventListeners() {
    
    if (this.homeBtn) {
      this.homeBtn.addEventListener('click', () => this.showHomeScreen());
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
        const manualUrl = `/api/manual/${encodeURIComponent(data.manual_id.split('/').pop())}`;
        
        try {
          const checkResponse = await fetch(manualUrl, { method: 'HEAD' });
          if (checkResponse.ok) {
            window.location.href = manualUrl;
          } else {
            this.showError('Manual was generated but could not be loaded. Please try again.');
          }
        } catch (err) {
          this.showError('Unable to verify manual. Please try again.');
        }
      }
      else {
        this.showError(data.error || 'Manual not found for this device');
      }

    } catch (error) {
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
