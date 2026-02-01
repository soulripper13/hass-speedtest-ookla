/**
 * Ookla Speedtest Card - Dashboard Version
 * Full-featured dashboard card with mini charts and all metrics
 * 
 * Version: 1.2.5
 */

class OoklaSpeedtestDashboard extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
    this._history = { download: [], upload: [], ping: [] };
  }

  static getConfigElement() {
    return document.createElement("ookla-speedtest-dashboard-editor");
  }

  static getStubConfig() {
    return {
      type: "custom:ookla-speedtest-dashboard",
      entities: {
        // Default sensors
        download: "sensor.ookla_speedtest_download",
        upload: "sensor.ookla_speedtest_upload",
        ping: "sensor.ookla_speedtest_ping",
        jitter: "sensor.ookla_speedtest_jitter",
        grade: "sensor.ookla_speedtest_bufferbloat_grade",
        isp: "sensor.ookla_speedtest_isp",
        server: "sensor.ookla_speedtest_server",
        last_test: "sensor.ookla_speedtest_last_test",
        result_url: "sensor.ookla_speedtest_result_url",
        // Latency Metrics (Optional)
        ping_min: "sensor.ookla_speedtest_ping_low",
        ping_max: "sensor.ookla_speedtest_ping_high",
        dl_ping: "sensor.ookla_speedtest_ping_during_download",
        dl_ping_min: "sensor.ookla_speedtest_ping_low_during_download",
        dl_ping_max: "sensor.ookla_speedtest_ping_high_during_download",
        ul_ping: "sensor.ookla_speedtest_ping_during_upload",
        ul_ping_min: "sensor.ookla_speedtest_ping_low_during_upload",
        ul_ping_max: "sensor.ookla_speedtest_ping_high_during_upload",
        // Stability & Compliance (Optional)
        dl_compliance: "sensor.ookla_speedtest_download_percent",
        ul_compliance: "sensor.ookla_speedtest_upload_percent",
        dl_jitter: "sensor.ookla_speedtest_jitter_during_download",
        ul_jitter: "sensor.ookla_speedtest_jitter_during_upload"
      },
      show_charts: true,
      chart_points: 20
    };
  }

  setConfig(config) {
    this._config = { ...OoklaSpeedtestDashboard.getStubConfig(), ...config };
    // Merge entities individually to ensure defaults are preserved if keys are missing
    this._config.entities = { ...OoklaSpeedtestDashboard.getStubConfig().entities, ...config.entities };
  }

  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;
    
    if (hass && oldHass !== hass) {
      this._updateHistory();
      this.updateCard();
    }
  }

  connectedCallback() {
    this.render();
  }

  _updateHistory() {
    const e = this._config.entities;
    const download = parseFloat(this._getState(e.download)) || 0;
    const upload = parseFloat(this._getState(e.upload)) || 0;
    const ping = parseFloat(this._getState(e.ping)) || 0;

    this._history.download.push(download);
    this._history.upload.push(upload);
    this._history.ping.push(ping);

    const maxPoints = this._config.chart_points || 20;
    Object.keys(this._history).forEach(key => {
      if (this._history[key].length > maxPoints) {
        this._history[key] = this._history[key].slice(-maxPoints);
      }
    });
  }

  updateCard() {
    if (!this._hass) return;
    
    const e = this._config.entities;
    
    // Main Metrics
    this._updateMetricValue('.metric-dl', e.download, ' Mbps', true);
    this._updateMetricValue('.metric-ul', e.upload, ' Mbps', true);
    this._updateMetricValue('.metric-ping', e.ping, ' ms');
    this._updateMetricValue('.metric-jitter', e.jitter, ' ms');
    
    // Grade with color
    const gradeVal = this._getState(e.grade);
    const gradeEl = this.querySelector('.metric-grade .value');
    if (gradeEl && gradeVal) {
      const colors = { 'A+': '#22c55e', 'A': '#22c55e', 'B': '#84cc16', 'C': '#eab308' };
      const color = colors[gradeVal] || '#ef4444';
      gradeEl.innerHTML = `<span style="color:${color}">${gradeVal}</span>`;
    }

    // Optional Metrics
    const optionalFields = [
      { key: 'ping_min', suffix: ' ms' }, { key: 'ping_max', suffix: ' ms' },
      { key: 'dl_ping', suffix: ' ms' }, { key: 'dl_ping_min', suffix: ' ms' }, { key: 'dl_ping_max', suffix: ' ms' },
      { key: 'ul_ping', suffix: ' ms' }, { key: 'ul_ping_min', suffix: ' ms' }, { key: 'ul_ping_max', suffix: ' ms' },
      { key: 'dl_compliance', suffix: '%' }, { key: 'ul_compliance', suffix: '%' },
      { key: 'dl_jitter', suffix: ' ms' }, { key: 'ul_jitter', suffix: ' ms' }
    ];

    optionalFields.forEach(field => {
      const entityId = e[field.key];
      const el = this.querySelector(`.metric-${field.key.replace(/_/g, '-')}`);
      if (el) {
        const state = this._getState(entityId);
        const valueEl = el.querySelector('.value');
        if (valueEl) valueEl.textContent = (state !== null ? state : '--') + field.suffix;
        el.style.display = (entityId && this._hass.states[entityId]) ? 'block' : 'none';
      }
    });

    // ISP and server
    this.querySelector('.isp-name')?.setAttribute('data-text', this._getState(e.isp) || 'Unknown ISP');
    this.querySelector('.server-name')?.setAttribute('data-text', this._getState(e.server) || 'Unknown Server');
    
    // Last test
    const lastTestEl = this.querySelector('.last-test');
    if (lastTestEl) lastTestEl.textContent = this._formatTime(this._getState(e.last_test));

    // Result link
    const resultUrl = this._getState(e.result_url);
    const linkEl = this.querySelector('.result-link');
    if (linkEl) {
      if (resultUrl && resultUrl.startsWith('http')) {
        linkEl.href = resultUrl;
        linkEl.style.display = 'inline-flex';
      } else {
        linkEl.style.display = 'none';
      }
    }

    this._drawCharts();
  }

  _updateMetricValue(selector, entityId, suffix = '', round = false) {
    const el = this.querySelector(selector + ' .value');
    if (!el) return;
    let val = this._getState(entityId);
    if (val !== null) {
      if (round) val = Math.round(parseFloat(val));
      el.setAttribute('data-val', val + suffix);
    } else {
      el.setAttribute('data-val', '--' + suffix);
    }
  }

  _drawCharts() {
    ['download', 'upload', 'ping'].forEach(type => {
      const svg = this.querySelector(`.chart-${type} svg`);
      if (!svg || this._history[type].length < 2) return;

      const data = this._history[type];
      const max = Math.max(...data, 1);
      const min = Math.min(...data);
      const range = max - min || 1;
      const width = 100;
      const height = 40;
      
      const points = data.map((val, i) => {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((val - min) / range) * height;
        return [x, y];
      });

      const areaPoints = [[0, height], ...points, [width, height]].map(p => `${p[0]},${p[1]}`).join(' ');
      const linePoints = points.map(p => `${p[0]},${p[1]}`).join(' ');

      const colors = { download: ['#0ea5e9', '#22d3ee'], upload: ['#7c3aed', '#a78bfa'], ping: ['#f59e0b', '#fbbf24'] };
      const [stroke] = colors[type] || ['#ccc', '#eee'];

      svg.innerHTML = `
        <defs>
          <linearGradient id="grad-${type}" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:${stroke};stop-opacity:0.5" />
            <stop offset="100%" style="stop-color:${stroke};stop-opacity:0" />
          </linearGradient>
        </defs>
        <polygon points="${areaPoints}" fill="url(#grad-${type})" />
        <polyline points="${linePoints}" fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      `;
    });
  }

  _getState(entityId) {
    if (!this._hass || !entityId) return null;
    const state = this._hass.states[entityId];
    return state ? state.state : null;
  }

  _formatTime(dateStr) {
    if (!dateStr || dateStr === 'unknown' || dateStr === 'unavailable') return 'Never tested';
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diff = Math.floor((now - date) / 1000);
      if (diff < 60) return 'Just now';
      if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
      if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
      return date.toLocaleDateString();
    } catch { return dateStr; }
  }

  _showMoreInfo(entityId) {
    if (!entityId) return;
    const event = new CustomEvent('hass-more-info', { bubbles: true, composed: true, detail: { entityId } });
    this.dispatchEvent(event);
  }

  render() {
    const e = this._config.entities;
    this.innerHTML = `
      <style>
        :host { display: block; }
        .card {
          background: rgba(15, 23, 42, 0.6);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 24px;
          padding: 20px;
          border: 1px solid rgba(255, 255, 255, 0.08);
          color: #f8fafc;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          direction: ltr;
        }
        .header { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-start; }
        .isp-name { font-size: 18px; font-weight: 700; margin-bottom: 4px; color: #f8fafc; }
        .isp-name::before { content: attr(data-text); }
        .server-name { font-size: 12px; color: #94a3b8; display: flex; align-items: center; gap: 6px; }
        .server-name::before { content: attr(data-text); }
        
        .metrics-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 20px; }
        .metric {
          background: rgba(255,255,255,0.03);
          border-radius: 12px;
          padding: 10px 5px;
          text-align: center;
          border: 1px solid rgba(255,255,255,0.02);
          cursor: pointer;
          transition: all 0.2s;
        }
        .metric:hover { transform: translateY(-2px); background: rgba(255,255,255,0.05); }
        .metric .label { font-size: 9px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 600; }
        .metric .value { font-size: 16px; font-weight: 700; line-height: 1; }
        .metric .value::before { content: attr(data-val); }
        
        .optional-grid { 
          display: grid; 
          grid-template-columns: repeat(4, 1fr); 
          gap: 8px; 
          margin-bottom: 20px;
          border-top: 1px solid rgba(255,255,255,0.05);
          padding-top: 15px;
        }
        .optional-grid .metric { padding: 8px 4px; }
        .optional-grid .metric .value { font-size: 13px; }

        .metric-dl .value { color: #38bdf8; }
        .metric-ul .value { color: #a78bfa; }
        .metric-ping .value { color: #fbbf24; }
        .metric-jitter .value { color: #f472b6; }
        
        .charts-section { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
        .chart-box { background: rgba(15, 23, 42, 0.4); border-radius: 16px; padding: 12px; border: 1px solid rgba(255,255,255,0.03); cursor: pointer; }
        .chart-title { font-size: 10px; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; font-weight: 600; }
        .chart-box svg { width: 100%; height: 40px; overflow: visible; }
        
        .footer { display: flex; align-items: center; justify-content: space-between; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); }
        .last-test { font-size: 11px; color: #64748b; }
        .run-btn {
          padding: 6px 15px; border: none; border-radius: 20px;
          background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
          color: white; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s;
        }
        .run-btn.running { background: #10b981; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
        .result-link { color: #38bdf8; text-decoration: none; font-size: 11px; }
        
        @media (max-width: 600px) {
          .metrics-grid { grid-template-columns: repeat(3, 1fr); }
          .optional-grid { grid-template-columns: repeat(2, 1fr); }
          .charts-section { grid-template-columns: 1fr; }
        }
      </style>
      
      <div class="card">
        <div class="header">
          <div class="isp-info">
            <div class="isp-name" data-text="Loading..."></div>
            <div class="server-name" data-text="-"></div>
          </div>
          <a href="#" class="result-link" target="_blank" rel="noopener" style="display:none;">View Results ↗</a>
        </div>
        
        <div class="metrics-grid">
          <div class="metric metric-dl" id="m-dl"><div class="label">Download</div><div class="value"></div></div>
          <div class="metric metric-ul" id="m-ul"><div class="label">Upload</div><div class="value"></div></div>
          <div class="metric metric-ping" id="m-ping"><div class="label">Ping</div><div class="value"></div></div>
          <div class="metric metric-jitter" id="m-jitter"><div class="label">Jitter</div><div class="value"></div></div>
          <div class="metric metric-grade" id="m-grade"><div class="label">Grade</div><div class="value">-</div></div>
        </div>

        <div class="optional-grid" id="opt-grid">
          <div class="metric metric-ping-min" id="m-pmin"><div class="label">Ping Min</div><div class="value"></div></div>
          <div class="metric metric-ping-max" id="m-pmax"><div class="label">Ping Max</div><div class="value"></div></div>
          <div class="metric metric-dl-ping" id="m-dlp"><div class="label">DL Ping</div><div class="value"></div></div>
          <div class="metric metric-dl-jitter" id="m-dlj"><div class="label">DL Jitter</div><div class="value"></div></div>
          <div class="metric metric-ul-ping" id="m-ulp"><div class="label">UL Ping</div><div class="value"></div></div>
          <div class="metric metric-ul-jitter" id="m-ulj"><div class="label">UL Jitter</div><div class="value"></div></div>
          <div class="metric metric-dl-compliance" id="m-dlc"><div class="label">DL Plan</div><div class="value"></div></div>
          <div class="metric metric-ul-compliance" id="m-ulc"><div class="label">UL Plan</div><div class="value"></div></div>
        </div>
        
        <div class="charts-section">
          <div class="chart-box chart-download" id="c-dl"><div class="chart-title">Download</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"></svg></div>
          <div class="chart-box chart-upload" id="c-ul"><div class="chart-title">Upload</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"></svg></div>
          <div class="chart-box chart-ping" id="c-ping"><div class="chart-title">Ping</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"></svg></div>
        </div>
        
        <div class="footer">
          <span class="last-test">Never tested</span>
          <button class="run-btn" id="run">▶ Run Test</button>
        </div>
      </div>
    `;

    // Event Listeners
    const clickMap = {
      '#m-dl': e.download, '#m-ul': e.upload, '#m-ping': e.ping, '#m-jitter': e.jitter, '#m-grade': e.grade,
      '#m-pmin': e.ping_min, '#m-pmax': e.ping_max, '#m-dlp': e.dl_ping, '#m-dlj': e.dl_jitter,
      '#m-ulp': e.ul_ping, '#m-ulj': e.ul_jitter, '#m-dlc': e.dl_compliance, '#m-ulc': e.ul_compliance,
      '#c-dl': e.download, '#c-ul': e.upload, '#c-ping': e.ping, '#run': null
    };

    Object.entries(clickMap).forEach(([id, ent]) => {
      const el = this.querySelector(id);
      if (!el) return;
      if (id === '#run') el.onclick = () => {
        this._hass.callService('ookla_speedtest', 'run_speedtest');
        el.classList.add('running');
        setTimeout(() => el.classList.remove('running'), 5000);
      };
      else el.onclick = () => this._showMoreInfo(ent);
    });
  }
}

