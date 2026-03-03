/**
 * Ookla Speedtest Card - Dashboard Version
 * Full-featured dashboard card with configurable gauges and charts
 *
 * Version: 1.4.0 - Improved masonry and sections layout compatibility
 *
 * Layout Compatibility:
 * - Masonry: Returns card size for proper column distribution
 * - Sections: Uses 6 columns x 6 rows grid by default
 * - Both layouts fully supported with proper height handling
 * - Added cache busting support
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
        ping_min: "sensor.ookla_speedtest_ping_min",
        ping_max: "sensor.ookla_speedtest_ping_max",
        dl_ping: "sensor.ookla_speedtest_download_ping",
        dl_ping_min: "sensor.ookla_speedtest_download_ping_min",
        dl_ping_max: "sensor.ookla_speedtest_download_ping_max",
        ul_ping: "sensor.ookla_speedtest_upload_ping",
        ul_ping_min: "sensor.ookla_speedtest_upload_ping_min",
        ul_ping_max: "sensor.ookla_speedtest_upload_ping_max",
        // Stability & Compliance (Optional)
        dl_compliance: "sensor.ookla_speedtest_download_plan_compliance",
        ul_compliance: "sensor.ookla_speedtest_upload_plan_compliance",
        dl_jitter: "sensor.ookla_speedtest_download_jitter",
        ul_jitter: "sensor.ookla_speedtest_upload_jitter"
      },
      labels: {
        download: "Download",
        upload: "Upload",
        ping: "Ping",
        jitter: "Jitter",
        grade: "Grade"
      },
      show_gauges: true,
      show_charts: true,
      history_hours: 168,  // 7 days (24 * 7)
      max_download: 1000,
      max_upload: 500
    };
  }

  setConfig(config) {
    // Merge config but don't force stub defaults for entities
    const stubConfig = OoklaSpeedtestDashboard.getStubConfig();
    this._config = { ...stubConfig, ...config };

    // Only use stub entities if user hasn't provided any entities at all
    if (!config.entities) {
      this._config.entities = stubConfig.entities;
    } else {
      // Use only the entities the user explicitly configured
      this._config.entities = config.entities;
    }
  }

  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;

    if (hass && oldHass !== hass) {
      this.updateCard();
      // Fetch history data periodically (every 5 minutes)
      if (!this._historyUpdateInterval) {
        this._fetchHistory();
        this._historyUpdateInterval = setInterval(() => this._fetchHistory(), 5 * 60 * 1000);
      }
    }
  }

  connectedCallback() {
    this.render();
    // Fetch history immediately if hass is already available
    if (this._hass && this._config.show_charts) {
      this._fetchHistory();
    }
  }

  /**
   * Card size for Masonry view (1 = 50px)
   * This helps masonry layout calculate proper column distribution
   * Adjust size based on enabled features
   */
  getCardSize() {
    let size = 10; // Base size for metrics and footer
    if (this._config.show_gauges) size += 3; // Add space for gauges
    if (this._config.show_charts) size += 4; // Add space for charts
    return size;
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

  async _fetchHistory() {
    if (!this._hass || !this._config.show_charts) return;

    const e = this._config.entities;
    const entities = [e.download, e.upload, e.ping].filter(id => id);

    if (entities.length === 0) return;

    const hours = this._config.history_hours || 168; // Default 7 days
    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - hours * 60 * 60 * 1000);

    try {
      const history = await this._hass.callWS({
        type: 'history/history_during_period',
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        entity_ids: entities,
        minimal_response: true,
        significant_changes_only: false
      });

      console.log('History response:', history);

      // Process history data
      this._history = { download: [], upload: [], ping: [] };

      if (history) {
        // History is an object with entity_id as keys
        entities.forEach((entityId) => {
          const entityHistory = history[entityId];  // Access by entity ID key
          let key = null;

          if (entityId === e.download) key = 'download';
          else if (entityId === e.upload) key = 'upload';
          else if (entityId === e.ping) key = 'ping';

          if (key && entityHistory && Array.isArray(entityHistory)) {
            entityHistory.forEach(state => {
              // Handle both minimal and full response formats
              const value = parseFloat(state.s || state.state);
              if (!isNaN(value) && value >= 0) {
                this._history[key].push(value);
              }
            });
          }
        });

        console.log('Processed history:', this._history);

        // Sample data if too many points (keep max 100 points for smooth rendering)
        Object.keys(this._history).forEach(key => {
          const data = this._history[key];
          if (data.length > 100) {
            const step = Math.ceil(data.length / 100);
            this._history[key] = data.filter((_, i) => i % step === 0);
          }
        });

        console.log('Sampled history:', this._history);
      }

      if (this._config.show_charts) {
        this._drawCharts();
      }
    } catch (error) {
      console.error('Failed to fetch history:', error);
      // Fallback to current values if history fetch fails
      this._history = {
        download: [parseFloat(this._getState(e.download)) || 0],
        upload: [parseFloat(this._getState(e.upload)) || 0],
        ping: [parseFloat(this._getState(e.ping)) || 0]
      };
      if (this._config.show_charts) {
        this._drawCharts();
      }
    }
  }

  disconnectedCallback() {
    if (this._historyUpdateInterval) {
      clearInterval(this._historyUpdateInterval);
      this._historyUpdateInterval = null;
    }
  }

  updateCard() {
    if (!this._hass) return;

    const e = this._config.entities;

    // Main Metrics
    this._updateMetricValue('.metric-dl', e.download, ' Mbps', true);
    this._updateMetricValue('.metric-ul', e.upload, ' Mbps', true);
    this._updateMetricValue('.metric-ping', e.ping, ' ms');
    this._updateMetricValue('.metric-jitter', e.jitter, ' ms');

    // Update gauges if enabled
    if (this._config.show_gauges) {
      const download = parseFloat(this._getState(e.download)) || 0;
      const upload = parseFloat(this._getState(e.upload)) || 0;
      this._updateGauge('download', download, this._config.max_download);
      this._updateGauge('upload', upload, this._config.max_upload);
    }

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

    if (this._config.show_charts) {
      this._drawCharts();
    }
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

  _drawCharts() {
    if (!this._config.show_charts) return;

    ['download', 'upload', 'ping'].forEach(type => {
      const svg = this.querySelector(`.chart-${type} svg`);
      if (!svg) return;

      const data = this._history[type] || [];

      // Need at least 1 data point to draw
      if (data.length === 0) {
        svg.innerHTML = '<text x="50" y="20" text-anchor="middle" fill="#64748b" font-size="8">No data</text>';
        return;
      }

      // If only 1 point, duplicate it to draw a line
      const chartData = data.length === 1 ? [data[0], data[0]] : data;

      const max = Math.max(...chartData, 1);
      const min = Math.min(...chartData);
      const range = max - min || 1;
      const width = 100;
      const height = 40;

      const points = chartData.map((val, i) => {
        const x = (i / (chartData.length - 1)) * width;
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
      const labels = this._config.labels || { download: 'Download', upload: 'Upload', ping: 'Ping', jitter: 'Jitter', grade: 'Grade' };
      
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
            padding: 12px;
            padding-left: max(12px, env(safe-area-inset-left));
            padding-right: max(12px, env(safe-area-inset-right));
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2);
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            width: 100%;
            height: 100%;
            min-height: 0;
            display: flex;
            flex-direction: column;
            overflow: auto;
            /* Ensure card fills available space in sections view */
            flex: 1;
            direction: ltr;
          }
          .header { margin-bottom: 10px; display: flex; justify-content: space-between; align-items: flex-start; flex-shrink: 0; }
          .isp-name { font-size: 18px; font-weight: 700; margin-bottom: 4px; color: #f8fafc; }
          .isp-name::before { content: attr(data-text); }
          .server-name { font-size: 12px; color: #94a3b8; display: flex; align-items: center; gap: 6px; }
          .server-name::before { content: attr(data-text); }
          
          .metrics-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            margin-bottom: 10px;
            flex-shrink: 0;
          }
          .metric {
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 8px 4px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.02);
            cursor: pointer;
            transition: all 0.2s;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
          }
          .metric:hover { transform: translateY(-2px); background: rgba(255,255,255,0.05); }
          .metric:active { transform: translateY(0); background: rgba(255,255,255,0.07); }
          .metric .label { font-size: 9px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 600; }
          .metric .value { font-size: 16px; font-weight: 700; line-height: 1; }
          .metric .value::before { content: attr(data-val); }
  
          .optional-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 6px;
            margin-bottom: 10px;
            border-top: 1px solid rgba(255,255,255,0.05);
            padding-top: 10px;
            flex-shrink: 0;
          }
          .optional-grid .metric { padding: 6px 4px; }
          .optional-grid .metric .value { font-size: 12px; }
  
          .metric-dl .value { color: #38bdf8; }
          .metric-ul .value { color: #a78bfa; }
          .metric-ping .value { color: #fbbf24; }
          .metric-jitter .value { color: #f472b6; }
  
          /* Gauge Styles */
          .gauges-container {
            display: flex;
            justify-content: center;
            gap: 16px;
            margin: 10px 0;
            flex-shrink: 0;
          }
  
          .gauge {
            position: relative;
            width: 110px;
            height: 110px;
            flex-shrink: 0;
          }
  
          .gauge-svg {
            transform: rotate(135deg);
            width: 100%;
            height: 100%;
          }
  
          .gauge-bg {
            fill: none;
            stroke: rgba(255,255,255,0.05);
            stroke-width: 10;
            stroke-linecap: round;
            stroke-dasharray: 424 566;
            stroke-dashoffset: 0;
          }
  
          .gauge-fill {
            fill: none;
            stroke-width: 10;
            stroke-linecap: round;
            stroke-dasharray: 424 566;
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
            font-size: 9px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
            font-weight: 600;
          }
  
          .gauge-value {
            font-size: 24px;
            font-weight: 800;
            color: #fff;
            line-height: 1;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.3);
          }
  
          .gauge-unit {
            font-size: 9px;
            color: #64748b;
            margin-top: 2px;
            font-weight: 500;
          }
  
          .charts-section {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 10px;
            flex-shrink: 0;
            min-height: 100px;
          }
          .chart-box {
            background: rgba(15, 23, 42, 0.4);
            border-radius: 16px;
            padding: 8px;
            border: 1px solid rgba(255,255,255,0.03);
            cursor: pointer;
            display: flex;
            flex-direction: column;
            min-height: 90px;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
            transition: all 0.2s;
          }
          .chart-box:hover { background: rgba(15, 23, 42, 0.5); }
          .chart-box:active { transform: scale(0.98); background: rgba(15, 23, 42, 0.6); }
          .chart-title { font-size: 10px; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px; font-weight: 600; }
          .chart-box svg { width: 100%; height: 70px; overflow: visible; }
          
          .footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.05);
            flex-shrink: 0;
          }
          .last-test { font-size: 11px; color: #64748b; }
          .run-btn {
            padding: 6px 15px; border: none; border-radius: 20px;
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            color: white; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s;
            min-height: 32px;
            min-width: 80px;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
          }
          .run-btn:active { transform: scale(0.95); }
          .run-btn.running { background: #10b981; animation: pulse 1.5s infinite; }
          @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
          .result-link {
            color: #38bdf8; text-decoration: none; font-size: 11px;
            min-height: 32px;
            display: inline-flex;
            align-items: center;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
          }
          .result-link:active { transform: scale(0.95); }
  
          /* Container query responsive adjustments */
          @container (max-width: 500px) {
            .card { padding: 14px; }
            .isp-name { font-size: 16px; }
            .server-name { font-size: 11px; }
            .metrics-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; }
            .metric .label { font-size: 8px; }
            .metric .value { font-size: 14px; }
            .optional-grid { grid-template-columns: repeat(3, 1fr); gap: 6px; }
            .optional-grid .metric { padding: 6px 3px; }
            .optional-grid .metric .value { font-size: 11px; }
            .optional-grid .metric .label { font-size: 7px; }
            .gauge { width: 110px; height: 110px; }
            .gauge-value { font-size: 22px; }
            .gauge-label { font-size: 8px; }
            .gauge-unit { font-size: 8px; }
            .charts-section { grid-template-columns: 1fr; gap: 8px; }
            .chart-title { font-size: 9px; }
          }
  
          @container (max-width: 400px) {
            .card { padding: 12px; border-radius: 20px; }
            .header { margin-bottom: 10px; }
            .isp-name { font-size: 15px; }
            .server-name { font-size: 10px; }
            .metrics-grid { grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 10px; }
            .metric { padding: 8px 4px; border-radius: 10px; }
            .metric .label { font-size: 7px; letter-spacing: 0.3px; }
            .metric .value { font-size: 13px; }
            .optional-grid { grid-template-columns: repeat(3, 1fr); gap: 5px; padding-top: 10px; margin-bottom: 10px; }
            .optional-grid .metric { padding: 5px 3px; }
            .optional-grid .metric .value { font-size: 10px; }
            .optional-grid .metric .label { font-size: 7px; }
            .gauges-container { gap: 10px; margin: 12px 0; }
            .gauge { width: 100px; height: 100px; }
            .gauge-value { font-size: 20px; }
            .gauge-label { font-size: 7px; letter-spacing: 0.5px; }
            .gauge-unit { font-size: 7px; }
            .gauge-bg, .gauge-fill { stroke-width: 9; }
            .charts-section { margin-bottom: 10px; }
            .chart-box { padding: 8px; border-radius: 12px; }
            .chart-title { font-size: 8px; margin-bottom: 6px; }
            .footer { padding-top: 10px; flex-direction: column; gap: 8px; align-items: flex-start; }
            .last-test { font-size: 10px; }
            .run-btn { font-size: 11px; padding: 5px 12px; align-self: stretch; text-align: center; }
            .result-link { font-size: 10px; padding: 5px 10px; }
          }
  
          @container (max-width: 320px) {
            .card { padding: 10px; border-radius: 16px; }
            .isp-name { font-size: 14px; }
            .server-name { font-size: 9px; }
            .metrics-grid { grid-template-columns: repeat(2, 1fr); gap: 5px; }
            .metric { padding: 6px 3px; }
            .metric .label { font-size: 7px; }
            .metric .value { font-size: 12px; }
            .optional-grid { grid-template-columns: repeat(2, 1fr); gap: 4px; }
            .optional-grid .metric { padding: 4px 2px; }
            .optional-grid .metric .value { font-size: 9px; }
            .optional-grid .metric .label { font-size: 6px; }
            .gauges-container { flex-direction: column; gap: 8px; margin: 10px 0; }
            .gauge { width: 90px; height: 90px; }
            .gauge-value { font-size: 18px; }
            .gauge-label { font-size: 7px; }
            .gauge-unit { font-size: 7px; }
            .gauge-bg, .gauge-fill { stroke-width: 8; }
            .chart-box { padding: 6px; }
            .chart-title { font-size: 7px; }
            .footer { gap: 6px; }
            .last-test { font-size: 9px; }
            .run-btn { font-size: 10px; padding: 4px 10px; border-radius: 16px; }
          }
  
          @container (max-width: 280px) {
            .card { padding: 8px; }
            .header { margin-bottom: 8px; }
            .metrics-grid { gap: 4px; margin-bottom: 8px; }
            .optional-grid { gap: 3px; margin-bottom: 8px; padding-top: 8px; }
            .gauges-container { margin: 8px 0; }
            .gauge { width: 80px; height: 80px; }
            .gauge-value { font-size: 16px; }
            .gauge-label { font-size: 6px; }
            .gauge-unit { font-size: 6px; }
            .charts-section { gap: 6px; margin-bottom: 8px; }
            .footer { padding-top: 8px; }
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
            <div class="metric metric-dl" id="m-dl"><div class="label">${labels.download}</div><div class="value"></div></div>
            <div class="metric metric-ul" id="m-ul"><div class="label">${labels.upload}</div><div class="value"></div></div>
            <div class="metric metric-ping" id="m-ping"><div class="label">${labels.ping}</div><div class="value"></div></div>
            <div class="metric metric-jitter" id="m-jitter"><div class="label">${labels.jitter}</div><div class="value"></div></div>
            <div class="metric metric-grade" id="m-grade"><div class="label">${labels.grade}</div><div class="value">-</div></div>
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

        ${this._config.show_gauges ? `
        <div class="gauges-container">
          <div class="gauge gauge-download">
            <svg class="gauge-svg" viewBox="0 0 200 200">
              <defs>
                <linearGradient id="grad-download-dash" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#0ea5e9;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#22d3ee;stop-opacity:1" />
                </linearGradient>
              </defs>
              <circle class="gauge-bg" cx="100" cy="100" r="90"></circle>
              <circle class="gauge-fill" cx="100" cy="100" r="90" stroke="url(#grad-download-dash)"></circle>
            </svg>
            <div class="gauge-content">
              <div class="gauge-label">${labels.download}</div>
              <div class="gauge-value">0</div>
              <div class="gauge-unit">Mbps</div>
            </div>
          </div>

          <div class="gauge gauge-upload">
            <svg class="gauge-svg" viewBox="0 0 200 200">
              <defs>
                <linearGradient id="grad-upload-dash" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#a78bfa;stop-opacity:1" />
                </linearGradient>
              </defs>
              <circle class="gauge-bg" cx="100" cy="100" r="90"></circle>
              <circle class="gauge-fill" cx="100" cy="100" r="90" stroke="url(#grad-upload-dash)"></circle>
            </svg>
            <div class="gauge-content">
              <div class="gauge-label">${labels.upload}</div>
              <div class="gauge-value">0</div>
              <div class="gauge-unit">Mbps</div>
            </div>
          </div>
        </div>
        ` : ''}

        ${this._config.show_charts ? `
        <div class="charts-section">
          <div class="chart-box chart-download" id="c-dl"><div class="chart-title">${labels.download}</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"></svg></div>
          <div class="chart-box chart-upload" id="c-ul"><div class="chart-title">${labels.upload}</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"></svg></div>
          <div class="chart-box chart-ping" id="c-ping"><div class="chart-title">${labels.ping}</div><svg viewBox="0 0 100 40" preserveAspectRatio="none"></svg></div>
        </div>
        ` : ''}
        
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

    // Show Gauges Toggle
    const gaugesToggle = document.createElement('div');
    gaugesToggle.style.cssText = "display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;";
    gaugesToggle.innerHTML = `<label style="font-size: 12px; color: var(--secondary-text-color, #ccc);">Show Gauges</label>`;
    const gaugesCheckbox = document.createElement('input');
    gaugesCheckbox.type = "checkbox";
    gaugesCheckbox.checked = this._config.show_gauges !== false;
    gaugesCheckbox.style.cssText = "width: 20px; height: 20px; cursor: pointer;";
    gaugesCheckbox.addEventListener('change', (e) => this.configChanged({ ...this._config, show_gauges: e.target.checked }));
    gaugesToggle.appendChild(gaugesCheckbox);
    genDiv.appendChild(gaugesToggle);

    // Max Download
    const maxDlOption = document.createElement('div');
    maxDlOption.style.cssText = "display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;";
    maxDlOption.innerHTML = `<label style="font-size: 12px; color: var(--secondary-text-color, #ccc);">Max Download (Mbps)</label>`;
    const maxDlInput = document.createElement('input');
    maxDlInput.type = "number";
    maxDlInput.value = this._config.max_download || 1000;
    maxDlInput.style.cssText = "padding: 6px; border-radius: 4px; border: 1px solid var(--divider-color, #444); background: var(--card-background-color, #111); color: var(--primary-text-color, #fff); width: 80px;";
    maxDlInput.addEventListener('change', (e) => this.configChanged({ ...this._config, max_download: Number(e.target.value) }));
    maxDlOption.appendChild(maxDlInput);
    genDiv.appendChild(maxDlOption);

    // Max Upload
    const maxUlOption = document.createElement('div');
    maxUlOption.style.cssText = "display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;";
    maxUlOption.innerHTML = `<label style="font-size: 12px; color: var(--secondary-text-color, #ccc);">Max Upload (Mbps)</label>`;
    const maxUlInput = document.createElement('input');
    maxUlInput.type = "number";
    maxUlInput.value = this._config.max_upload || 500;
    maxUlInput.style.cssText = "padding: 6px; border-radius: 4px; border: 1px solid var(--divider-color, #444); background: var(--card-background-color, #111); color: var(--primary-text-color, #fff); width: 80px;";
    maxUlInput.addEventListener('change', (e) => this.configChanged({ ...this._config, max_upload: Number(e.target.value) }));
    maxUlOption.appendChild(maxUlInput);
    genDiv.appendChild(maxUlOption);

    // Show Charts Toggle
    const chartsToggle = document.createElement('div');
    chartsToggle.style.cssText = "display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;";
    chartsToggle.innerHTML = `<label style="font-size: 12px; color: var(--secondary-text-color, #ccc);">Show Charts</label>`;
    const chartsCheckbox = document.createElement('input');
    chartsCheckbox.type = "checkbox";
    chartsCheckbox.checked = this._config.show_charts !== false;
    chartsCheckbox.style.cssText = "width: 20px; height: 20px; cursor: pointer;";
    chartsCheckbox.addEventListener('change', (e) => this.configChanged({ ...this._config, show_charts: e.target.checked }));
    chartsToggle.appendChild(chartsCheckbox);
    genDiv.appendChild(chartsToggle);

    const historyOption = document.createElement('div');
    historyOption.style.cssText = "display: flex; align-items: center; justify-content: space-between;";
    historyOption.innerHTML = `<label style="font-size: 12px; color: var(--secondary-text-color, #ccc);">History (hours)</label>`;
    const historyInput = document.createElement('input');
    historyInput.type = "number";
    historyInput.value = this._config.history_hours || 168;
    historyInput.min = "24";
    historyInput.max = "720";
    historyInput.step = "24";
    historyInput.style.cssText = "padding: 6px; border-radius: 4px; border: 1px solid var(--divider-color, #444); background: var(--card-background-color, #111); color: var(--primary-text-color, #fff); width: 60px;";
    historyInput.addEventListener('change', (e) => this.configChanged({ ...this._config, history_hours: Number(e.target.value) }));
    historyOption.appendChild(historyInput);
    genDiv.appendChild(historyOption);
    container.appendChild(genDiv);

    // Labels Section
    const labelsDiv = document.createElement('div');
    labelsDiv.style.cssText = "border: 1px solid var(--divider-color, #444); border-radius: 8px; padding: 10px; background: var(--card-background-color, #222); margin-top: 10px;";
    labelsDiv.innerHTML = `<div style="font-weight: bold; margin-bottom: 10px; color: var(--primary-color, #0ea5e9); font-size: 13px; text-transform: uppercase;">Labels</div>`;

    const createLabelInput = (key, label, defaultValue) => {
      const div = document.createElement('div');
      div.style.cssText = "display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;";
      
      const lbl = document.createElement('label');
      lbl.innerText = label;
      lbl.style.cssText = "font-size: 12px; color: var(--secondary-text-color, #ccc);";
      div.appendChild(lbl);

      const input = document.createElement('input');
      input.type = "text";
      input.value = (this._config.labels && this._config.labels[key]) || defaultValue;
      input.style.cssText = "padding: 6px; border-radius: 4px; border: 1px solid var(--divider-color, #444); background: var(--card-background-color, #111); color: var(--primary-text-color, #fff); width: 100px;";
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
  description: "Fully configurable dashboard with gauges, charts, and 20+ sensors",
  preview: true
});

console.info("%c OOKLA SPEEDTEST DASHBOARD %c v1.4.4 ", "background: #00d2ff; color: #fff; font-weight: bold;", "background: #1e293b; color: #fff;");
