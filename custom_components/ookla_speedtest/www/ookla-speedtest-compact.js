/**
 * Ookla Speedtest Card - Compact Version
 * Small footprint card perfect for side panels
 * 
 * Version: 1.2.5
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

  updateCard() {
    if (!this._hass) return;
    
    const e = this._config.entities;
    const dl = this._getState(e.download);
    const ul = this._getState(e.upload);
    const ping = this._getState(e.ping);

    this.querySelector('.dl-value')?.setAttribute('data-value', dl ? Math.round(dl) : '--');
    this.querySelector('.ul-value')?.setAttribute('data-value', ul ? Math.round(ul) : '--');
    this.querySelector('.ping-value')?.setAttribute('data-value', ping ? Math.round(ping) : '--');
  }

  _getState(entityId) {
    if (!this._hass || !entityId) return null;
    const state = this._hass.states[entityId];
    return state ? parseFloat(state.state) || null : null;
  }

  _runTest() {
    this._hass?.callService('ookla_speedtest', 'run_speedtest');
    const btn = this.querySelector('.go-btn');
    if (btn) {
      btn.classList.add('running');
      setTimeout(() => btn.classList.remove('running'), 5000);
    }
  }

  render() {
    this.innerHTML = `
      <style>
        :host { display: block; }
        .card {
          background: rgba(15, 23, 42, 0.6);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 16px;
          padding: 12px 16px;
          color: #f8fafc;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          display: flex;
          flex-direction: row;
          align-items: center;
          justify-content: space-between;
          border: 1px solid rgba(255, 255, 255, 0.08);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          flex: 1;
          text-align: left;
        }
        .title {
          font-size: 11px;
          font-weight: 600;
          color: #94a3b8;
          text-transform: uppercase;
          letter-spacing: 1px;
        }
        .stats {
          display: flex;
          gap: 12px;
          align-items: baseline;
        }
        .stat {
          display: flex;
          align-items: baseline;
          gap: 2px;
        }
        .stat-dl { color: #38bdf8; }
        .stat-ul { color: #a78bfa; }
        .stat-ping { color: #fbbf24; }
        .stat::before {
          content: attr(data-value);
          font-weight: 700;
          color: #f8fafc;
          font-size: 16px;
          line-height: 1;
        }
        .unit {
          font-size: 10px;
          font-weight: 500;
          opacity: 0.6;
          text-transform: lowercase;
        }
        .go-btn {
          width: 42px;
          height: 42px;
          border-radius: 50%;
          border: 2px solid rgba(255,255,255,0.1);
          background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
          color: white;
          font-size: 10px;
          font-weight: 900;
          cursor: pointer;
          box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3);
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          flex-shrink: 0;
          margin-left: 12px;
        }
        .go-btn:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 14px rgba(14, 165, 233, 0.4);
          background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
        }
        .go-btn.running {
          animation: pulse 1.5s infinite;
          background: #10b981;
          border-color: rgba(255,255,255,0.2);
        }
        @keyframes pulse { 
          0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); } 
          70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); } 
          100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } 
        }
      </style>
      
      <div class="card">
        <div class="info">
          <div class="title">Internet Speed</div>
          <div class="stats">
            <div class="stat stat-dl dl-value" data-value="--"><span class="unit">mbps</span></div>
            <div class="stat stat-ul ul-value" data-value="--"><span class="unit">mbps</span></div>
            <div class="stat stat-ping ping-value" data-value="--"><span class="unit">ms</span></div>
          </div>
        </div>
        <button class="go-btn">GO</button>
      </div>
    `;

    this.querySelector('.go-btn')?.addEventListener('click', () => this._runTest());
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
  name: "Ookla Speedtest - Compact",
  description: "Compact card for side panels and crowded dashboards",
  preview: true
});
