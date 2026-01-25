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
    
    // Se siamo sulla pagina del manuale, formatta il contenuto
    if (document.querySelector('.manual-content-body')) {
      this.formatManualContent();
    }
  }

  formatManualContent() {
    // Cerchiamo il div che contiene il testo generato da Jinja
    const contentBody = document.querySelector('.manual-content-body');
    if (!contentBody) return;

    let rawText = contentBody.innerHTML;

    // 1. TRASFORMAZIONE TITOLI SEZIONE (**Titolo**)
    // Cerca i doppi asterischi, mette in grassetto, aggiunge un'icona e va a capo
    rawText = rawText.replace(/\*\*(.*?)\*\*/g, '<br><h3 class="manual-section-title"> • $1</h3>');

    // 2. TRASFORMAZIONE PUNTI ELENCO (* Elemento)
    // Cerca l'asterisco singolo e lo trasforma in un elemento di lista stilizzato
    rawText = rawText.replace(/^\s*\*\s+(.+)$/gm, '<li class="manual-item">$1</li>');

    // 3. AVVOLGIMENTO LISTE
    // Se abbiamo creato dei <li>, dobbiamo assicurarci che siano dentro un <ul>
    if (rawText.includes('<li class="manual-item">')) {
        // Questa regex raggruppa righe consecutive di <li> in un unico <ul>
        rawText = rawText.replace(/(<li class="manual-item">.*?<\/li>(?:\s*<li class="manual-item">.*?<\/li>)*)/gs, '<ul class="manual-list">$1</ul>');
    }

    // Reinseriamo l'HTML formattato nel contenitore
    contentBody.innerHTML = rawText;
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

        // Salva lo scroll corrente
        const originalScrollY = window.scrollY;
        
        // Scorri all'inizio della pagina
        window.scrollTo(0, 0);

        // Trova tutti gli elementi che potrebbero avere overflow o altezza limitata
        const elementsToFix = [
          this.manualContainer,
          this.manualContainer.parentElement,
          document.querySelector('.manual-content-body'),
          document.body
        ].filter(el => el !== null);

        // Salva gli stili originali di tutti gli elementi
        const originalStyles = elementsToFix.map(el => ({
          element: el,
          overflow: el.style.overflow,
          overflowY: el.style.overflowY,
          maxHeight: el.style.maxHeight,
          height: el.style.height
        }));

        // Rimuovi tutte le limitazioni
        elementsToFix.forEach(el => {
          el.style.overflow = 'visible';
          el.style.overflowY = 'visible';
          el.style.maxHeight = 'none';
          el.style.height = 'auto';
        });

        // Aspetta un momento per assicurarsi che il layout sia aggiornato
        await new Promise(resolve => setTimeout(resolve, 100));

        // Get device name from the page
        const deviceTitle = document.querySelector('h2')?.textContent || 'manual';
        const filename = deviceTitle.replace(/[^a-zA-Z0-9]/g, '_') + '.pdf';

        const opt = {
          margin: 10,
          filename: filename,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { 
            scale: 2,
            useCORS: true,
            logging: false,
            allowTaint: true
          },
          jsPDF: { 
            unit: 'mm', 
            format: 'a4', 
            orientation: 'portrait' 
          },
          pagebreak: { 
            mode: ['avoid-all', 'css', 'legacy'],
            before: '.manual-section-title'
          }
        };

        await html2pdf().set(opt).from(this.manualContainer).save();

        // Ripristina tutti gli stili originali
        originalStyles.forEach(({ element, overflow, overflowY, maxHeight, height }) => {
          element.style.overflow = overflow;
          element.style.overflowY = overflowY;
          element.style.maxHeight = maxHeight;
          element.style.height = height;
        });

        // Ripristina lo scroll originale
        window.scrollTo(0, originalScrollY);

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
