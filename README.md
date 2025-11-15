# Ookla Speedtest Integration for Home Assistant

![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge)
[![GitHub release](https://img.shields.io/github/release/soulripper13/hass-speedtest-ookla.svg)](https://github.com/soulripper13/hass-speedtest-ookla/releases)
[![GitHub issues](https://img.shields.io/github/issues/soulripper13/hass-speedtest-ookla.svg)](https://github.com/soulripper13/hass-speedtest-ookla/issues)

The Ookla Speedtest integration lets you track your internet speed in Home Assistant using the official Ookla `speedtest-cli` tool. It creates sensors for ping, download, and upload speeds, with options for automatic or manual testing.

<img width="1043" alt="card-example" src="https://github.com/user-attachments/assets/87633825-55bc-4819-a67d-1a79030ad8a1" />

## Features
- **Sensors for**:
  - **Ping** (ms): Measures latency.
  - **Download** (Mbit/s): Measures download speed.
  - **Upload** (Mbit/s): Measures upload speed.
  - **Jitter** (ms): Measures network stability by tracking variations in ping times.
  - **Server**: Displays the name and location of the speed test server used.
  - **ISP**: Shows the name of your Internet Service Provider.
- **Flexible Testing**:
  - Choose the closest server or a specific server by ID.
  - Run tests automatically at a configurable interval.
  - Disable automatic tests and run them on-demand via services or automations.
- **Service to trigger tests**: `ookla_speedtest.run_speedtest`.

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

During the setup wizard, you can configure the following:

-   **Server**: Choose "Closest Server" for automatic selection or pick a specific server from the list. If the server list fails to load, you can manually enter a server ID from the [official list](https://c.speedtest.net/speedtest-servers-static.php).
-   **Manual Mode**: Enable this option to disable automatic, scheduled tests. You can then trigger tests using automations or the `ookla_speedtest.run_speedtest` service.
-   **Scan Interval**: If not in manual mode, set the frequency of automatic tests in minutes (default is 1440 minutes, or 24 hours).

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
          - value: 50
            color: orange
          - value: 100
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
        max: 100
        color_threshold:
          - value: 0
            color: red
          - value: 50
            color: orange
          - value: 100
            color: green
        show:
          header_color_threshold: true
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
  - show_name: true
    show_icon: false
    type: button
    tap_action:
      action: call-service
      service: script.speedtest
    name: Run Speedtest Now
layout:
  width: "320"
```

### Customizing Card Ranges

To get the most accurate visual feedback, adjust the `max` and `color_threshold` values in the card configuration to match your internet plan's speeds.

## Troubleshooting

-   **Setup Fails**: Check the Home Assistant logs at **Settings > System > Logs** for any errors related to `custom_components.ookla_speedtest`. Ensure that `curl` and `tar` are available in your Home Assistant environment.
-   **No Server List**: If the server list doesn't load, try using the "Closest Server" option or find a manual server ID from the [Speedtest Servers list](https://c.speedtest.net/speedtest-servers-static.php).
-   **Card Not Displaying**: Ensure `custom:apexcharts-card` and `custom:layout-card` are correctly installed and that you have cleared your browser cache.

## Reporting Issues

If you encounter any issues, please [report them on GitHub](https://github.com/soulripper13/hass-speedtest-ookla/issues). Include detailed logs and steps to reproduce the problem. To enable debug logging, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ookla_speedtest: debug
```
