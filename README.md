# Ookla Speedtest Integration for Home Assistant

[![HACS Default](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/release/soulripper13/hass-speedtest-ookla.svg?style=for-the-badge)](https://github.com/soulripper13/hass-speedtest-ookla/releases)
[![GitHub Issues](https://img.shields.io/github/issues/soulripper13/hass-speedtest-ookla.svg?style=for-the-badge)](https://github.com/soulripper13/hass-speedtest-ookla/issues)
![Downloads](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=Downloads&suffix=%20installs&cacheSeconds=15600&style=for-the-badge&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.ookla_speedtest.total)

[![Support Development](https://img.shields.io/badge/Support-Development-FFDD00?style=for-the-badge&logo=paypal&logoColor=black)](#support-the-project)

---

The **Ookla Speedtest** integration allows you to measure and monitor your internet connection performance directly in Home Assistant using the official **Ookla `speedtest-cli`** tool.

It provides sensors for latency, download speed, upload speed, jitter, ISP information, and the test server used — with support for both **automatic** and **manual** testing.

<img width="1043" alt="card-example" src="https://github.com/user-attachments/assets/87633825-55bc-4819-a67d-1a79030ad8a1" />

---

## Features

### 📊 Sensors
- **Ping** (ms) – Network latency
- **Download** (Mbit/s)
- **Upload** (Mbit/s)
- **Jitter** (ms) – Network stability
- **Server** – Name and location of the test server
- **ISP** – Detected Internet Service Provider

### ⚙️ Flexible Testing
- Automatically select the closest server
- Choose from the 10 nearest servers
- Manually specify a server ID
- Automatic testing at a configurable interval
- Manual-only mode for on-demand testing

### 🧭 User-Friendly Setup
- Full UI-based setup and reconfiguration
- Clear descriptions for every option
- Automatic integration reload on configuration changes
- No YAML required

### ▶️ Service Support
- Run tests on demand via:
```

ookla_speedtest.run_speedtest

```

---

## Installation

This integration is designed to be installed via **HACS**.

### 1️⃣ Add the Repository
- Go to **HACS → Integrations → ⋮ → Custom repositories**
- Add:
```

[https://github.com/soulripper13/hass-speedtest-ookla](https://github.com/soulripper13/hass-speedtest-ookla)

````
- Category: **Integration**

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=soulripper13&repository=hass-speedtest-ookla&category=integration)

---

### 2️⃣ Install
- Search for **Ookla Speedtest** in HACS
- Click **Download**

---

### 3️⃣ Restart Home Assistant
- Go to **Settings → System → Restart**

---

### 4️⃣ Add the Integration
- Go to **Settings → Devices & Services → Add Integration**
- Search for **Ookla Speedtest**

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ookla_speedtest)

---

## Configuration

All configuration is handled through the Home Assistant UI.

### Options

#### **Speedtest Server**
- Closest server (automatic)
- Select from 10 nearest servers
- Manual server ID

> Tip: Server IDs can be found at  
> https://www.speedtest.net/speedtest-servers-static.php

#### **Manual Server ID**
- Required only when manual mode is selected

#### **Manual Mode**
- **Enabled**: Tests run only when triggered manually
- **Disabled**: Tests run automatically
- Default: **Enabled**

#### **Scan Interval**
- Automatic test interval (minutes)
- Default: **1440** (24 hours)
- Lower values consume more bandwidth

---

### Reconfiguring
1. Go to **Settings → Devices & Services**
2. Select **Ookla Speedtest**
3. Click **Configure**
4. Update options
5. Integration reloads automatically

---

## Usage

### Sensors Created
- `sensor.speedtest_ping`
- `sensor.speedtest_download`
- `sensor.speedtest_upload`
- `sensor.speedtest_jitter`
- `sensor.speedtest_isp`
- `sensor.speedtest_server`

---

### Automation Example

Run a speed test every day at midnight:

```yaml
automation:
- alias: Daily Speedtest
  trigger:
    - platform: time
      at: "00:00:00"
  action:
    - service: ookla_speedtest.run_speedtest
````

---

## Lovelace Card Example

This example uses:

* `custom:apexcharts-card`
* `custom:layout-card`

Install both via HACS.

### Optional Script

```yaml
script:
  speedtest:
    alias: Run Speedtest
    sequence:
      - service: ookla_speedtest.run_speedtest
```

---

### Example Card Configuration

```yaml
type: custom:layout-card
layout_type: custom:vertical-layout
layout:
  width: 320
cards:
  - type: custom:apexcharts-card
    chart_type: radialBar
    header:
      show: true
      title: Speedtest
      show_states: true
    series:
      - entity: sensor.speedtest_ping
        name: Ping
      - entity: sensor.speedtest_download
        name: Download
      - entity: sensor.speedtest_upload
        name: Upload
```

Adjust ranges and thresholds to match your internet plan.

---

## Troubleshooting

* **Setup fails**: Check logs at
  **Settings → System → Logs**
* **Configure button error**: Fixed in v2.0.0
* **No server list**: Try closest server or manual ID
* **Card not displaying**: Ensure required custom cards are installed

---

## Debug Logging

```yaml
logger:
  default: info
  logs:
    custom_components.ookla_speedtest: debug
```

---

## Support the Project

This integration is developed and maintained in spare time and is provided free to the Home Assistant community.

If you find it useful and would like to support ongoing development, maintenance, and improvements, any contribution is appreciated — but never required ❤️

### Ways to Support

* **PayPal**
  [https://paypal.me/SKatoaroo](https://paypal.me/SKatoaroo)

* **Bitcoin (BTC)**
  `bc1qvu8a9gdy3dcxa94jge7d3rd7claapsydjsjxn0`

* **Solana (SOL)**
  `4jvCR2YFQLqguoyz9qAMPzVbaEcDsG5nzRHFG8SeaeBK`

You can also help by:

* Reporting bugs
* Submitting pull requests
* Suggesting features
* Helping other users
* Starring the repository ⭐

Thank you for being part of the Home Assistant community.

---

## License

MIT License

