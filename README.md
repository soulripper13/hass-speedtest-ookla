# Ookla Speedtest Integration for Home Assistant

[![HACS Default](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/release/soulripper13/hass-speedtest-ookla.svg?style=for-the-badge)](https://github.com/soulripper13/hass-speedtest-ookla/releases)
[![GitHub Issues](https://img.shields.io/github/issues/soulripper13/hass-speedtest-ookla.svg?style=for-the-badge)](https://github.com/soulripper13/hass-speedtest-ookla/issues)
![Downloads](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=Downloads&suffix=%20installs&cacheSeconds=15600&style=for-the-badge&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.ookla_speedtest.total)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support%20This%20Project-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://github.com/soulripper13/hass-speedtest-ookla#support-the-project)
[![Solana](https://img.shields.io/badge/Solana-14F195?style=for-the-badge&logo=solana&logoColor=white)](https://solana.com)
[![Bitcoin](https://img.shields.io/badge/Bitcoin-FF9900?style=for-the-badge&logo=bitcoin&logoColor=white)](https://bitcoin.org)

**Support Development:** If you find this integration helpful, consider supporting with Solana (`4jvCR2YFQLqguoyz9qAMPzVbaEcDsG5nzRHFG8SeaeBK`) or Bitcoin (`bc1qvu8a9gdy3dcxa94jge7d3rd7claapsydjsjxn0`)

---

The Ookla Speedtest integration lets you track your internet speed in Home Assistant using the official Ookla `speedtest-cli` tool. It creates sensors for ping, download, and upload speeds, with options for automatic or manual testing.

<img width="1043" alt="card-example" src="https://github.com/user-attachments/assets/87633825-55bc-4819-a67d-1a79030ad8a1" />

## Features
- **Comprehensive Sensors**:
  - **Ping** (ms): Measures latency.
  - **Download** (Mbit/s): Measures download speed.
  - **Upload** (Mbit/s): Measures upload speed.
  - **Jitter** (ms): Measures network stability by tracking variations in ping times.
  - **Server**: Displays the name and location of the speed test server used.
  - **ISP**: Shows the name of your Internet Service Provider.
- **Flexible Testing Options**:
  - Choose the closest server automatically or select from the 10 nearest servers.
  - Enter a specific server ID manually for precise testing.
  - Run tests automatically at a configurable interval (default: 24 hours).
  - Enable manual mode to run tests only on-demand via services or automations.
- **User-Friendly Configuration**:
  - Easy setup with step-by-step guidance and helpful descriptions for each option.
  - Reconfigure anytime through the Home Assistant UI (Settings > Devices & Services > Ookla Speedtest > Configure).
  - Automatic integration reload when settings are changed.
- **Service Integration**: Trigger tests manually using `ookla_speedtest.run_speedtest` service.

## Recent Updates

### Version 2.0.0 (Latest)
- **Fixed**: Resolved 500 Internal Server Error when clicking Configure button
- **Fixed**: Config flow handler registration for improved compatibility
- **New**: Added user-friendly descriptions for all configuration options
- **New**: Configuration changes now automatically reload the integration
- **New**: Complete UI-based configuration and reconfiguration support
- **Improved**: Options flow now properly handles entry.options with fallback to entry.data for backwards compatibility
- **Enhanced**: Better error messages and validation during setup
- **Enhanced**: Added comprehensive translation files (strings.json, en.json)

## Installation

This integration is best installed via the [Home Assistant Community Store (HACS)](https://hacs.xyz/).

1.  **Add the Custom Repository**:
    *   Ensure HACS is installed.
    *   Go to **HACS > Integrations > ... (three dots) > Custom repositories**.
    *   Add this repository's URL: `https://github.com/soulripper13/hass-speedtest-ookla`
    *   Select the category **Integration** and click **Add**.
  
      [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store (HACS).](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=soulripper13&repository=hass-speedtest-ookla&category=integration)


      [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ookla_speedtest)

3.  **Install the Integration**:
    *   In HACS, search for "Ookla Speedtest" and click **Download**.
    *   Follow the prompts to complete the download.

4.  **Restart Home Assistant**:
    *   Go to **Settings > System** and click the **Restart** button.

5.  **Add the Integration**:
    *   Go to **Settings > Devices & Services > Add Integration**.
    *   Search for and select **Ookla Speedtest**.
    *   The setup wizard will guide you through the final configuration steps.

## Configuration

During the setup wizard, you'll be guided through configuring the integration with helpful descriptions for each option:

### Configuration Options

-   **Speedtest Server**:
    - Choose "Closest Server" for automatic selection
    - Select from the 10 nearest servers (sorted by distance)
    - Or select "Manual Server ID" to enter a specific server ID
    - *Tip: Find server IDs at [speedtest.net/servers](https://www.speedtest.net/speedtest-servers-static.php)*

-   **Manual Server ID**:
    - Only required when "Manual Server ID" is selected above
    - Enter a specific numeric server ID for precise testing

-   **Manual Mode**:
    - **Enabled**: Speed tests only run when manually triggered via the `ookla_speedtest.run_speedtest` service
    - **Disabled**: Tests run automatically based on the scan interval
    - *Default: Enabled*

-   **Scan Interval** (minutes):
    - How often to automatically run speed tests (only when Manual Mode is disabled)
    - *Default: 1440 minutes (24 hours)*
    - *Warning: Lower values will use more bandwidth*

### Reconfiguring

You can change these settings anytime:
1. Go to **Settings > Devices & Services**
2. Find **Ookla Speedtest** in your integrations
3. Click the **Configure** button
4. Update your settings
5. The integration will automatically reload with the new configuration

## Usage

### Sensors

The integration creates the following sensors:

-   `sensor.speedtest_ping`: Latency (ms)
-   `sensor.speedtest_download`: Download speed (Mbit/s)
-   `sensor.speedtest_upload`: Upload speed (Mbit/s)

### Automation Example

Here is an example of an automation that runs a speed test every day at midnight:

```yaml
automation:
  - alias: "Daily Speedtest"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: ookla_speedtest.run_speedtest
```

## Lovelace Card Example

You can create a beautiful and functional Lovelace card to display your speed test results and trigger new tests. This example uses `custom:apexcharts-card` and `custom:layout-card`, which can be installed via HACS.

### Prerequisites

1.  Install `custom:apexcharts-card` and `custom:layout-card` from HACS.
2.  Create a script to trigger the speed test. Add the following to your `configuration.yaml`:
    ```yaml
    script:
      speedtest:
        alias: Run Speedtest
        sequence:
          - service: ookla_speedtest.run_speedtest
    ```
    Then, reload your scripts from **Settings > Automations & Scenes > Scripts**.

### Card Configuration

Add the following YAML to your Lovelace dashboard:

```yaml
type: custom:layout-card
layout_type: custom:vertical-layout
layout:
  width: 320
  card_margin: 0px
cards:
  - type: custom:apexcharts-card
    chart_type: radialBar
    experimental:
      color_threshold: true
    header:
      show: true
      title: Speedtest
      show_states: true
      colorize_states: true
    series:
      - entity: sensor.speedtest_ping
        name: Ping
        min: 1
        max: 200
        color_threshold:
          - value: 1
            color: green
          - value: 100
            color: orange
          - value: 200
            color: red
        show:
          header_color_threshold: true
      - entity: sensor.speedtest_download
        name: Download
        min: 0
        max: 1000
        color_threshold:
          - value: 0
            color: red
          - value: 500
            color: orange
          - value: 1000
            color: green
        show:
          header_color_threshold: true
      - entity: sensor.speedtest_upload
        name: Upload
        min: 0
        max: 110
        color_threshold:
          - value: 0
            color: red
          - value: 55
            color: orange
          - value: 110
            color: green
        show:
          header_color_threshold: true
      - entity: sensor.speedtest_jitter
        name: Jitter
        color: aqua
        show:
          header_color_threshold: true
          in_chart: false
    apex_config:
      plotOptions:
        radialBar:
          offsetY: 0
          startAngle: -90
          endAngle: 90
          dataLabels:
            name:
              show: false
            value:
              show: false
      legend:
        show: false
      fill:
        type: gradient
    card_mod:
      style: |
        :host {
          margin: 0 !important;
          padding: 0 !important;
        }
  - type: entities
    entities:
      - entity: sensor.speedtest_isp
        name: ISP
        icon: false
      - entity: sensor.speedtest_server
        name: Server
        icon: false
    card_mod:
      style: |
        :host {
          margin: 0 !important;
          padding: 0 !important;
          --ha-card-border-width: 0;
        }
  - show_name: true
    show_icon: false
    type: button
    tap_action:
      action: perform-action
      perform_action: ookla_speedtest.run_speedtest
      target: {}
    name: Speedtest
    card_mod:
      style: |
        :host {
          margin: 0 !important;
          padding: 0 !important;
          --ha-card-border-width: 0;
        }

```

### Customizing Card Ranges

To get the most accurate visual feedback, adjust the `max` and `color_threshold` values in the card configuration to match your internet plan's speeds.

## Troubleshooting

-   **Setup Fails**: Check the Home Assistant logs at **Settings > System > Logs** for any errors related to `custom_components.ookla_speedtest`. Ensure that `curl` and `tar` are available in your Home Assistant environment.
-   **Configure Button Error (500 Error)**: This issue has been fixed in version 2.0.0. If you're still experiencing this, ensure you've updated to the latest version and restarted Home Assistant.
-   **No Server List**: If the server list doesn't load, try using the "Closest Server" option or find a manual server ID from the [Speedtest Servers list](https://c.speedtest.net/speedtest-servers-static.php).
-   **Configuration Changes Not Applied**: Make sure you click "Submit" in the configuration dialog. The integration will automatically reload with the new settings.
-   **Card Not Displaying**: Ensure `custom:apexcharts-card` and `custom:layout-card` are correctly installed and that you have cleared your browser cache.

## Reporting Issues

If you encounter any issues, please [report them on GitHub](https://github.com/soulripper13/hass-speedtest-ookla/issues). Include detailed logs and steps to reproduce the problem. To enable debug logging, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ookla_speedtest: debug
```
