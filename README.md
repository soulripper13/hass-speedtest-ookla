# Ookla Speedtest Integration for Home Assistant

This custom integration uses the official Ookla `speedtest-cli` binary to measure internet speed and provides sensors for ping, download, and upload speeds in Home Assistant.

## Installation

1. **Install HACS** if not already installed.
2. Add this repository to HACS:
   - Go to HACS > Integrations > Explore & Download Repositories.
   - Add the custom repository: `https://github.com/soulripper13/hass-speedtest-ookla`.
3. Install the "Ookla Speedtest" integration.
4. Download the `speedtest-cli` binary:
   - Visit [Ookla Speedtest CLI](https://www.speedtest.net/apps/cli).
   - Download the appropriate Linux binary for your system (e.g., `x86_64`).
   - Extract and rename the binary to `speedtest.bin`.
   - Place it in `/config/shell/` (create the `shell` directory if it doesn't exist).
5. Accept the Ookla EULA by running `/config/shell/speedtest.bin` once via terminal.
6. Restart Home Assistant.
7. Add the integration via Settings > Devices & Services > Add Integration.

## Configuration

- **Server Selection**: Choose "Closest Server" for automatic server selection or pick a specific server from the dropdown (e.g., "Server Name (City, Country)"). Server IDs can also be found at [Speedtest Servers](https://c.speedtest.net/speedtest-servers-static.php).
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
- The `speedtest.bin` binary must be executable (`chmod +x /config/shell/speedtest.bin`).
- Server list retrieval requires the `speedtest-cli` binary to be properly configured.

Report issues at [GitHub Issues](https://github.com/yourusername/hass-speedtest-ookla/issues).
