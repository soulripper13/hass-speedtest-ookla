"""Constants for the Ookla Speedtest integration."""

DOMAIN = "ookla_speedtest"

# Configuration
CONF_SERVER_ID = "server_id"
CONF_MANUAL = "manual"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_START_TIME = "start_time"
CONF_ISP_DL_SPEED = "isp_dl_speed"
CONF_ISP_UL_SPEED = "isp_ul_speed"
DEFAULT_SCAN_INTERVAL = 1440  # minutes (24 hours)
STARTUP_DELAY = 60  # seconds - delay before first speedtest in interval mode

# Service
SERVICE_RUN_SPEEDTEST = "run_speedtest"

# Paths
SPEEDTEST_BIN_PATH = "/config/shell/speedtest.bin"
LAUNCH_SCRIPT_PATH = "/config/shell/launch_speedtest.sh"
INTEGRATION_SHELL_DIR = "/config/custom_components/ookla_speedtest/shell"

# Sensor attributes
ATTR_PING = "ping"
ATTR_PING_LOW = "ping low"
ATTR_PING_HIGH = "ping high"
ATTR_DOWNLOAD = "download"
ATTR_DOWNLOAD_LATENCY_IQM = "ping during download"
ATTR_DOWNLOAD_LATENCY_LOW = "ping low during download"
ATTR_DOWNLOAD_LATENCY_HIGH = "ping high during download"
ATTR_DOWNLOAD_LATENCY_JITTER = "jitter during download"
ATTR_UPLOAD = "upload"
ATTR_DL_PCT = "download_percent"
ATTR_UL_PCT = "upload_percent"
ATTR_BUFFERBLOAT_GRADE = "bufferbloat_grade"
ATTR_UPLOAD_LATENCY_IQM = "ping during upload"
ATTR_UPLOAD_LATENCY_LOW = "ping low during upload"
ATTR_UPLOAD_LATENCY_HIGH = "ping high during upload"
ATTR_UPLOAD_LATENCY_JITTER = "jitter during upload"
ATTR_JITTER = "jitter"
ATTR_SERVER = "server"
ATTR_ISP = "isp"
ATTR_DATE_LAST_TEST = "last_test"
ATTR_RESULT_URL = "result_url"
