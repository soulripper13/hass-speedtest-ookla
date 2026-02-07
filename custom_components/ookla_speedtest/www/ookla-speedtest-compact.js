/**
 * Ookla Speedtest Card - Compact Version (Bubble Style)
 * Minimalist pill-shaped card inspired by Bubble Card design
 *
 * Version: 1.4.0 - Improved masonry and sections layout compatibility
 *
 * Layout Compatibility:
 * - Masonry: Returns card size for proper column distribution
 * - Sections: Uses 3 columns x 1 row grid by default
 * - Both layouts fully supported with proper height handling
 * - Mobile-first, minimalist design
 * - Added cache busting support
 */

class OoklaSpeedtestCompact extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
  }

  static getConfigElement() {
    return document.createElement("ookla-speedtest-compact-editor");
  }

  static getStubConfig() {
    return {
      type: "custom:ookla-speedtest-compact",
      entities: {
        download: "sensor.ookla_speedtest_download",
        upload: "sensor.ookla_speedtest_upload",
        ping: "sensor.ookla_speedtest_ping"
      },
      labels: {
        download: "Download",
        upload: "Upload",
        ping: "Ping"
      }
    };
  }

  setConfig(config) {
    this._config = { ...OoklaSpeedtestCompact.getStubConfig(), ...config };
  }

  set hass(hass) {
    this._hass = hass;
    this.updateCard();
  }

  connectedCallback() {
    this.render();
  }

  /**
   * Card size for Masonry view (1 = 50px)
   * This helps masonry layout calculate proper column distribution
   */
  getCardSize() {
    return 2; // ~100px height (compact but readable)
  }

  /**
   * Layout options for Sections view (Bubble Card style)
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
    if (!this._hass) return;

    const e = this._config.entities;
    const dl = this._getState(e.download);
    const ul = this._getState(e.upload);
    const ping = this._getState(e.ping);

    const dlEl = this.querySelector('.dl-value');
    const ulEl = this.querySelector('.ul-value');
    const pingEl = this.querySelector('.ping-value');

    if (dlEl) dlEl.textContent = dl ? Math.round(dl) : '--';
    if (ulEl) ulEl.textContent = ul ? Math.round(ul) : '--';
    if (pingEl) pingEl.textContent = ping ? Math.round(ping) : '--';
  }

  _getState(entityId) {
    if (!this._hass || !entityId) return null;
    const state = this._hass.states[entityId];
    return state ? parseFloat(state.state) || null : null;
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

  _runTest() {
    if (!this._hass) return;

    this._hass.callService('ookla_speedtest', 'run_speedtest');
    const btn = this.querySelector('.action-button');
    if (btn) {
      btn.classList.add('running');
      btn.textContent = '...';
      setTimeout(() => {
        btn.classList.remove('running');
        btn.textContent = 'GO';
      }, 5000);
    }
  }

  render() {
    const labels = this._config.labels || { download: 'Download', upload: 'Upload', ping: 'Ping' };
    
    this.innerHTML = `
      <style>
        :host {
          display: block;
          width: 100%;
          height: 100%;
          box-sizing: border-box;
          container-type: inline-size;
        }

        * {
          box-sizing: border-box;
        }

        .card {
          background: var(--bubble-main-background-color, var(--ha-card-background, var(--card-background-color, rgba(255, 255, 255, 0.04))));
          backdrop-filter: blur(50px);
          -webkit-backdrop-filter: blur(50px);
          border-radius: var(--bubble-border-radius, 12px);
          padding: 4px 8px 4px 4px; /* Tighter padding */
          color: var(--primary-text-color, #f8fafc);
          font-family: var(--primary-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
          display: flex;
          flex-direction: row;
          flex-wrap: nowrap;
          align-items: center;
          justify-content: flex-start;
          border: none;
          box-shadow: var(--bubble-box-shadow, 0 2px 8px 0 rgba(0, 0, 0, 0.16));
          width: 100%;
          height: 100%;
          min-height: 50px;
          max-height: 80px;
          gap: 8px; /* Reduced gap */
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          cursor: pointer;
          position: relative;
          overflow: hidden;
          /* Ensure proper sizing in sections view */
          flex: 1;
          direction: ltr;
        }

        .card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(14, 165, 233, 0.05) 0%, rgba(167, 139, 250, 0.05) 100%);
          opacity: 0;
          transition: opacity 0.3s ease;
          pointer-events: none;
        }

        .card:hover {
          box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.24);
          transform: translateY(-1px);
        }

        .card:hover::before {
          opacity: 1;
        }

        .card:active {
          transform: scale(0.98);
        }

        .stats-container {
          display: flex;
          flex-direction: row;
          align-items: center;
          flex: 1;
          min-width: 0;
          overflow: hidden;
        }

        .stats {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          gap: 4px;
          min-width: 0;
          overflow: hidden;
        }

        .stat {
          display: flex;
          flex-direction: row;
          align-items: baseline;
          justify-content: center;
          gap: 2px;
          white-space: nowrap;
          flex: 1;
          min-width: 0;
          overflow: hidden;
          cursor: pointer;
          transition: opacity 0.2s;
        }
        
        .stat:hover {
          opacity: 0.8;
        }

        .stat-icon {
          font-size: 10px;
          opacity: 0.6;
          margin: 0;
        }

        .stat-value {
          font-size: 13px;
          font-weight: 700;
          letter-spacing: -0.02em;
        }

        .stat-unit {
          font-size: 9px;
          font-weight: 500;
          opacity: 0.5;
          margin: 0;
        }

        .stat-dl .stat-value { color: #38bdf8; }
        .stat-ul .stat-value { color: #a78bfa; }
        .stat-ping .stat-value { color: #fbbf24; }

        .action-button {
          width: 38px;
          height: 38px;
          border-radius: 50%;
          background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
          font-weight: 800;
          cursor: pointer;
          box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          flex: 0 0 auto;
          border: none;
          letter-spacing: 0.5px;
          white-space: nowrap;
          padding: 0;
        }

        .action-button:hover {
          transform: scale(1.05);
          box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
        }

        .action-button:active {
          transform: scale(0.95);
        }

        .action-button.running {
          animation: pulse-glow 1.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        }

        @keyframes pulse-glow {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.8; }
        }

        /* Container query responsive adjustments - simplified to prevent wrapping */
        @container (max-width: 320px) {
          .stat-icon { display: none; }
          .stats { gap: 4px; }
          .stat-value { font-size: 11px; }
          .stat-unit { font-size: 8px; }
          .card { padding: 4px 8px; }
        }
      </style>

      <div class="card">
        <button class="action-button">GO</button>
        <div class="stats-container">
          <div class="stats">
            <div class="stat stat-dl" title="${labels.download}">
              <span class="stat-icon">⬇</span>
              <span class="stat-value dl-value">--</span>
              <span class="stat-unit">Mbps</span>
            </div>
            <div class="stat stat-ul" title="${labels.upload}">
              <span class="stat-icon">⬆</span>
              <span class="stat-value ul-value">--</span>
              <span class="stat-unit">Mbps</span>
            </div>
            <div class="stat stat-ping" title="${labels.ping}">
              <span class="stat-icon">⏱</span>
              <span class="stat-value ping-value">--</span>
              <span class="stat-unit">ms</span>
            </div>
          </div>
        </div>
      </div>
    `;

    this.querySelector('.action-button')?.addEventListener('click', (e) => {
      e.stopPropagation();
      this._runTest();
    });
    
    // Interactive elements
    const e = this._config.entities;
    this.querySelector('.stat-dl')?.addEventListener('click', (ev) => { ev.stopPropagation(); this._showMoreInfo(e.download); });
    this.querySelector('.stat-ul')?.addEventListener('click', (ev) => { ev.stopPropagation(); this._showMoreInfo(e.upload); });
    this.querySelector('.stat-ping')?.addEventListener('click', (ev) => { ev.stopPropagation(); this._showMoreInfo(e.ping); });
  }
}

customElements.define("ookla-speedtest-compact", OoklaSpeedtestCompact);

class OoklaSpeedtestCompactEditor extends HTMLElement {
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
    const event = new CustomEvent("config-changed", { detail: { config: newConfig }, bubbles: true, composed: true });
    this.dispatchEvent(event);
  }

  render() {
    if (this._elements) return;

    this.innerHTML = '';
    this._elements = [];

    const container = document.createElement('div');
    container.style.cssText = "display: flex; flex-direction: column; gap: 12px; padding: 10px;";

    // Labels Section
    const labelsDiv = document.createElement('div');
    labelsDiv.style.cssText = "border: 1px solid var(--divider-color, #e0e0e0); border-radius: 8px; padding: 10px; background: var(--card-background-color, rgba(0,0,0,0.2));";
    labelsDiv.innerHTML = `<div style="font-weight: 500; margin-bottom: 10px; color: var(--primary-text-color); font-size: 14px;">Labels (Tooltips)</div>`;

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
    container.appendChild(labelsDiv);

    const createPicker = (key, label) => {
        const div = document.createElement('div');
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

    container.appendChild(createPicker('download', 'Download Entity'));
    container.appendChild(createPicker('upload', 'Upload Entity'));
    container.appendChild(createPicker('ping', 'Ping Entity'));

    this.appendChild(container);
  }
}
customElements.define("ookla-speedtest-compact-editor", OoklaSpeedtestCompactEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "ookla-speedtest-compact",
  name: "Ookla Speedtest - Compact (Bubble Style)",
  description: "Minimalist pill-shaped card inspired by Bubble Card design - perfect for side panels",
  preview: true
});

console.info("%c OOKLA COMPACT (BUBBLE) %c v1.4.4 ", "background: #0ea5e9; color: #fff; font-weight: bold;", "background: #1e293b; color: #fff;");
