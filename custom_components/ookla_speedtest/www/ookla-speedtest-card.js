/**
 * Ookla Speedtest Card for Home Assistant
 * A custom Lovelace card that recreates the iconic Ookla Speedtest interface
 *
 * Version: 1.4.0 - Improved masonry and sections layout compatibility
 *
 * Layout Compatibility:
 * - Masonry: Returns card size for proper column distribution
 * - Sections: Uses 6 columns x 4 rows grid by default
 * - Both layouts fully supported with proper height handling
 * - Added cache busting support
 */

class OoklaSpeedtestCard extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
    this._isRunning = false;
  }

  static getConfigElement() {
    return document.createElement("ookla-speedtest-card-editor");
  }

  static getStubConfig() {
    return {
      type: "custom:ookla-speedtest-card",
      entities: {
        download: "sensor.ookla_speedtest_download",
        upload: "sensor.ookla_speedtest_upload",
        ping: "sensor.ookla_speedtest_ping",
        jitter: "sensor.ookla_speedtest_jitter",
        grade: "sensor.ookla_speedtest_bufferbloat_grade",
        isp: "sensor.ookla_speedtest_isp",
        server: "sensor.ookla_speedtest_server",
        last_test: "sensor.ookla_speedtest_last_test",
        result_url: "sensor.ookla_speedtest_result_url"
      },
      labels: {
        download: "Download",
        upload: "Upload",
        ping: "Ping",
        jitter: "Jitter",
        grade: "Grade"
      },
      max_download: 1000,
      max_upload: 500,
      show_gauges: true,
      theme: "dark"
    };
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Invalid configuration");
    }
    this._config = {
      ...OoklaSpeedtestCard.getStubConfig(),
      ...config
    };
  }

  set hass(hass) {
    this._hass = hass;
    this.updateCard();
  }

  get hass() {
    return this._hass;
  }

  connectedCallback() {
    this.render();
  }

  /**
   * Card size for Masonry view (1 = 50px)
   * This helps masonry layout calculate proper column distribution
   */
  getCardSize() {
    return 12; // ~600px height
  }

  /**
   * Layout options for Sections view
   * Sections use a 12-column grid system
   * 
   * grid_columns: How many columns the card should occupy (1-12)
   * grid_rows: How many rows the card should occupy (1+), each row is ~56px
   * grid_min/max: Constraints for user resizing
   */
  static getLayoutOptions() {
    return {
      grid_columns: null,     // Automatic width
      grid_rows: null,        // Automatic height
    };
  }

  getLayoutOptions() {
    return {
      grid_columns: null,     // Automatic width
      grid_rows: null,        // Automatic height
    };
  }

  updateCard() {
    if (!this._hass || !this.isConnected) return;
    
    const entities = this._config.entities;
    const download = this._getState(entities.download);
    const upload = this._getState(entities.upload);
    const ping = this._getState(entities.ping);
    const jitter = this._getState(entities.jitter);
    const grade = this._getState(entities.grade);
    const isp = this._getState(entities.isp);
    const server = this._getState(entities.server);
    const lastTest = this._getState(entities.last_test);
    const resultUrl = this._getState(entities.result_url);

    // Update gauge values
    this._updateGauge('download', download, this._config.max_download);
    this._updateGauge('upload', upload, this._config.max_upload);

    // Update metrics
    this._updateMetric('ping', ping, 'ms');
    this._updateMetric('jitter', jitter, 'ms');
    this._updateMetric('grade', grade, '');

    // Update header
    const ispEl = this.querySelector('.isp-name');
    const serverEl = this.querySelector('.server-name');
    if (ispEl) ispEl.textContent = isp || 'Unknown ISP';
    if (serverEl) serverEl.textContent = server || 'Unknown Server';

    // Update footer
    const lastTestEl = this.querySelector('.last-test');
    if (lastTestEl && lastTest) {
      lastTestEl.textContent = this._formatDate(lastTest);
    }

    // Update result link
    const resultLink = this.querySelector('.result-link');
    if (resultLink) {
      if (resultUrl && resultUrl.startsWith('http')) {
        resultLink.href = resultUrl;
        resultLink.style.display = 'inline-block';
      } else {
        resultLink.style.display = 'none';
      }
    }
  }

  _getState(entityId) {
    if (!this._hass || !entityId) return null;
    const state = this._hass.states[entityId];
    return state ? state.state : null;
  }
  
  _showMoreInfo(entityId) {
    if (!entityId) return;
    const event = new CustomEvent('hass-more-info', {
      bubbles: true,
      composed: true,
      detail: { entityId }
    });
    this.dispatchEvent(event);
  }

  _updateGauge(type, value, max) {
    const gauge = this.querySelector(`.gauge-${type} .gauge-fill`);
    const valueEl = this.querySelector(`.gauge-${type} .gauge-value`);
    
    if (!gauge || !valueEl) return;

    const numValue = parseFloat(value) || 0;
    const percentage = Math.min((numValue / max) * 100, 100);
    
    // Calculate stroke dashoffset for SVG circle (270 degrees)
    const maxArc = 424; 
    const offset = maxArc * (1 - percentage / 100);
    
    gauge.style.strokeDashoffset = offset;
    
    // Color based on percentage
    let color = '#ef4444'; // red
    if (percentage >= 50) color = '#22d3ee'; // cyan
    if (percentage >= 80) color = '#22c55e'; // green
    
    gauge.style.stroke = color;
    valueEl.textContent = Math.round(numValue);
    valueEl.style.color = color;
  }

  _updateMetric(type, value, unit) {
    const el = this.querySelector(`.metric-${type} .metric-value`);
    if (el) {
      let displayValue = value || '-';
      if (type === 'grade' && value) {
        const colors = { 'A+': '#22c55e', 'A': '#22c55e', 'B': '#84cc16', 'C': '#eab308' };
        const color = colors[value] || '#ef4444';
        el.innerHTML = `<span style="color:${color}">${value}</span>`;
      } else {
        el.textContent = displayValue + (unit ? ` ${unit}` : '');
      }
    }
  }

  _formatDate(dateStr) {
    if (!dateStr || dateStr === 'unknown' || dateStr === 'unavailable') return 'Never';
    try {
      const date = new Date(dateStr);
      return date.toLocaleString();
    } catch {
      return dateStr;
    }
  }

  _runSpeedtest() {
    if (this._isRunning) return;
    
    this._isRunning = true;
    const btn = this.querySelector('.go-button');
    if (btn) {
      btn.classList.add('running');
      btn.textContent = '...';
    }

    this._hass.callService('ookla_speedtest', 'run_speedtest').then(() => {
      setTimeout(() => {
        this._isRunning = false;
        if (btn) {
          btn.classList.remove('running');
          btn.textContent = 'GO';
        }
      }, 3000);
    });
  }

  render() {
    const labels = this._config.labels || { download: 'Download', upload: 'Upload', ping: 'Ping', jitter: 'Jitter', grade: 'Grade' };
    
    this.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          width: 100%;
          height: 100%;
          box-sizing: border-box;
          container-type: inline-size;
        }

        * {
          box-sizing: border-box;
        }

        .card {
          background: rgba(15, 23, 42, 0.6);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 24px;
          padding: 20px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
          border: 1px solid rgba(255, 255, 255, 0.08);
          color: #f8fafc;
          position: relative;
          overflow: hidden;
          width: 100%;
          height: 100%;
          min-height: 0;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          /* Ensure card fills available space in sections view */
          flex: 1;
        }

        .card::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: radial-gradient(circle at 50% 50%, rgba(34, 211, 238, 0.05), transparent 60%);
          pointer-events: none;
          z-index: 0;
        }
        
        .content-wrapper {
          position: relative;
          z-index: 1;
        }
        
        .header {
          text-align: center;
          margin-bottom: 16px;
          display: flex;
          flex-direction: column;
          align-items: center;
          flex-shrink: 0;
        }
        
        .header-icon {
          font-size: 28px;
          margin-bottom: 12px;
          background: rgba(255,255,255,0.05);
          width: 50px;
          height: 50px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .isp-name {
          font-size: 20px;
          font-weight: 700;
          color: #f8fafc;
          margin-bottom: 4px;
          text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .server-name {
          font-size: 13px;
          color: #94a3b8;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        
        .gauges-container {
          display: flex;
          justify-content: center;
          gap: 16px;
          margin: 16px 0;
          position: relative;
          flex: 1;
          align-items: center;
        }
        
        .gauge {
          position: relative;
          width: 140px;
          height: 140px;
          flex-shrink: 0;
          cursor: pointer;
          transition: transform 0.2s;
        }
        
        .gauge:hover {
          transform: scale(1.05);
        }
        
        .gauge-svg {
          transform: rotate(135deg);
          width: 100%;
          height: 100%;
        }
        
        .gauge-bg {
          fill: none;
          stroke: rgba(255,255,255,0.05);
          stroke-width: 12;
          stroke-linecap: round;
          stroke-dasharray: 424 566;
          stroke-dashoffset: 0;
        }
        
        .gauge-fill {
          fill: none;
          stroke-width: 12;
          stroke-linecap: round;
          stroke-dasharray: 424 566; /* 2 * PI * 90 * 0.75 */
          stroke-dashoffset: 424;
          transition: stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease;
          filter: drop-shadow(0 0 4px currentColor);
        }
        
        .gauge-content {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        
        .gauge-label {
          font-size: 11px;
          color: #94a3b8;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          margin-bottom: 8px;
          font-weight: 600;
        }
        
        .gauge-value {
          font-size: 32px;
          font-weight: 800;
          color: #fff;
          line-height: 1;
          letter-spacing: -0.5px;
          text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .gauge-unit {
          font-size: 12px;
          color: #64748b;
          margin-top: 4px;
          font-weight: 500;
        }
        
        .go-button-container {
          display: flex;
          justify-content: center;
          margin: -30px 0 20px;
          position: relative;
          z-index: 10;
        }
        
        .go-button {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          border: 4px solid rgba(255,255,255,0.1);
          background: radial-gradient(circle at 30% 30%, #0ea5e9, #0284c7);
          color: white;
          font-size: 20px;
          font-weight: 900;
          letter-spacing: 1px;
          cursor: pointer;
          box-shadow: 
            0 0 20px rgba(14, 165, 233, 0.4),
            inset 0 0 20px rgba(255,255,255,0.2),
            0 10px 20px rgba(0,0,0,0.3);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          text-shadow: 0 2px 4px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .go-button:hover {
          transform: scale(1.05) translateY(-2px);
          box-shadow: 
            0 0 30px rgba(14, 165, 233, 0.6),
            inset 0 0 20px rgba(255,255,255,0.3),
            0 15px 25px rgba(0,0,0,0.4);
          background: radial-gradient(circle at 30% 30%, #38bdf8, #0ea5e9);
        }
        
        .go-button:active {
          transform: scale(0.95) translateY(0);
          box-shadow: 0 0 10px rgba(14, 165, 233, 0.4);
        }
        
        .go-button.running {
          animation: pulse 1.5s infinite;
          background: radial-gradient(circle at 30% 30%, #10b981, #059669);
          box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        }
        
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
          70% { box-shadow: 0 0 0 20px rgba(16, 185, 129, 0); }
          100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        
        .metrics {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-bottom: 16px;
        }
        
        .metric {
          background: rgba(255,255,255,0.03);
          border-radius: 16px;
          padding: 16px 12px;
          text-align: center;
          border: 1px solid rgba(255,255,255,0.02);
          transition: transform 0.2s, background 0.2s;
          cursor: pointer;
        }
        
        .metric:hover {
          background: rgba(255,255,255,0.05);
          transform: translateY(-2px);
        }
        
        .metric-icon {
          font-size: 20px;
          margin-bottom: 8px;
          opacity: 0.8;
        }
        
        .metric-label {
          font-size: 10px;
          color: #94a3b8;
          text-transform: uppercase;
          letter-spacing: 1px;
          margin-bottom: 4px;
          font-weight: 600;
        }
        
        .metric-value {
          font-size: 16px;
          font-weight: 700;
          color: #f8fafc;
        }
        
        .metric-ping .metric-value { color: #fbbf24; text-shadow: 0 0 10px rgba(251, 191, 36, 0.3); }
        .metric-jitter .metric-value { color: #a78bfa; text-shadow: 0 0 10px rgba(167, 139, 250, 0.3); }
        .metric-grade .metric-value { font-size: 18px; }
        
        .footer {
          text-align: center;
          padding-top: 16px;
          border-top: 1px solid rgba(255,255,255,0.05);
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-shrink: 0;
        }
        
        .last-test {
          font-size: 11px;
          color: #64748b;
          display: flex;
          align-items: center;
          gap: 6px;
          cursor: pointer;
        }
        
        .last-test::before {
          content: '';
          display: block;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #64748b;
        }
        
        .result-link {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          color: #38bdf8;
          text-decoration: none;
          font-size: 12px;
          font-weight: 600;
          transition: all 0.2s;
          padding: 6px 12px;
          border-radius: 20px;
          background: rgba(56, 189, 248, 0.1);
        }
        
        .result-link:hover {
          background: rgba(56, 189, 248, 0.2);
          color: #7dd3fc;
        }

        /* Container query responsive adjustments */
        @container (max-width: 450px) {
          .card { padding: 16px; }
          .gauges-container { gap: 12px; }
          .gauge { width: 120px; height: 120px; }
          .gauge-value { font-size: 28px; }
          .go-button { width: 70px; height: 70px; font-size: 18px; }
          .metrics { gap: 8px; }
          .metric { padding: 12px 8px; }
        }

        @container (max-width: 350px) {
          .gauges-container { flex-direction: column; gap: 8px; }
          .gauge { width: 100px; height: 100px; }
          .gauge-value { font-size: 24px; }
          .go-button { width: 60px; height: 60px; font-size: 16px; }
          .go-button-container { margin: -20px 0 16px; }
        }
</style>
      
      <div class="card">
        <div class="content-wrapper">
          <div class="header">
            <div class="header-icon">🌐</div>
            <div class="isp-name">Loading...</div>
            <div class="server-name">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
              <span>-</span>
            </div>
          </div>
          
          <div class="gauges-container">
            <div class="gauge gauge-download">
              <svg class="gauge-svg" viewBox="0 0 200 200">
                <!-- Defs for gradients -->
                <defs>
                  <linearGradient id="grad-download" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#0ea5e9;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#22d3ee;stop-opacity:1" />
                  </linearGradient>
                  <linearGradient id="grad-upload" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#a78bfa;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <circle class="gauge-bg" cx="100" cy="100" r="90"></circle>
                <circle class="gauge-fill" cx="100" cy="100" r="90" stroke="url(#grad-download)"></circle>
              </svg>
              <div class="gauge-content">
                <div class="gauge-label">${labels.download}</div>
                <div class="gauge-value">0</div>
                <div class="gauge-unit">Mbps</div>
              </div>
            </div>
            
            <div class="gauge gauge-upload">
              <svg class="gauge-svg" viewBox="0 0 200 200">
                <circle class="gauge-bg" cx="100" cy="100" r="90"></circle>
                <circle class="gauge-fill" cx="100" cy="100" r="90" stroke="url(#grad-upload)"></circle>
              </svg>
              <div class="gauge-content">
                <div class="gauge-label">${labels.upload}</div>
                <div class="gauge-value">0</div>
                <div class="gauge-unit">Mbps</div>
              </div>
            </div>
          </div>
          
          <div class="go-button-container">
            <button class="go-button">GO</button>
          </div>
          
          <div class="metrics">
            <div class="metric metric-ping">
              <div class="metric-icon">⚡</div>
              <div class="metric-label">${labels.ping}</div>
              <div class="metric-value">- ms</div>
            </div>
            <div class="metric metric-jitter">
              <div class="metric-icon">📶</div>
              <div class="metric-label">${labels.jitter}</div>
              <div class="metric-value">- ms</div>
            </div>
            <div class="metric metric-grade">
              <div class="metric-icon">🏆</div>
              <div class="metric-label">${labels.grade}</div>
              <div class="metric-value">-</div>
            </div>
          </div>
          
          <div class="footer">
            <div class="last-test">Never tested</div>
            <a href="#" class="result-link" target="_blank" rel="noopener noreferrer" style="display:none;">View Results</a>
          </div>
        </div>
      </div>
    `;

    // Add event listeners
    const goBtn = this.querySelector('.go-button');
    if (goBtn) {
      goBtn.addEventListener('click', () => this._runSpeedtest());
    }

    // Interactive elements
    const entities = this._config.entities;
    this.querySelector('.gauge-download')?.addEventListener('click', () => this._showMoreInfo(entities.download));
    this.querySelector('.gauge-upload')?.addEventListener('click', () => this._showMoreInfo(entities.upload));
    this.querySelector('.metric-ping')?.addEventListener('click', () => this._showMoreInfo(entities.ping));
    this.querySelector('.metric-jitter')?.addEventListener('click', () => this._showMoreInfo(entities.jitter));
    this.querySelector('.metric-grade')?.addEventListener('click', () => this._showMoreInfo(entities.grade));
    this.querySelector('.last-test')?.addEventListener('click', () => this._showMoreInfo(entities.last_test));
  }
}

// Register the card
customElements.define("ookla-speedtest-card", OoklaSpeedtestCard);

class OoklaSpeedtestCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._elements) {
      this._elements.forEach(el => el.hass = hass);
    }
  }

  configChanged(newConfig) {
    const event = new CustomEvent("config-changed", {
      detail: { config: newConfig },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  render() {
    if (this._elements) return;

    this.innerHTML = '';
    this._elements = [];

    const container = document.createElement('div');
    container.style.cssText = "display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px;";

    // Gauge Settings Section
    const gaugeDiv = document.createElement('div');
    gaugeDiv.style.cssText = "border: 1px solid var(--divider-color, #e0e0e0); border-radius: 8px; padding: 10px; background: var(--card-background-color, rgba(0,0,0,0.2));";
    gaugeDiv.innerHTML = `<div style="font-weight: 500; margin-bottom: 10px; color: var(--primary-text-color); font-size: 14px;">Gauge Scale Settings</div>`;

    const createInput = (key, label, defaultValue) => {
      const div = document.createElement('div');
      div.style.cssText = "display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;";
      
      const lbl = document.createElement('label');
      lbl.innerText = label;
      lbl.style.cssText = "font-size: 13px; color: var(--primary-text-color);";
      div.appendChild(lbl);

      const input = document.createElement('input');
      input.type = "number";
      input.value = this._config[key] || defaultValue;
      input.style.cssText = "padding: 6px; border-radius: 4px; border: 1px solid var(--divider-color, #888); background: var(--card-background-color, #fff); color: var(--primary-text-color, #000); width: 80px;";
      input.addEventListener('change', (e) => {
        this.configChanged({ ...this._config, [key]: Number(e.target.value) });
      });
      
      div.appendChild(input);
      return div;
    };

    gaugeDiv.appendChild(createInput('max_download', 'Max Download (Mbps)', 1000));
    gaugeDiv.appendChild(createInput('max_upload', 'Max Upload (Mbps)', 500));
    container.appendChild(gaugeDiv);

    // Labels Section
    const labelsDiv = document.createElement('div');
    labelsDiv.style.cssText = "border: 1px solid var(--divider-color, #e0e0e0); border-radius: 8px; padding: 10px; background: var(--card-background-color, rgba(0,0,0,0.2));";
    labelsDiv.innerHTML = `<div style="font-weight: 500; margin-bottom: 10px; color: var(--primary-text-color); font-size: 14px;">Labels</div>`;

    const createLabelInput = (key, label, defaultValue) => {
      const div = document.createElement('div');
      div.style.cssText = "display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;";
      
      const lbl = document.createElement('label');
      lbl.innerText = label;
      lbl.style.cssText = "font-size: 13px; color: var(--primary-text-color);";
      div.appendChild(lbl);

      const input = document.createElement('input');
      input.type = "text";
      input.value = (this._config.labels && this._config.labels[key]) || defaultValue;
      input.style.cssText = "padding: 6px; border-radius: 4px; border: 1px solid var(--divider-color, #888); background: var(--card-background-color, #fff); color: var(--primary-text-color, #000); width: 100px;";
      input.addEventListener('change', (e) => {
        const labels = { ...(this._config.labels || {}) };
        labels[key] = e.target.value;
        this.configChanged({ ...this._config, labels });
      });
      
      div.appendChild(input);
      return div;
    };

    labelsDiv.appendChild(createLabelInput('download', 'Download', 'Download'));
    labelsDiv.appendChild(createLabelInput('upload', 'Upload', 'Upload'));
    labelsDiv.appendChild(createLabelInput('ping', 'Ping', 'Ping'));
    labelsDiv.appendChild(createLabelInput('jitter', 'Jitter', 'Jitter'));
    labelsDiv.appendChild(createLabelInput('grade', 'Grade', 'Grade'));
    container.appendChild(labelsDiv);

    // Entities Section
    const entitiesDiv = document.createElement('div');
    entitiesDiv.style.cssText = "border: 1px solid var(--divider-color, #e0e0e0); border-radius: 8px; padding: 10px; background: var(--card-background-color, rgba(0,0,0,0.2));";
    entitiesDiv.innerHTML = `<div style="font-weight: 500; margin-bottom: 10px; color: var(--primary-text-color); font-size: 14px;">Entities</div>`;

    const createPicker = (key, label) => {
      const div = document.createElement('div');
      div.style.marginBottom = "12px";
      
      const lbl = document.createElement('label');
      lbl.innerText = label;
      lbl.style.cssText = "font-size: 12px; color: var(--secondary-text-color); margin-bottom: 4px; display: block;";
      div.appendChild(lbl);

      const picker = document.createElement('ha-entity-picker');
      picker.hass = this._hass;
      picker.value = (this._config.entities && this._config.entities[key]) || '';
      picker.includeDomains = ['sensor'];
      picker.allowCustomEntity = true;
      picker.addEventListener('value-changed', (e) => {
        const entities = { ...(this._config.entities || {}) };
        entities[key] = e.detail.value;
        this.configChanged({ ...this._config, entities });
      });
      
      this._elements.push(picker);
      div.appendChild(picker);
      return div;
    };

    const entityFields = [
      { key: 'download', label: 'Download Speed' },
      { key: 'upload', label: 'Upload Speed' },
      { key: 'ping', label: 'Ping Latency' },
      { key: 'jitter', label: 'Jitter' },
      { key: 'grade', label: 'Bufferbloat Grade' },
      { key: 'isp', label: 'ISP Name' },
      { key: 'server', label: 'Server Name' },
      { key: 'last_test', label: 'Last Test Time' },
      { key: 'result_url', label: 'Result URL' }
    ];

    entityFields.forEach(f => entitiesDiv.appendChild(createPicker(f.key, f.label)));
    container.appendChild(entitiesDiv);

    this.appendChild(container);
  }
}

customElements.define("ookla-speedtest-card-editor", OoklaSpeedtestCardEditor);

// Add to card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "ookla-speedtest-card",
  name: "Ookla Speedtest",
  description: "Beautiful Ookla-style speedtest interface with radial gauges",
  preview: true,
  documentationURL: "https://github.com/soulripper13/hass-speedtest-ookla"
});

console.info("%c OOKLA SPEEDTEST CARD %c v1.4.3 ", "background: #00d2ff; color: #fff; font-weight: bold;", "background: #1e293b; color: #fff;");