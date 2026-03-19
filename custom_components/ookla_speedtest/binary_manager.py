"""Setup module for Ookla Speedtest binary — replaces setup_speedtest.sh."""

import logging
import os
import platform
import shutil
import stat
import subprocess
import tarfile
import tempfile
import urllib.request

from homeassistant.core import HomeAssistant

from .const import SPEEDTEST_BIN_PATH

_LOGGER = logging.getLogger(__name__)

BIN_DIR = os.path.dirname(SPEEDTEST_BIN_PATH)
SPEEDTEST_VERSION = "1.2.0"
DOWNLOAD_BASE = "https://install.speedtest.net/app/cli"

# Legacy path used by previous versions
_OLD_SHELL_DIR = "/config/shell"


def detect_arch() -> str:
    """Detect system architecture and return Ookla's naming convention.

    Returns one of: x86_64, aarch64, armhf, armel, i386.
    Raises RuntimeError if architecture is unsupported.
    """
    machine = platform.machine().lower()

    arch_map = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "aarch64": "aarch64",
        "arm64": "aarch64",
        "armv7l": "armhf",
        "armv7": "armhf",
        "armv6l": "armel",
        "arm": "armel",
        "i386": "i386",
        "i486": "i386",
        "i586": "i386",
        "i686": "i386",
    }

    arch = arch_map.get(machine)
    if arch is None:
        raise RuntimeError(
            f"Unsupported architecture: {machine}. "
            "Manually download the speedtest binary from https://www.speedtest.net/apps/cli, "
            f"rename it to speedtest.bin, and place it in {BIN_DIR}."
        )
    return arch


def _download_and_extract(arch: str) -> None:
    """Download the speedtest tarball for the given arch and extract the binary."""
    url = f"{DOWNLOAD_BASE}/ookla-speedtest-{SPEEDTEST_VERSION}-linux-{arch}.tgz"
    _LOGGER.info("Downloading speedtest binary for %s from %s", arch, url)

    with tempfile.TemporaryDirectory() as tmpdir:
        tgz_path = os.path.join(tmpdir, "speedtest.tgz")
        urllib.request.urlretrieve(url, tgz_path)

        with tarfile.open(tgz_path, "r:gz") as tar:
            tar.extractall(tmpdir)

        # Find the speedtest binary inside the extracted files
        binary_path = None
        for root, _dirs, files in os.walk(tmpdir):
            if "speedtest" in files:
                binary_path = os.path.join(root, "speedtest")
                break

        if binary_path is None:
            raise RuntimeError("Could not find 'speedtest' binary in the downloaded archive.")

        shutil.move(binary_path, SPEEDTEST_BIN_PATH)
        os.chmod(SPEEDTEST_BIN_PATH, os.stat(SPEEDTEST_BIN_PATH).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    _LOGGER.info("Speedtest binary installed to %s", SPEEDTEST_BIN_PATH)


def _binary_is_valid() -> bool:
    """Check if the existing binary runs successfully."""
    try:
        subprocess.run(
            [SPEEDTEST_BIN_PATH, "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


def _accept_license() -> None:
    """Accept Ookla license/GDPR by running the binary with the relevant flags."""
    try:
        subprocess.run(
            [SPEEDTEST_BIN_PATH, "--accept-license", "--accept-gdpr", "--version"],
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        _LOGGER.warning("Could not accept Ookla license: %s", exc)


_ORPHANED_FILES = [
    os.path.join(_OLD_SHELL_DIR, name)
    for name in ("launch_speedtest.sh", "list_servers.sh", "setup_speedtest.sh", "speedtest.bin")
]


def _cleanup_legacy_files() -> None:
    """Remove files left behind by previous versions in /config/shell/."""
    for path in _ORPHANED_FILES:
        try:
            if os.path.isfile(path):
                os.remove(path)
                _LOGGER.info("Removed legacy file: %s", path)
        except OSError as exc:
            _LOGGER.debug("Could not remove %s: %s", path, exc)


def _setup_speedtest_sync() -> None:
    """Synchronous setup: download binary if needed, accept license."""
    os.makedirs(BIN_DIR, exist_ok=True)
    _cleanup_legacy_files()

    # If binary exists, verify it works (catches arch mismatch after migration)
    if os.path.isfile(SPEEDTEST_BIN_PATH):
        if _binary_is_valid():
            _LOGGER.debug("Existing speedtest binary is valid")
            _accept_license()
            return
        _LOGGER.warning("Existing speedtest binary is invalid, re-downloading")
        os.remove(SPEEDTEST_BIN_PATH)

    arch = detect_arch()
    _download_and_extract(arch)
    _accept_license()


async def async_setup_speedtest(hass: HomeAssistant) -> None:
    """Set up the speedtest binary (async wrapper).

    Creates the bin directory inside the integration folder, downloads the
    correct binary if missing or invalid, cleans up legacy /config/shell/ files,
    and accepts the Ookla license/GDPR.
    """
    await hass.async_add_executor_job(_setup_speedtest_sync)
