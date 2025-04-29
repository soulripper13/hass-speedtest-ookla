# Ookla Speedtest Integration for Home Assistant

The Ookla Speedtest integration enables you to monitor your internet speed within Home Assistant using the official Ookla `speedtest-cli` tool. It provides sensors for ping, download, and upload speeds, supporting both automatic and manual testing.

## Features
- Sensors for ping (ms), download (Mbit/s), and upload (Mbit/s).
- Configurable server selection (closest server or specific server by ID).
- Automatic speed tests with a default interval of 24 hours.
- Manual mode for on-demand testing via automations or services.
- Service to trigger tests manually (`ookla_speedtest.run_speedtest`).

## Installation
This integration can be installed via HACS (Home Assistant Community Store). Follow these steps to set it up:

1. **Add the Custom Repository to HACS**:
   - Ensure HACS is installed in Home Assistant (see [HACS documentation](https://hacs.xyz/docs/setup/download)).
   - In Home Assistant, go to **HACS > Integrations > Menu (⋮) > Custom repositories**.
   - Add the repository URL: `https://github.com/soulripper13/hass-speedtest-ookla`.
   - Set the category to **Integration**.
   - Click **Add**.

2. **Install the Integration**:
   - In HACS, go to **Integrations** and search for "Ookla Speedtest".
   - Click **Download** and select the desired version (e.g., commit `a0308b1` or latest).
   - Click **Download** to install the integration.

3. **Set Script Permissions**:
   - To avoid a `PermissionError`, make the shell scripts executable:
     ```bash
     chmod +x /config/custom_components/ookla_speedtest/shell/*.sh
     ```
   - Access your Home Assistant instance via SSH (e.g., Terminal & SSH add-on) or a file manager (e.g., Samba).
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
   - Navigate to **Settings > Devices & Services > Add Integration** and select "Ookla Speedtest".
   - Follow the setup wizard, which will:
     - Download the `speedtest-cli` binary for your system architecture.
     - Place scripts and binaries in `/config/shell/`.
     - Accept the Ookla EULA.

### Manual Setup (if HACS Installation Fails)
If the setup fails (e.g., due to network issues or unsupported architecture):
1. Download the `speedtest-cli` binary:
   - Visit [Ookla Speedtest CLI](https://www.speedtest.net/apps/cli).
   - Select the Linux binary for your architecture (check with `uname -m`, e.g., `x86_64`).
   - Extract and rename to `speedtest.bin`.
   - Place it in `/config/shell/` (create the directory if needed).
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
Configure the integration via the setup wizard:
- **Server**: Choose "Closest Server" for automatic selection or select a specific server (e.g., "Server Name (City, Country)"). If the server list fails to load, enter a manual server ID from [Speedtest Servers](https://c.speedtest.net/speedtest-servers-static.php).
- **Manual Mode**: Enable to disable automatic tests and run them manually or via automations.
- **Scan Interval**: Set the automatic test frequency in minutes (default: 1440 minutes, or 24 hours).

## Usage
- **Sensors**: The integration creates:
  - `sensor.speedtest_ping`: Latency in milliseconds.
  - `sensor.speedtest_download`: Download speed in Mbit/s.
  - `sensor.speedtest_upload`: Upload speed in Mbit/s.
- **Service**: Call `ookla_speedtest.run_speedtest` to trigger a test manually.

### Automation Example
Run a speed test every 24 hours at midnight:
```yaml
automation:
  - alias: "Daily Speedtest"
    trigger:
      platform: time
      at: "00:00:00"
    action:
      service: ookla_speedtest.run_speedtest
```

## Troubleshooting
- **PermissionError**:
  - Ensure scripts are executable:
    ```bash
    chmod +x /config/custom_components/ookla_speedtest/shell/*.sh
    ```
  - For Docker users:
    ```bash
    docker exec -it <container> bash
    chmod +x /config/custom_components/ookla_speedtest/shell/*.sh
    ```
  - Verify `/config/` is writable: `touch /config/test && rm /config/test`.
- **Setup Fails**:
  - Check logs (**Settings > System > Logs**) for errors.
  - Ensure `curl` and `tar` are installed:
    ```bash
    apk add curl tar
    ```
  - Manually download `speedtest.bin` as described in the manual setup.
- **No Server List**:
  - Use "Closest Server" or find a server ID at [Speedtest Servers](https://c.speedtest.net/speedtest-servers-static.php).
- **Frequent Tests**:
  - Verify the scan interval is 1440 minutes in **Settings > Devices & Services > Ookla Speedtest > Configure**.
  - Check for automations calling `ookla_speedtest.run_speedtest`.

## Notes
- Ensure TCP port 8080 is open outbound for Speedtest servers.
- Speed tests consume significant bandwidth; the 24-hour default interval minimizes impact.
- Report issues at [GitHub Issues](https://github.com/soulripper13/hass-speedtest-ookla/issues).
- For detailed setup logs, enable debug logging:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.ookla_speedtest: debug
  ```