customElements.define("ookla-speedtest-dashboard", OoklaSpeedtestDashboard);

class OoklaSpeedtestDashboardEditor extends HTMLElement {
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
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: newConfig }, bubbles: true, composed: true }));
  }

  render() {
    if (this._elements) return;

    this.innerHTML = '';
    this._elements = [];

    const container = document.createElement('div');
    container.style.cssText = "display: flex; flex-direction: column; gap: 12px; padding: 10px; font-family: sans-serif;";

    // General Section
    const genDiv = document.createElement('div');
    genDiv.style.cssText = "border: 1px solid var(--divider-color, #444); border-radius: 8px; padding: 10px; background: var(--card-background-color, #222);";
    genDiv.innerHTML = `<div style="font-weight: bold; margin-bottom: 10px; color: var(--primary-color, #0ea5e9); font-size: 13px; text-transform: uppercase;">General Settings</div>`;
    
    const chartOption = document.createElement('div');
    chartOption.style.cssText = "display: flex; align-items: center; justify-content: space-between;";
    chartOption.innerHTML = `<label style="font-size: 12px; color: var(--secondary-text-color, #ccc);">Chart Points</label>`;
    const chartInput = document.createElement('input');
    chartInput.type = "number";
    chartInput.value = this._config.chart_points || 20;
    chartInput.style.cssText = "padding: 6px; border-radius: 4px; border: 1px solid var(--divider-color, #444); background: var(--card-background-color, #111); color: var(--primary-text-color, #fff); width: 60px;";
    chartInput.addEventListener('change', (e) => this.configChanged({ ...this._config, chart_points: Number(e.target.value) }));
    chartOption.appendChild(chartInput);
    genDiv.appendChild(chartOption);
    container.appendChild(genDiv);

    // Helpers
    const createSection = (title, items) => {
      const secDiv = document.createElement('div');
      secDiv.style.cssText = "border: 1px solid var(--divider-color, #444); border-radius: 8px; padding: 10px; background: var(--card-background-color, #222); margin-top: 10px;";
      secDiv.innerHTML = `<div style="font-weight: bold; margin-bottom: 10px; color: var(--primary-color, #0ea5e9); font-size: 13px; text-transform: uppercase;">${title}</div>`;
      
      items.forEach(item => {
        const option = document.createElement('div');
        option.style.marginBottom = "12px";
        const label = document.createElement('label');
        label.innerText = item.label;
        label.style.cssText = "font-size: 12px; color: var(--secondary-text-color, #ccc); margin-bottom: 4px; display: block;";
        option.appendChild(label);

        const picker = document.createElement('ha-entity-picker');
        picker.hass = this._hass;
        picker.value = (this._config.entities && this._config.entities[item.key]) || '';
        picker.includeDomains = ['sensor'];
        picker.allowCustomEntity = true;
        picker.addEventListener('value-changed', (e) => {
          const entities = { ...(this._config.entities || {}) };
          entities[item.key] = e.detail.value;
          this.configChanged({ ...this._config, entities });
        });
        
        // Add to elements tracker for hass updates
        this._elements.push(picker);
        option.appendChild(picker);
        secDiv.appendChild(option);
      });
      return secDiv;
    };

    container.appendChild(createSection("Core Entities", [
      { key: 'download', label: 'Download' },
      { key: 'upload', label: 'Upload' },
      { key: 'ping', label: 'Ping' },
      { key: 'jitter', label: 'Jitter' },
      { key: 'grade', label: 'Grade' }
    ]));

    container.appendChild(createSection("Extended Latency", [
      { key: 'ping_min', label: 'Ping Min' },
      { key: 'ping_max', label: 'Ping Max' },
      { key: 'dl_ping', label: 'DL Ping' },
      { key: 'ul_ping', label: 'UL Ping' }
    ]));

    container.appendChild(createSection("Stability & Compliance", [
      { key: 'dl_compliance', label: 'DL Plan %' },
      { key: 'ul_compliance', label: 'UL Plan %' },
      { key: 'dl_jitter', label: 'DL Jitter' },
      { key: 'ul_jitter', label: 'UL Jitter' }
    ]));

    this.appendChild(container);
  }
}
customElements.define("ookla-speedtest-dashboard-editor", OoklaSpeedtestDashboardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "ookla-speedtest-dashboard",
  name: "Ookla Speedtest - Dashboard",
  description: "Advanced dashboard with 20+ sensors and history tracking",
  preview: true
});
