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
    for cmd in curl tar; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_cmds="$missing_cmds $cmd"
        fi
    done
    if [ -n "$missing_cmds" ]; then
        log_error "Required commands not found:$missing_cmds"
        log_error "Install them (e.g., 'apk add curl tar' in Alpine-based systems) and re-run this script."
        exit 1
    fi
}

# Function to check if shell scripts are executable
check_executable_permissions() {
    echo "Checking executable permissions for shell scripts..."
    local scripts=("setup_speedtest.sh" "launch_speedtest.sh" "list_servers.sh")
    local non_executable=""
    for script in "${scripts[@]}"; do
        if [ -f "${SCRIPT_DIR}/${script}" ] && [ ! -x "${SCRIPT_DIR}/${script}" ]; then
            non_executable="$non_executable ${SCRIPT_DIR}/${script}"
        fi
        if [ -f "${SHELL_DIR}/${script}" ] && [ ! -x "${SHELL_DIR}/${script}" ]; then
            non_executable="$non_executable ${SHELL_DIR}/${script}"
        fi
    done
    if [ -n "$non_executable" ]; then
        log_error "Non-executable scripts detected:$non_executable"
        log_error "Run 'chmod +x /config/custom_components/ookla_speedtest/shell/*.sh' and try again."
        exit 1
    fi
}

# Function to detect architecture
detect_arch() {
    local detected_arch=""
    
    # Method 1: Check dpkg (Debian/Ubuntu/Raspbian/HAOS)
    if command -v dpkg >/dev/null 2>&1; then
        local dpkg_arch
        dpkg_arch=$(dpkg --print-architecture)
        case "$dpkg_arch" in
            amd64) detected_arch="x86_64" ;;
            arm64) detected_arch="aarch64" ;;
            armhf) detected_arch="armhf" ;;
            armel) detected_arch="armel" ;;
            i386) detected_arch="i386" ;;
        esac
    fi
    
    # Method 2: Check apk (Alpine)
    if [ -z "$detected_arch" ] && command -v apk >/dev/null 2>&1; then
        local apk_arch
        apk_arch=$(apk --print-arch)
        case "$apk_arch" in
            x86_64) detected_arch="x86_64" ;;
            aarch64) detected_arch="aarch64" ;;
            armv7) detected_arch="armhf" ;;
            x86) detected_arch="i386" ;;
        esac
    fi

    # Method 3: Fallback to uname -m with bitness check
    if [ -z "$detected_arch" ]; then
        local uname_arch
        uname_arch=$(uname -m)
        local bitness="64"
        if command -v getconf >/dev/null 2>&1; then
            bitness=$(getconf LONG_BIT)
        fi
        
        case "$uname_arch" in
            x86_64)
                if [ "$bitness" = "32" ]; then detected_arch="i386"; else detected_arch="x86_64"; fi
                ;;
            aarch64)
                if [ "$bitness" = "32" ]; then detected_arch="armhf"; else detected_arch="aarch64"; fi
                ;;
            armv7l|armv7)
                detected_arch="armhf" # Assume armhf for armv7
                ;;
            armv6l|arm)
                detected_arch="armel"
                ;;
            i*86)
                detected_arch="i386"
                ;;
            *)
                detected_arch="$uname_arch"
                ;;
        esac
    fi
    echo "$detected_arch"
}

