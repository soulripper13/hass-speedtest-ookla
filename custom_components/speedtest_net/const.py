"""Constants for the Speedtest.net integration."""

DOMAIN = "speedtest_net"

# Configuration keys
CONF_SCAN_INTERVAL = "scan_interval"
CONF_AUTO_UPDATE = "auto_update"

# Defaults
DEFAULT_SCAN_INTERVAL = 1800  # 30 minutes in seconds
DEFAULT_AUTO_UPDATE = True

# Sensor attributes
ATTR_DOWNLOAD = "download"
ATTR_UPLOAD = "upload"
ATTR_PING = "ping"
ATTR_JITTER = "jitter"
ATTR_ISP = "isp"
ATTR_SERVER = "server"
ATTR_CURRENT_VERSION = "current_version"
ATTR_LATEST_VERSION = "latest_version"

# Binary paths and URLs
BINARY_NAME = "speedtest"
BINARY_URL = "https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz"
BINARY_DIR = "custom_components/speedtest_net/bin"
