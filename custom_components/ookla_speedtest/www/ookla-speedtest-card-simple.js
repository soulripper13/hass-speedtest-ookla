/**
 * Ookla Speedtest Card - Simplified Version
 * Basic working version to test setup
 */

class OoklaSpeedtestCardSimple extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
  }

  static getConfigElement() {
    return document.createElement("ookla-speedtest-card-simple-editor");
  }

  static getStubConfig() {
    return {
      type: "custom:ookla-speedtest-card-simple"
    };
  }

  setConfig(config) {
    this._config = config;
    this.render();
  }

  set hass(hass) {
    if (!this._hass && hass) {
      this._hass = hass;
      this.update();
    }
    this._hass = hass;
    this.update();
  }

  update() {
    if (!this._hass) return;
    
    const download = this._hass.states['sensor.ookla_speedtest_download'];
    const upload = this._hass.states['sensor.ookla_speedtest_upload'];
    const ping = this._hass.states['sensor.ookla_speedtest_ping'];
    
    const dlEl = this.querySelector('.dl');
    const ulEl = this.querySelector('.ul');
    const pingEl = this.querySelector('.ping');
    
    if (dlEl) dlEl.textContent = download ? download.state + ' Mbps' : '--';
    if (ulEl) ulEl.textContent = upload ? upload.state + ' Mbps' : '--';
    if (pingEl) pingEl.textContent = ping ? ping.state + ' ms' : '--';
  }

  render() {
    this.innerHTML = `
      <style>
        .card { 
          background: rgba(15, 23, 42, 0.6); 
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          color: white; 
          padding: 20px; 
          border-radius: 24px;
          font-family: sans-serif;
          border: 1px solid rgba(255, 255, 255, 0.08);
          direction: ltr;
        }
        .title { font-size: 18px; margin-bottom: 10px; font-weight: 700; }
        .row { display: flex; justify-content: space-between; margin: 10px 0; }
        .btn { 
          background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
          color: white; 
          border: none; 
          padding: 15px 30px; 
          border-radius: 30px;
          font-size: 16px;
          font-weight: 700;
          cursor: pointer;
          margin-top: 10px;
          width: 100%;
          transition: all 0.2s;
        }
        .btn:hover { opacity: 0.9; transform: scale(1.02); }
      </style>
      <div class="card">
        <div class="title">🌐 Speedtest</div>
        <div class="row"><span>⬇ Download:</span> <span class="dl">--</span></div>
        <div class="row"><span>⬆ Upload:</span> <span class="ul">--</span></div>
        <div class="row"><span>⏱ Ping:</span> <span class="ping">--</span></div>
        <button class="btn">GO</button>
      </div>
    `;
    
    const btn = this.querySelector('.btn');
    if (btn) {
      btn.addEventListener('click', () => {
        if (this._hass) {
          this._hass.callService('ookla_speedtest', 'run_speedtest');
          btn.textContent = 'Testing...';
          setTimeout(() => btn.textContent = 'GO', 3000);
        }
      });
    }
  }
}

customElements.define("ookla-speedtest-card-simple", OoklaSpeedtestCardSimple);

class OoklaSpeedtestCardSimpleEditor extends HTMLElement {
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
          <span class="info">This is a simplified test card. It uses default sensors automatically.</span>
        </div>
      `;
    }
  }
}
customElements.define("ookla-speedtest-card-simple-editor", OoklaSpeedtestCardSimpleEditor);


window.customCards = window.customCards || [];
window.customCards.push({
  type: "ookla-speedtest-card-simple",
  name: "Ookla Speedtest - Simple Test",
  description: "Simplified test version"
});

console.log("✅ Ookla Speedtest Simple Card loaded");
