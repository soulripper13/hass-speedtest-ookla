# Ookla Speedtest Integration for Home Assistant

This custom integration uses the official Ookla `speedtest-cli` binary to measure internet speed and provides sensors for ping, download, and upload speeds in Home Assistant.

## Installation

1. **Install HACS** if not already installed.
2. Add this repository to HACS:
   - Go to HACS > Integrations > Explore & Download Repositories.
   - Add the custom repository: `https://github.com/soulripper13/hass-speedtest-ookla`.
3. Install the "Ookla Speedtest" integration.
4. Add the integration via Settings > Devices & Services > Add Integration:
   - The integration will automatically download the `speedtest-cli` binary, set up required files, and accept the EULA during configuration.
   - If the setup fails (e.g., due to network issues or unsupported architecture), follow the manual setup instructions below.
5. Restart Home Assistant if prompted.

### Manual Setup (Only if Automated Setup Fails)
1. Download the `speedtest-cli` binary:
   - Visit [Ookla Speedtest CLI](https://www.speedtest.net/apps/cli).
   - Download the appropriate Linux binary for your system (e.g., `x86_64`, check with `uname -m`).
   - Extract the binary and rename it to `speedtest.bin`.
   - Place it in `/config/shell/` (create the directory if needed, e.g., via Terminal & SSH or Samba).
2. Run the setup script:
   ```bash
   cd /config/custom_components/ookla_speedtest/shell
   bash setup_speedtest.sh
   ```
3. Restart Home Assistant.

## Configuration

- **Server Selection**: Choose "Closest Server" for automatic server selection or pick a specific server from the dropdown (e.g., "Server Name (City, Country)"). If the server list fails to load, you can enter a manual server ID (find IDs at [Speedtest Servers](https://c.speedtest.net/speedtest-servers-static.php)).
- **Manual Mode**: Enable to disable automatic polling and run tests manually or via automation.
- **Scan Interval**: Set the polling interval in minutes (default: 60).

## Service

- `ookla_speedtest.run_speedtest`: Manually trigger a speed test.

## Automation Example

```yaml
automation:
  - alias: "Run Speedtest Every Hour"
    trigger:
      platform: time_pattern
      minutes: "/60"
    action:
      service: ookla_speedtest.run_speedtest
```

## Notes

- Ensure TCP port 8080 is open outbound for Speedtest servers.
- Running speed tests consumes significant bandwidth; avoid frequent tests on metered connections.
- The integration automatically sets up the `speedtest-cli` binary and required files in `/config/shell/`.
- If the server list cannot be retrieved, you can still configure the integration using "Closest Server" or a manual server ID.
- Sensors are updated only after a speed test completes successfully, ensuring consistent and reliable data.

Report issues at [GitHub Issues](https://github.com/soulripper13/hass-speedtest-ookla/issues).