# Function to download speedtest.bin
download_speedtest_bin() {
    local arch
    arch=$(detect_arch)
    local url=""
    local filename="speedtest.tgz"

    echo "Detected architecture: $arch"

    case "$arch" in
        x86_64)
            url="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz"
            ;;
        armhf)
            url="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-armhf.tgz"
            ;;
        armel)
            url="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-armel.tgz"
            ;;
        aarch64)
            url="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-aarch64.tgz"
            ;;
        i386)
            url="https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-i386.tgz"
            ;;
        *)
            log_error "Unsupported architecture ($arch)."
            log_error "Manually download the speedtest-cli binary from https://www.speedtest.net/apps/cli, rename it to speedtest.bin, and place it in ${SHELL_DIR}."
            exit 1
            ;;
    esac

    echo "Downloading speedtest-cli for $arch from $url..."
    if ! curl -f -L -o "/tmp/$filename" "$url"; then
        log_error "Failed to download speedtest-cli from $url."
        log_error "Check your internet connection or manually download the binary."
        exit 1
    fi

    echo "Extracting speedtest-cli..."
    # Extract to a temp dir to handle structure
    mkdir -p "/tmp/speedtest_extract"
    if ! tar -xzf "/tmp/$filename" -C "/tmp/speedtest_extract" 2>/dev/null; then
        log_error "Failed to extract speedtest-cli from /tmp/$filename."
        rm -f "/tmp/$filename"
        rm -rf "/tmp/speedtest_extract"
        exit 1
    fi
    
    # Locate the binary (it might be in root or subfolder)
    local binary_path
    binary_path=$(find "/tmp/speedtest_extract" -name "speedtest" -type f | head -n 1)
    
    if [ -z "$binary_path" ]; then
        log_error "Could not find 'speedtest' binary in the downloaded archive."
        rm -f "/tmp/$filename"
        rm -rf "/tmp/speedtest_extract"
        exit 1
    fi

    mv "$binary_path" "${SHELL_DIR}/speedtest.bin"
    rm -f "/tmp/$filename"
    rm -rf "/tmp/speedtest_extract"
    
    chmod +x "${SHELL_DIR}/speedtest.bin"
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

# Check shell scripts are executable
check_executable_permissions

# Copy shell scripts to /config/shell if not already present
echo "Copying shell scripts to ${SHELL_DIR}..."
if [ -d "${SCRIPT_DIR}" ]; then
    for script in launch_speedtest.sh list_servers.sh; do
        if [ ! -f "${SHELL_DIR}/${script}" ]; then
            cp "${SCRIPT_DIR}/${script}" "${SHELL_DIR}/" || {
                log_error "Failed to copy ${script} to ${SHELL_DIR}."
                exit 1
            }
            chmod +x "${SHELL_DIR}/${script}"
        else
            echo "${script} already exists in ${SHELL_DIR}, skipping copy."
            chmod +x "${SHELL_DIR}/${script}"
        fi
    done
else
    log_error "Integration shell directory (${SCRIPT_DIR}) not found. Ensure the integration is installed."
    exit 1
fi

# Check if speedtest.bin exists and works
if [ -f "${SHELL_DIR}/speedtest.bin" ]; then
    echo "Verifying existing speedtest.bin..."
    # Attempt to execute the binary to check for Exec format error
    if ! "${SHELL_DIR}/speedtest.bin" --version >/dev/null 2>&1; then
        echo "Existing speedtest.bin is invalid or incompatible (Exec format error?). Removing it..."
        rm -f "${SHELL_DIR}/speedtest.bin"
    else
        echo "Existing speedtest.bin is valid."
    fi
fi

# Download speedtest.bin if not present
if [ ! -f "${SHELL_DIR}/speedtest.bin" ]; then
    download_speedtest_bin
else
    echo "speedtest.bin already exists in ${SHELL_DIR}, skipping download."
fi

# Check speedtest.bin is executable
echo "Checking executable permissions for speedtest.bin..."
if [ ! -x "${SHELL_DIR}/speedtest.bin" ]; then
    log_error "speedtest.bin is not executable."
    log_error "Run 'chmod +x /config/shell/speedtest.bin' manually."
    exit 1
fi

# Accept EULA for speedtest.bin
echo "Accepting Ookla EULA for speedtest.bin..."
"${SHELL_DIR}/speedtest.bin" --accept-license --accept-gdpr >/dev/null 2>&1 || {
    echo "Warning: Failed to accept EULA. This may not affect functionality."
}

echo "Setup complete! Restart Home Assistant to apply changes."