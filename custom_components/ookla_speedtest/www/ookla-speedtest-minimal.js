/**
 * Ookla Speedtest Card - Minimal Version
 * A clean, simple speedtest card with large typography
 *
 * Version: 1.4.0 - Improved masonry and sections layout compatibility
 *
 * Layout Compatibility:
 * - Masonry: Returns card size for proper column distribution
 * - Sections: Uses 4 columns x 3 rows grid by default
 * - Both layouts fully supported with proper height handling
 * - Added cache busting support
 */

class OoklaSpeedtestMinimal extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
  }

  static getConfigElement() {
    return document.createElement("ookla-speedtest-minimal-editor");
  }

  static getStubConfig() {
    return {
      type: "custom:ookla-speedtest-minimal",
      entities: {
        download: "sensor.ookla_speedtest_download",
        upload: "sensor.ookla_speedtest_upload",
        ping: "sensor.ookla_speedtest_ping",
        isp: "sensor.ookla_speedtest_isp"
      },
      labels: {
        download: "Download",
        upload: "Upload",
        ping: "Ping"
      }
    };
  }

  setConfig(config) {
    this._config = { ...OoklaSpeedtestMinimal.getStubConfig(), ...config };
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
    return 6; // ~300px height
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
    if (!this._hass) return;
    
    const e = this._config.entities;
    const download = this._getState(e.download);
    const upload = this._getState(e.upload);
    const ping = this._getState(e.ping);
    const isp = this._getState(e.isp);

    const dlEl = this.querySelector('.speed-download');
    const ulEl = this.querySelector('.speed-upload');
    const pingEl = this.querySelector('.ping-value');
    const ispEl = this.querySelector('.isp-text');

    if (dlEl) dlEl.textContent = download ? `${Math.round(download)} Mbps` : '--';
    if (ulEl) ulEl.textContent = upload ? `${Math.round(upload)} Mbps` : '--';
    if (pingEl) pingEl.textContent = ping ? `${Math.round(ping)} ms` : '--';
    if (ispEl) ispEl.textContent = isp || 'Unknown ISP';

    // Color coding
    if (dlEl && download) {
      dlEl.style.color = download > 100 ? '#38bdf8' : download > 50 ? '#fbbf24' : '#ef4444';
    }
    if (ulEl && upload) {
      ulEl.style.color = upload > 50 ? '#a78bfa' : upload > 20 ? '#fbbf24' : '#ef4444';
    }
  }

  _getState(entityId) {
    if (!this._hass || !entityId) return null;
    const state = this._hass.states[entityId];
    return state ? parseFloat(state.state) || state.state : null;
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
    if (this._hass) {
      this._hass.callService('ookla_speedtest', 'run_speedtest');
      const btn = this.querySelector('.test-btn');
      if (btn) {
        btn.textContent = 'Testing...';
        setTimeout(() => btn.textContent = 'Run Speed Test', 3000);
      }
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
          background: rgba(15, 23, 42, 0.6);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 24px;
          padding: 20px;
          color: #f8fafc;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          border: 1px solid rgba(255, 255, 255, 0.08);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2);
          width: 100%;
          height: 100%;
          min-height: 0;
          display: flex;
          flex-direction: column;
          justify-content: center;
          /* Ensure card fills available space in sections view */
          flex: 1;
        }
        .isp-text {
          font-size: 11px;
          color: #94a3b8;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          margin-bottom: 20px;
          font-weight: 600;
        }
        .speeds {
          display: flex;
          gap: 20px;
          margin-bottom: 20px;
        }
        .speed-block {
          flex: 1;
          cursor: pointer;
          transition: transform 0.2s;
        }
        .speed-block:hover {
          transform: translateY(-2px);
        }
        .speed-label {
          font-size: 10px;
          color: #94a3b8;
          text-transform: uppercase;
          letter-spacing: 1px;
          margin-bottom: 8px;
          display: flex;
          align-items: center;
          gap: 6px;
          font-weight: 600;
        }
        .speed-value {
          font-size: 36px;
          font-weight: 800;
          line-height: 1;
          transition: color 0.3s;
          letter-spacing: -1px;
        }
        .arrow-down { color: #38bdf8; }
        .arrow-up { color: #a78bfa; }
        .ping-row {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #94a3b8;
          margin-bottom: 24px;
          background: rgba(255,255,255,0.03);
          padding: 8px 16px;
          border-radius: 12px;
          width: fit-content;
          cursor: pointer;
          transition: background 0.2s;
        }
        .ping-row:hover {
          background: rgba(255,255,255,0.08);
        }
        .ping-value {
          color: #fbbf24;
          font-weight: 700;
        }
        .test-btn {
          width: 100%;
          padding: 14px;
          border: none;
          border-radius: 16px;
          background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
          color: white;
          font-size: 15px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
        }
        .test-btn:hover {
          opacity: 0.9;
          transform: translateY(-1px);
          box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
        }
        .test-btn:active {
          transform: translateY(0);
        }
      </style>
      
      <div class="card">
        <div class="isp-text">Internet Speed</div>
        
        <div class="speeds">
          <div class="speed-block speed-block-dl">
            <div class="speed-label">
              <span class="arrow-down">⬇</span> ${labels.download}
            </div>
            <div class="speed-value speed-download">--</div>
          </div>
          <div class="speed-block speed-block-ul">
            <div class="speed-label">
              <span class="arrow-up">⬆</span> ${labels.upload}
            </div>
            <div class="speed-value speed-upload">--</div>
          </div>
        </div>
        
        <div class="ping-row">
          <span>⚡</span> ${labels.ping}: <span class="ping-value">--</span>
        </div>
        
        <button class="test-btn">Run Speed Test</button>
      </div>
    `;

    this.querySelector('.test-btn')?.addEventListener('click', () => this._runTest());
    
    // Interactive elements
    const e = this._config.entities;
    this.querySelector('.speed-block-dl')?.addEventListener('click', () => this._showMoreInfo(e.download));
    this.querySelector('.speed-block-ul')?.addEventListener('click', () => this._showMoreInfo(e.upload));
    this.querySelector('.ping-row')?.addEventListener('click', () => this._showMoreInfo(e.ping));
  }
}

customElements.define("ookla-speedtest-minimal", OoklaSpeedtestMinimal);

class OoklaSpeedtestMinimalEditor extends HTMLElement {
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
    container.style.cssText = "display: flex; flex-direction: column; gap: 12px; padding: 10px;";

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
    container.appendChild(labelsDiv);

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

    entitiesDiv.appendChild(createPicker('download', 'Download Entity'));
    entitiesDiv.appendChild(createPicker('upload', 'Upload Entity'));
    entitiesDiv.appendChild(createPicker('ping', 'Ping Entity'));
    entitiesDiv.appendChild(createPicker('isp', 'ISP Entity'));
    
    container.appendChild(entitiesDiv);
    this.appendChild(container);
  }
}
customElements.define("ookla-speedtest-minimal-editor", OoklaSpeedtestMinimalEditor);


window.customCards = window.customCards || [];
window.customCards.push({
  type: "ookla-speedtest-minimal",
  name: "Ookla Speedtest - Minimal",
  description: "Clean minimal speedtest card with large typography",
  preview: true
});

console.info("%c OOKLA SPEEDTEST MINIMAL %c v1.4.3 ", "background: #00d2ff; color: #fff; font-weight: bold;", "background: #1e293b; color: #fff;");