#!/bin/bash
# Fully automated setup script for Ookla Speedtest integration

# Define paths
CONFIG_DIR="/config"
SHELL_DIR="${CONFIG_DIR}/shell"
INTEGRATION_DIR="/config/custom_components/ookla_speedtest"
SCRIPT_DIR="${INTEGRATION_DIR}/shell"

# Function to log errors to stderr for Home Assistant logs
log_error() {
    echo "ERROR: $1" >&2
}

# Function to check for required commands
check_prerequisites() {
    local missing_cmds=""
    for cmd in curl tar chmod; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_cmds="$missing_cmds $cmd"
        fi
    done
    if [ -n "$missing_cmds" ]; then
        log_error "Required commands not found:$missing_cmds"
        log_error "Install them (e.g., 'apk add curl tar coreutils' in Alpine-based systems) and re-run this script."
        exit 1
    fi
}

# Function to ensure shell scripts are executable
ensure_executable_permissions() {
    echo "Ensuring executable permissions for shell scripts..."
    local scripts=("setup_speedtest.sh" "launch_speedtest.sh" "list_servers.sh")
    local success=true

    # Try setting permissions in SCRIPT_DIR
    for script in "${scripts[@]}"; do
        if [ -f "${SCRIPT_DIR}/${script}" ]; then
            chmod +x "${SCRIPT_DIR}/${script}" 2>/dev/null || {
                log_error "Failed to set executable permission for ${SCRIPT_DIR}/${script}"
                success=false
            }
        else
            log_error "Script not found: ${SCRIPT_DIR}/${script}"
            success=false
        fi
    done

    # If any permission setting failed in SCRIPT_DIR, try SHELL_DIR
    if [ "$success" = false ]; then
        echo "Attempting to set permissions in ${SHELL_DIR}..."
        for script in "${scripts[@]}"; do
            if [ -f "${SHELL_DIR}/${script}" ]; then
                chmod +x "${SHELL_DIR}/${script}" 2>/dev/null || {
                    log_error "Failed to set executable permission for ${SHELL_DIR}/${script}"
                    log_error "Run 'chmod +x /config/custom_components/ookla_speedtest/shell/*.sh' manually."
                    exit 1
                }
            fi
        done
    fi
}

# Function to detect architecture and download speedtest.bin
download_speedtest_bin() {
    local arch
    arch=$(uname -m)
    local url=""
    local filename="speedtest.tgz"

    case "$arch" in
        x86_64)
            url="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz"
            ;;
        arm|armv7l)
            url="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-armel.tgz"
            ;;
        aarch64)
            url="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-aarch64.tgz"
            ;;
        *)
            log_error "Unsupported architecture ($arch)."
            log_error "Manually download the speedtest-cli binary from https://www.speedtest.net/apps/cli, rename it to speedtest.bin, and place it in ${SHELL_DIR}."
            exit 1
            ;;
    esac

    echo "Downloading speedtest-cli for $arch..."
    if ! curl -L -o "/tmp/$filename" "$url" 2>/dev/null; then
        log_error "Failed to download speedtest-cli from $url."
        log_error "Manually download the binary from https://www.speedtest.net/apps/cli and place it in ${SHELL_DIR}/speedtest.bin."
        exit 1
    fi

    echo "Extracting speedtest-cli..."
    if ! tar -xzf "/tmp/$filename" -C "/tmp" speedtest 2>/dev/null; then
        log_error "Failed to extract speedtest-cli from /tmp/$filename."
        rm -f "/tmp/$filename"
        exit 1
    fi
    mv "/tmp/speedtest" "${SHELL_DIR}/speedtest.bin"
    rm -f "/tmp/$filename"
}

# Main setup process
echo "Starting automated setup for Ookla Speedtest integration..."

# Check prerequisites
check_prerequisites

# Create /config/shell directory if it doesn't exist
echo "Creating shell directory if it doesn't exist..."
mkdir -p "${SHELL_DIR}" || {
    log_error "Failed to create directory ${SHELL_DIR}. Ensure /config/ is writable."
    exit 1
}

# Ensure shell scripts are executable
ensure_executable_permissions

# Copy shell scripts to /config/shell if not already present
echo "Copying shell scripts to ${SHELL_DIR}..."
if [ -d "${SCRIPT_DIR}" ]; then
    for script in launch_speedtest.sh list_servers.sh; do
        if [ ! -f "${SHELL_DIR}/${script}" ]; then
            cp "${SCRIPT_DIR}/${script}" "${SHELL_DIR}/" || {
                log_error "Failed to copy ${script} to ${SHELL_DIR}."
                exit 1
            }
        else
            echo "${script} already exists in ${SHELL_DIR}, skipping copy."
        fi
    done
else
    log_error "Integration shell directory (${SCRIPT_DIR}) not found. Ensure the integration is installed."
    exit 1
fi

# Download speedtest.bin if not present
if [ ! -f "${SHELL_DIR}/speedtest.bin" ]; then
    download_speedtest_bin
else
    echo "speedtest.bin already exists in ${SHELL_DIR}, skipping download."
fi

# Set executable permissions for speedtest.bin
echo "Setting executable permissions for speedtest.bin..."
chmod +x "${SHELL_DIR}/speedtest.bin" 2>/dev/null || {
    log_error "Failed to set executable permissions for ${SHELL_DIR}/speedtest.bin."
    log_error "Run 'chmod +x /config/shell/speedtest.bin' manually."
    exit 1
}

# Accept EULA for speedtest.bin
echo "Accepting Ookla EULA for speedtest.bin..."
"${SHELL_DIR}/speedtest.bin" --accept-license --accept-gdpr >/dev/null 2>&1 || {
    echo "Warning: Failed to accept EULA. This may not affect functionality."
}

echo "Setup complete! Restart Home Assistant to apply changes."
echo "If errors occurred, follow manual setup instructions in the README."
