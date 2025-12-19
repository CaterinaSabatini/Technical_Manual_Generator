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
    this.showHomeScreen();
    this.deviceInput.focus();
  }

  addEventListeners() {
    
    this.homeBtn.addEventListener('click', () => this.showHomeScreen());
    this.downloadBtn.addEventListener('click', () => this.downloadPDF());
    this.goBackBtn.addEventListener('click', () => this.showHomeScreen());
    this.searchBtn.addEventListener('click', () => this.searchManual());

    
    this.deviceInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.searchManual();
      }
    });

  }

  showHomeScreen() {
    this.hideAllSections();
    this.searchSection.classList.remove('hidden');
    this.homeBtn.classList.add('hidden');
    this.deviceInput.value = '';
    this.deviceInput.focus();
    this.currentDevice = '';
  }

  hideAllSections() {
    this.searchSection.classList.add('hidden');
    this.loadingSection.classList.add('hidden');
    this.resultsSection.classList.add('hidden');
    this.errorSection.classList.add('hidden');
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

      if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        let data;
        try {
            data = await response.json(); 
        } catch (e) {
            console.error('JSON Parsing Error:', e);
            this.showError('Received malformed response from server.');
            return;
        }

      if (data.success) {
        this.showResults(data.html);
      } else {
        this.showError(data.error || 'Manual not found for this device');
      }

    } catch (error) {
      console.error('Search Network or unhandled error::', error);
      this.showError('Connection error. Please check your Internet connection.');
    }
  }

  showLoading() {
    this.hideAllSections();
    this.loadingSection.classList.remove('hidden');
    this.homeBtn.classList.remove('hidden');
  }

  showResults(htmlContent) {
    this.hideAllSections();
    this.resultsSection.classList.remove('hidden');
    this.homeBtn.classList.remove('hidden');
    this.manualContainer.innerHTML = '';

    if (typeof htmlContent === 'string' && htmlContent.length > 0) {
      const formattedHtml = marked.parse(htmlContent);  
      this.manualContainer.innerHTML = formattedHtml;
      /*this.manualContainer.innerText = htmlContent;*/
    } else {
        this.showError('Received empty content from the server.');
        return;
    }

  }

  showError(message) {
    this.hideAllSections();
    this.errorSection.classList.remove('hidden');
    this.homeBtn.classList.remove('hidden');
    this.errorMessage.textContent = message;
  }

  async downloadPDF() {
    if (!this.currentDevice) {
      this.showError('No device selected for download');
      return;
    }
    try {
      const originalText = this.downloadBtn.textContent;
      this.downloadBtn.textContent = 'Generating PDF...';
      this.downloadBtn.disabled = true;

      const downloadUrl = `/api/download-pdf?device=${encodeURIComponent(this.currentDevice)}`;
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `${this.currentDevice}_manual.pdf`;
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      this.downloadBtn.textContent = 'Downloaded';
      setTimeout(() => {
        this.downloadBtn.textContent = originalText;
        this.downloadBtn.disabled = false;
      }, 2000);
    } catch (error) {
      console.error('Download error:', error);
      alert(`PDF download failed: ${error.message}`);
      this.downloadBtn.textContent = 'Download PDF Manual';
      this.downloadBtn.disabled = false;
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
