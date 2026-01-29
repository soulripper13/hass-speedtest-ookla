/**
 * Ookla Speedtest Card - Minimal Version
 * A clean, simple speedtest card with large typography
 * 
 * Version: 1.1.4
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
    this.innerHTML = `
      <style>
        :host { display: block; }
        .card {
          background: rgba(15, 23, 42, 0.6);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 24px;
          padding: 24px;
          color: #f8fafc;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          border: 1px solid rgba(255, 255, 255, 0.08);
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
          gap: 24px;
          margin-bottom: 24px;
        }
        .speed-block {
          flex: 1;
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
          font-size: 42px;
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
        }
        .ping-value {
          color: #fbbf24;
          font-weight: 700;
        }
        .test-btn {
          width: 100%;
          padding: 16px;
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
          <div class="speed-block">
            <div class="speed-label">
              <span class="arrow-down">⬇</span> Download
            </div>
            <div class="speed-value speed-download">--</div>
          </div>
          <div class="speed-block">
            <div class="speed-label">
              <span class="arrow-up">⬆</span> Upload
            </div>
            <div class="speed-value speed-upload">--</div>
          </div>
        </div>
        
        <div class="ping-row">
          <span>⚡</span> Ping: <span class="ping-value">--</span>
        </div>
        
        <button class="test-btn">Run Speed Test</button>
      </div>
    `;

    this.querySelector('.test-btn')?.addEventListener('click', () => this._runTest());
  }
}

customElements.define("ookla-speedtest-minimal", OoklaSpeedtestMinimal);

class OoklaSpeedtestMinimalEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this.render();
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
    if (!this.innerHTML) {
      this.innerHTML = `
        <style>
          .card-config { display: flex; flex-direction: column; gap: 12px; padding: 8px; }
          .info { font-size: 14px; color: var(--secondary-text-color); }
        </style>
        <div class="card-config">
          <span class="info">Minimal card uses default sensors automatically. Configure entities in YAML if needed.</span>
        </div>
      `;
    }
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