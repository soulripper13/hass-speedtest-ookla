#!/bin/bash
# Fully automated setup script for Ookla Speedtest integration

# Define paths
CONFIG_DIR="/config"
SHELL_DIR="${CONFIG_DIR}/shell"
INTEGRATION_DIR="/config/custom_components/ookla_speedtest"
SCRIPT_DIR="${INTEGRATION_DIR}/shell"

# Function to check for required commands
check_prerequisites() {
    for cmd in curl tar; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: $cmd is required but not installed."
            echo "Please install $cmd (e.g., 'apk add curl tar' in Alpine-based systems) and re-run this script."
            exit 1
        fi
    done
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
            echo "Error: Unsupported architecture ($arch)."
            echo "Please manually download the speedtest-cli binary for your system from https://www.speedtest.net/apps/cli"
            echo "Rename it to speedtest.bin, place it in ${SHELL_DIR}, and re-run this script."
            exit 1
            ;;
    esac

    echo "Downloading speedtest-cli for $arch..."
    if curl -L -o "/tmp/$filename" "$url"; then
        echo "Extracting speedtest-cli..."
        tar -xzf "/tmp/$filename" -C "/tmp" speedtest
        mv "/tmp/speedtest" "${SHELL_DIR}/speedtest.bin"
        rm "/tmp/$filename"
    else
        echo "Error: Failed to download speedtest-cli from $url."
        echo "Please manually download the binary from https://www.speedtest.net/apps/cli and place it in ${SHELL_DIR}/speedtest.bin."
        exit 1
    fi
}

# Main setup process
echo "Starting automated setup for Ookla Speedtest integration..."

# Check prerequisites
check_prerequisites

# Create /config/shell directory if it doesn't exist
echo "Creating shell directory if it doesn't exist..."
mkdir -p "${SHELL_DIR}"

# Copy shell scripts to /config/shell
echo "Copying shell scripts to ${SHELL_DIR}..."
if [ -d "${SCRIPT_DIR}" ]; then
    cp "${SCRIPT_DIR}/launch_speedtest.sh" "${SHELL_DIR}/"
    cp "${SCRIPT_DIR}/list_servers.sh" "${SHELL_DIR}/"
else
    echo "Error: Integration shell directory (${SCRIPT_DIR}) not found. Ensure the integration is installed."
    exit 1
fi

# Download speedtest.bin if not present
if [ ! -f "${SHELL_DIR}/speedtest.bin" ]; then
    download_speedtest_bin
else
    echo "speedtest.bin already exists in ${SHELL_DIR}, skipping download."
fi

# Set executable permissions
echo "Setting executable permissions..."
chmod +x "${SHELL_DIR}/speedtest.bin" "${SHELL_DIR}/launch_speedtest.sh" "${SHELL_DIR}/list_servers.sh"

# Accept EULA for speedtest.bin
echo "Accepting Ookla EULA for speedtest.bin..."
"${SHELL_DIR}/speedtest.bin" --accept-license --accept-gdpr

echo "Setup complete! Restart Home Assistant to apply changes."
echo "If errors occurred, follow manual setup instructions in the README."
