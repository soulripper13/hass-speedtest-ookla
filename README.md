# Ookla Speedtest Integration for Home Assistant

The Ookla Speedtest integration lets you track your internet speed in Home Assistant using the official Ookla `speedtest-cli` tool. It creates sensors for ping, download, and upload speeds, with options for automatic or manual testing.

## Features
- Sensors for ping (ms), download (Mbit/s), and upload (Mbit/s).
- Choose the closest server or a specific server by ID.
- Automatic tests with a default interval of 24 hours.
- Manual mode for on-demand tests via automations or services.
- Service to trigger tests (`ookla_speedtest.run_speedtest`).

## Installation
Install the integration using HACS (Home Assistant Community Store).

1. **Add the Custom Repository**:
   - Ensure HACS is installed (see [HACS documentation](https://hacs.xyz/docs/setup/download)).
   - Go to **HACS > Integrations > Menu (⋮) > Custom repositories**.
   - Add the repository: `https://github.com/soulripper13/hass-speedtest-ookla`.
   - Set category to **Integration** and click **Add**.

2. **Install the Integration**:
   - In HACS, search for "Ookla Speedtest" under **Integrations**.
   - Click **Download**, select the version (e.g., latest or commit `a0308b1`), and download.

3. **Set Script Permissions**:
   - To prevent `PermissionError`, make shell scripts executable:
     ```bash
     chmod +x /config/custom_components/ookla_speedtest/shell/*.sh
     ```
   - Use SSH (e.g., Terminal & SSH add-on) or a file manager (e.g., Samba).
   - Verify permissions:
     ```bash
     ls -l /config/custom_components/ookla_speedtest/shell/
     # Should show -rwxr-xr-x for setup_speedtest.sh, launch_speedtest.sh, list_servers.sh
     ```

4. **Restart Home Assistant**:
   - Go to **Settings > System > Restart** or run:
     ```bash
     ha core restart
     ```

5. **Add the Integration**:
   - Go to **Settings > Devices & Services > Add Integration > Ookla Speedtest**.
   - The setup wizard will:
     - Download the `speedtest-cli` binary for your system.
     - Place scripts and binaries in `/config/shell/`.
     - Accept the Ookla EULA.

### Manual Setup (if HACS Fails)
If setup fails (e.g., due to network or architecture issues):
1. Download the `speedtest-cli` binary:
   - Visit [Ookla Speedtest CLI](https://www.speedtest.net/apps/cli).
   - Choose the Linux binary for your architecture (check with `uname -m`, e.g., `x86_64`).
   - Extract, rename to `speedtest.bin`, and place in `/config/shell/` (create if needed).
2. Set permissions:
   ```bash
   chmod +x /config/shell/speedtest.bin /config/shell/*.sh
   ```
3. Run the setup script:
   ```bash
   cd /config/custom_components/ookla_speedtest/shell
   bash setup_speedtest.sh
   ```
4. Restart Home Assistant.

## Configuration
In the setup wizard:
- **Server**: Select "Closest Server" or a specific server (e.g., "Server Name (City, Country)"). If the server list fails, use a manual server ID from [Speedtest Servers](https://c.speedtest.net/speedtest-servers-static.php).
- **Manual Mode**: Enable to disable automatic tests and run them manually or via automations.
- **Scan Interval**: Set automatic test frequency in minutes (default: 1440 minutes, or 24 hours).

## Usage
- **Sensors**:
  - `sensor.speedtest_ping`: Latency (ms).
  - `sensor.speedtest_download`: Download speed (Mbit/s).
  - `sensor.speedtest_upload`: Upload speed (Mbit/s).
- **Service**: Use `ookla_speedtest.run_speedtest` to trigger a test.

### Automation Example
Run a speed test daily at midnight:
```yaml
automation:
  - alias: "Daily Speedtest"
    trigger:
      platform: time
      at: "00:00:00"
    action:
      service: ookla_speedtest.run_speedtest
```

## Lovelace Card Example
Visualize your speed test results with a radial bar chart using `custom:apexcharts-card` and trigger tests with a button. This requires `custom:apexcharts-card` and `custom:layout-card` installed via HACS.

### Prerequisites
- Install `custom:apexcharts-card` and `custom:layout-card` in HACS.
- Create a script to trigger the speed test (add to `configuration.yaml`):
  ```yaml
  script:
    speedtest:
      sequence:
        - service: ookla_speedtest.run_speedtest
  ```

### Card Configuration
Add this to your Lovelace dashboard (via UI or YAML):
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
        max: 100
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
        max: 500
        color_threshold:
          - value: 0
            color: red
          - value: 250
            color: orange
          - value: 500
            color: green
        show:
          header_color_threshold: true
      - entity: sensor.speedtest_upload
        name: Upload
        min: 0
        max: 50
        color_threshold:
          - value: 0
            color: red
          - value: 25
            color: orange
          - value: 50
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
      action: perform-action
      perform_action: script.speedtest
      target: {}
    name: Speedtest
    entity: script.speedtest
layout:
  width: "320"
```

### Customizing Range Values
Adjust the `max` values in the `series` section based on your internet provider’s speed plan:
- **Ping (`sensor.speedtest_ping`)**: Set `max` to a reasonable latency for your connection (e.g., 100 ms for most broadband). Adjust `color_threshold` values (e.g., green for <50 ms, orange for 50–75 ms, red for >75 ms).
- **Download (`sensor.speedtest_download`)**: Set `max` to your plan’s download speed (e.g., 500 Mbps for a 500 Mbps plan). Adjust `color_threshold` (e.g., green for >400 Mbps, orange for 200–400 Mbps, red for <200 Mbps).
- **Upload (`sensor.speedtest_upload`)**: Set `max` to your plan’s upload speed (e.g., 50 Mbps for a 50 Mbps upload plan). Adjust `color_threshold` (e.g., green for >40 Mbps, orange for 20–40 Mbps, red for <20 Mbps).

Example for a 1000 Mbps download / 100 Mbps upload plan:
```yaml
series:
  - entity: sensor.speedtest_ping
    max: 100
    color_threshold:
      - value: 1
        color: green
      - value: 50
        color: orange
      - value: 100
        color: red
  - entity: sensor.speedtest_download
    max: 1000
    color_threshold:
      - value: 0
        color: red
      - value: 500
        color: orange
      - value: 1000
        color: green
  - entity: sensor.speedtest_upload
    max: 100
    color_threshold:
      - value: 0
        color: red
      - value: 50
        color: orange
      - value: 100
        color: green
```

## Troubleshooting
- **PermissionError**:
  - Run:
    ```bash
    chmod +x /config/custom_components/ookla_speedtest/shell/*.sh
    ```
  - For Docker:
    ```bash
    docker exec -it <container> bash
    chmod +x /config/custom_components/ookla_speedtest/shell/*.sh
    ```
  - Check `/config/` writability: `touch /config/test && rm /config/test`.
- **Setup Fails**:
  - Check logs (**Settings > System > Logs**).
  - Ensure `curl` and `tar` are installed:
    ```bash
    apk add curl tar
    ```
  - Manually place `speedtest.bin` in `/config/shell/` (see manual setup).
- **No Server List**:
  - Use "Closest Server" or find IDs at [Speedtest Servers](https://c.speedtest.net/speedtest-servers-static.php).
- **Card Not Displaying**:
  - Verify `custom:apexcharts-card` and `custom:layout-card` are installed via HACS.
  - Ensure `script.speedtest` is defined in `configuration.yaml`.
- **Incorrect Ranges**:
  - Check your provider’s speed plan and update `max` and `color_threshold` values.

## Notes
- TCP port 8080 must be open outbound for Speedtest servers.
- The 24-hour default interval minimizes bandwidth usage.
- Report issues at [GitHub Issues](https://github.com/soulripper13/hass-speedtest-ookla/issues).
- Enable debug logging for setup details:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.ookla_speedtest: debug
  ```
