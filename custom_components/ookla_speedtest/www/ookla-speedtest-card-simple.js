/**
 * Ookla Speedtest Card - Simplified Version
 * Basic working version to test setup
 *
 * Version: 1.4.0 - Improved masonry and sections layout compatibility
 *
 * Layout Compatibility:
 * - Masonry: Returns card size for proper column distribution
 * - Sections: Uses 4 columns x 3 rows grid by default
 * - Both layouts fully supported with proper height handling
 * - Added cache busting support
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
          color: white;
          padding: 16px;
          border-radius: 24px;
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
        .title { font-size: 18px; margin-bottom: 10px; font-weight: 700; }
        .row { 
          display: flex; 
          justify-content: space-between; 
          margin: 8px 0;
          gap: 10px;
        }
        .btn { 
          background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
          color: white; 
          border: none; 
          padding: 12px 30px; 
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
    
    container.appendChild(entitiesDiv);
    this.appendChild(container);
  }
}
customElements.define("ookla-speedtest-card-simple-editor", OoklaSpeedtestCardSimpleEditor);


window.customCards = window.customCards || [];
window.customCards.push({
  type: "ookla-speedtest-card-simple",
  name: "Ookla Speedtest - Simple Test",
  description: "Simplified test version"
});

console.info("%c OOKLA SPEEDTEST SIMPLE %c v1.4.3 ", "background: #0ea5e9; color: #fff; font-weight: bold;", "background: #1e293b; color: #fff;");
