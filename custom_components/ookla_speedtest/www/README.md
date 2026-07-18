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
history_hours: 168
chart_points: 100
chart_height: 70
chart_stroke_width: 2
chart_line_style: solid
chart_line_cap: round
chart_include_zero: false
chart_show_area: true
chart_area_opacity: 0.25
chart_show_points: false
chart_point_radius: 0.75
chart_colors:
  download: "#0ea5e9"
  upload: "#7c3aed"
  ping: "#f59e0b"
chart_area_colors:
  download: "#0ea5e9"
  upload: "#7c3aed"
  ping: "#f59e0b"
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

### Card Appearance (All Cards)

Appearance values can be configured visually or under the shared `appearance` block. Leave an option unset to inherit it from the active Home Assistant theme.

```yaml
appearance:
  shadow: subtle
  shadow_color: "#000000"
  # custom_shadow: "0 8px 24px rgba(0, 0, 0, 0.2)"
  background_color: "rgba(20, 24, 32, 0.92)"
  border_color: "rgba(255, 255, 255, 0.12)"
  border_width: 1
  border_radius: 12
  backdrop_blur: 16
  padding: 16
  text_color: "#f8fafc"
  accent_color: "#0ea5e9"
  font_family: "var(--primary-font-family)"
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `appearance.shadow` | string | `theme` | `theme`, `none`, `subtle`, `medium`, or `strong` |
| `appearance.shadow_color` | color | preset default | Color used by the subtle, medium, and strong shadow presets |
| `appearance.custom_shadow` | string | unset | Custom CSS `box-shadow`; overrides a preset |
| `appearance.background_color` | color | theme | Card background color, including RGB/HSL with alpha |
| `appearance.border_color` | color | theme | Card border color |
| `appearance.border_width` | number | theme | Border width in pixels (0-10) |
| `appearance.border_radius` | number | theme | Corner radius in pixels (0-64) |
| `appearance.backdrop_blur` | number | card default | Backdrop blur in pixels (0-60) |
| `appearance.padding` | number | card default | Inner card padding in pixels (0-64) |
| `appearance.text_color` | color | theme | Primary card text color |
| `appearance.accent_color` | color | card default | Buttons, links, and primary action accents |
| `appearance.font_family` | string | theme | CSS font-family value |

### Main Card Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_download` | number | `1000` | Max value for download gauge |
| `max_upload` | number | `500` | Max value for upload gauge |

### Dashboard Card Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_charts` | boolean | `true` | Show/hide sparkline charts |
| `history_hours` | number | `168` | Hours of recorder history shown in charts |
| `chart_points` | number | `100` | Maximum sampled points per series (2-500) |
| `chart_height` | number | `70` | Height of each chart in pixels (30-200) |
| `chart_stroke_width` | number | `2` | Chart line width in screen pixels (0.5-10) |
| `chart_line_style` | string | `solid` | Line style: `solid`, `dashed`, or `dotted` |
| `chart_line_cap` | string | `round` | Line ends: `round`, `butt`, or `square` |
| `chart_include_zero` | boolean | `false` | Include zero in the vertical scale |
| `chart_show_area` | boolean | `true` | Show/hide the shaded area below each line |
| `chart_area_opacity` | number | `0.25` | Shaded area opacity (0-1) |
| `chart_show_points` | boolean | `false` | Show a marker for each sampled data point |
| `chart_point_radius` | number | `0.75` | Data-point marker radius (0.25-4) |
| `chart_colors.download` | color | `#0ea5e9` | Download chart color |
| `chart_colors.upload` | color | `#7c3aed` | Upload chart color |
| `chart_colors.ping` | color | `#f59e0b` | Ping chart color |
| `chart_area_colors.download` | color | `#0ea5e9` | Download area-fill color |
| `chart_area_colors.upload` | color | `#7c3aed` | Upload area-fill color |
| `chart_area_colors.ping` | color | `#f59e0b` | Ping area-fill color |

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
