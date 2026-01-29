# 🚀 Ookla Speedtest Custom Cards

Beautiful, standalone Lovelace cards bundled with the Ookla Speedtest integration. No external dependencies required!

## 📦 Included Cards

| Card | File | Description | Best For |
|------|------|-------------|----------|
| **Main** | `ookla-speedtest-card.js` | Full Ookla interface with radial gauges, GO button, and all metrics | Main dashboard |
| **Minimal** | `ookla-speedtest-minimal.js` | Clean design with large typography | Minimalist setups |
| **Compact** | `ookla-speedtest-compact.js` | Small single-line card | Side panels, crowded dashboards |
| **Dashboard** | `ookla-speedtest-dashboard.js` | Full metrics with sparkline charts | Complete overview |

---

## 🚀 Installation

### Option 1: Automatic (Recommended)

The cards are automatically available after installing the integration. Just add the resource to your dashboard:

1. Go to **Settings** → **Dashboards** → **Resources**
2. Click **"Add Resource"**
3. Enter URL: `/local/ookla_speedtest/ookla-speedtest-card.js`
4. Select **"JavaScript Module"**
5. Click **"Create"**
6. Repeat for other card versions if desired

### Option 2: Manual Configuration

Add to your `configuration.yaml`:

```yaml
lovelace:
  resources:
    - url: /local/ookla_speedtest/ookla-speedtest-card.js
      type: module
    - url: /local/ookla_speedtest/ookla-speedtest-minimal.js
      type: module
    - url: /local/ookla_speedtest/ookla-speedtest-compact.js
      type: module
    - url: /local/ookla_speedtest/ookla-speedtest-dashboard.js
      type: module
```

---

## 🎨 Card Usage

### Main Card (Ookla Style)

```yaml
type: custom:ookla-speedtest-card
entities:
  download: sensor.ookla_speedtest_download
  upload: sensor.ookla_speedtest_upload
  ping: sensor.ookla_speedtest_ping
  jitter: sensor.ookla_speedtest_jitter
  grade: sensor.ookla_speedtest_bufferbloat_grade
  isp: sensor.ookla_speedtest_isp
  server: sensor.ookla_speedtest_server
  last_test: sensor.ookla_speedtest_last_test
  result_url: sensor.ookla_speedtest_result_url
max_download: 1000
max_upload: 500
```

**Features:**
- 🎯 Animated radial gauges (Download/Upload)
- 🔵 Large centered GO button with pulse animation
- 📊 Ping, Jitter, and Grade metrics
- 🌐 ISP and server display
- 🔗 "View Full Results" link (opens in new tab)
- 🎨 Beautiful dark gradient theme

---

### Minimal Card

```yaml
type: custom:ookla-speedtest-minimal
entities:
  download: sensor.ookla_speedtest_download
  upload: sensor.ookla_speedtest_upload
  ping: sensor.ookla_speedtest_ping
  isp: sensor.ookla_speedtest_isp
```

**Features:**
- ✨ Clean, simple design
- 🔢 Large speed numbers
- 🎨 Color-coded values
- ▶ Single "Run Test" button

---

### Compact Card

```yaml
type: custom:ookla-speedtest-compact
entities:
  download: sensor.ookla_speedtest_download
  upload: sensor.ookla_speedtest_upload
  ping: sensor.ookla_speedtest_ping
```

**Features:**
- 📏 Minimal footprint
- 🎯 Embedded GO button
- ⚡ Quick stats at a glance
- 💪 Perfect for side panels

---

### Dashboard Card

```yaml
type: custom:ookla-speedtest-dashboard
entities:
  download: sensor.ookla_speedtest_download
  upload: sensor.ookla_speedtest_upload
  ping: sensor.ookla_speedtest_ping
  jitter: sensor.ookla_speedtest_jitter
  grade: sensor.ookla_speedtest_bufferbloat_grade
  isp: sensor.ookla_speedtest_isp
  server: sensor.ookla_speedtest_server
  last_test: sensor.ookla_speedtest_last_test
  result_url: sensor.ookla_speedtest_result_url
show_charts: true
chart_points: 20
```

**Features:**
- 📈 Mini sparkline charts (Download/Upload/Ping history)
- 📊 All 5 metrics displayed
- 🕒 Smart relative time display
- 🔗 Direct result link
- 📱 Responsive (hides charts on mobile)

---

## ⚙️ Configuration Options

### Common Options (All Cards)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entities.download` | string | `sensor.ookla_speedtest_download` | Download speed entity |
| `entities.upload` | string | `sensor.ookla_speedtest_upload` | Upload speed entity |
| `entities.ping` | string | `sensor.ookla_speedtest_ping` | Ping entity |

### Main Card Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_download` | number | `1000` | Max value for download gauge |
| `max_upload` | number | `500` | Max value for upload gauge |

### Dashboard Card Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_charts` | boolean | `true` | Show/hide sparkline charts |
| `chart_points` | number | `20` | Number of data points to show |

---

## 🎨 Visual Preview

### Main Card
```
┌─────────────────────────────┐
│           🌐                │
│       Your ISP Name         │
│      Server: Amsterdam      │
│                             │
│    ⭕         ⭕            │
│   Download   Upload         │
│    847       425   Mbps     │
│                             │
│          ┌───┐              │
│          │GO │              │
│          └───┘              │
│  ⏱️ 12ms 📊 2ms 🏆 A+      │
│  Last test: 2 min ago       │
│  🔗 View Full Results →     │
└─────────────────────────────┘
```

### Compact Card
```
┌──────────────────────────┐
│ Speedtest      ┌──────┐  │
│ ⬇847 ⬆425 ⏱12 │  GO  │  │
│                └──────┘  │
└──────────────────────────┘
```

---

## 🔄 Updating Cards

The cards are updated automatically when you update the integration via HACS. Just refresh your browser after updating.

---

## 🐛 Troubleshooting

### Card not showing in card picker
- Make sure the resource is added in **Settings** → **Dashboards** → **Resources**
- Refresh your browser (Ctrl+F5)
- Check browser console for errors

### "Custom element doesn't exist"
- The resource URL might be incorrect
- Try: `/local/ookla_speedtest/ookla-speedtest-card.js`
- Or: `/hacsfiles/ookla_speedtest/ookla-speedtest-card.js` (if using HACS)

### Metrics showing "0" or "--"
- Run a speed test first by clicking the GO button
- Check that your entity IDs match in Developer Tools → States

---

## 💡 Tips

1. **Use Panel Mode** for best results:
   - Dashboard menu → **"Panel Mode"**

2. **Create a dedicated view**:
   - Add a new view called "Network"
   - Use "Panel (1 card)" view type

3. **Combine cards**:
   - Use the Dashboard card as main
   - Add Compact cards to sidebar

---

Made with ❤️ for the Home Assistant community
