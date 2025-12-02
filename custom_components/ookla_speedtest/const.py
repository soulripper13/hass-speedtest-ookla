"""Constants for the Ookla Speedtest integration."""

DOMAIN = "ookla_speedtest"
<<<<<<< HEAD
=======

# Configuration
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
CONF_SERVER_ID = "server_id"
CONF_MANUAL = "manual"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 1440  # minutes (24 hours)
<<<<<<< HEAD
SERVICE_RUN_SPEEDTEST = "run_speedtest"
=======

# Service
SERVICE_RUN_SPEEDTEST = "run_speedtest"

# Paths
SPEEDTEST_BIN_PATH = "/config/shell/speedtest.bin"
LAUNCH_SCRIPT_PATH = "/config/shell/launch_speedtest.sh"
INTEGRATION_SHELL_DIR = "/config/custom_components/ookla_speedtest/shell"

# Sensor attributes
ATTR_PING = "ping"
ATTR_DOWNLOAD = "download"
ATTR_UPLOAD = "upload"
ATTR_JITTER = "jitter"
ATTR_SERVER = "server"
ATTR_ISP = "isp"
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
