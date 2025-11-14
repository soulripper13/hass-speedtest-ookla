# Speedtest.net Integration for Home Assistant
[![HACS Badge][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![Community Forum][forum-shield]][forum]
---
## English
**Speedtest.net** is a Home Assistant integration that automatically downloads and runs the Ookla Speedtest CLI to measure your internet speed.

![Logo](icon.png)

It provides eight sensors:
- **Download** – download speed in Mbps
- **Upload** – upload speed in Mbps
- **Ping** – network latency in milliseconds
- **Jitter** – network jitter in milliseconds
- **ISP** – your Internet Service Provider name
- **Server** – the speedtest server used
- **Current Version** – the current version of the Ookla Speedtest CLI
- **Latest Version** – the latest version of the Ookla Speedtest CLI

### Features
- Automatic download of the Ookla Speedtest CLI on setup
- Automatic check for new versions of the Ookla Speedtest CLI
- Service to manually update the Ookla Speedtest CLI
- Configurable update interval through the Home Assistant UI or manual update
- Fully compatible with Home Assistant and HACS
- Requires **Home Assistant 2025.11+**
---
### Installation
#### Manual installation
1. Copy the `custom_components/speedtest_net` folder to your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration → Speedtest.net**.
4. Configure update interval or leave the default.
#### HACS installation (preferred)
The preferred way is to use HACS:
1. Search and download this integration to your HA installation via HACS, or click:
   [![Open HACS Repository][hacs-repo-badge]][hacs-repo]
2. Restart Home Assistant
3. Add this integration to Home Assistant, or click:
   [![Add Integration][config-flow-badge]][config-flow]

---
### Usage
After setup, you will see eight sensors (entity IDs may include the domain prefix, e.g. `sensor.speedtest_net_download`):
- `sensor.download`
- `sensor.upload`
- `sensor.ping`
- `sensor.jitter`
- `sensor.isp`
- `sensor.server`
- `sensor.current_version`
- `sensor.latest_version`

You can use them in automations, Lovelace dashboards, or for monitoring your internet connection.
The integration also exposes two services:
- `speedtest_net.perform_test`
- `speedtest_net.update_binary`

You can call `perform_test` manually to trigger a speed test and update all sensors.
To call the service:
1. Go to **Developer Tools → Services**.
2. Select `speedtest_net.perform_test` from the dropdown.
3. Call the service (no parameters required).

You can call `update_binary` manually to update the Ookla Speedtest CLI.
To call the service:
1. Go to **Developer Tools → Services**.
2. Select `speedtest_net.update_binary` from the dropdown.
3. Call the service (no parameters required).

If you prefer to disable automatic polling:
- Go to **Settings → Devices & Services**.
- Find your Speedtest.net integration.
- Click ⚙️ **Configure**.
- Disable “Enable polling” or set a high scan interval (e.g., never).
- Save changes.
Now sensors update only when the service is manually triggered.
---
### Troubleshooting
- **Binary download fails** → Verify [speedtest.net](https://www.speedtest.net/apps/cli) is reachable.
- Logs are available under **Settings → System → Logs**.
---
## Links and Credits
- [Ookla Speedtest CLI](https://www.speedtest.net/apps/cli)
- [Home Assistant](https://www.home-assistant.io)
- [HACS Integration Guide](https://hacs.xyz/docs/faq/custom_repositories/)
- Developed by [katoa-sultan](https://github.com/soulripper13)
---
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge
[hacs-repo-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
[hacs-repo]: https://my.home-assistant.io/redirect/hacs_repository/?owner=soulripper13&repository=hacs-speedtest&category=integration
[config-flow-badge]: https://my.home-assistant.io/badges/config_flow_start.svg
[config-flow]: https://my.home-assistant.io/redirect/config_flow_start?domain=speedtest_net
[commits-shield]: https://img.shields.io/github/commit-activity/m/soulripper13/hacs-speedtest?style=for-the-badge
[commits]: https://github.com/soulripper13/hacs-speedtest/commits/main
[forum-shield]: https://img.shields.io/badge/Community-Forum-blue?style=for-the-badge&logo=home-assistant
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/soulripper13/hacs-speedtest?style=for-the-badge
[releases-shield]: https://img.shields.io/github/v/release/soulripper13/hacs-speedtest?style=for-the-badge
[releases]: https://github.com/soulripper13/hacs-speedtest/releases
