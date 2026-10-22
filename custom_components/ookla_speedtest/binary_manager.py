"""Setup module for Ookla Speedtest binary — replaces setup_speedtest.sh."""

import asyncio
import logging
import os
import platform
import shutil
import ssl
import stat
import subprocess
import tarfile
import tempfile
import urllib.request

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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


def _check_existing_binary() -> bool:
    """Check if an existing binary is already valid and ready to run."""
    os.makedirs(BIN_DIR, exist_ok=True)
    _cleanup_legacy_files()

    if os.path.isfile(SPEEDTEST_BIN_PATH):
        try:
            os.chmod(
                SPEEDTEST_BIN_PATH,
                os.stat(SPEEDTEST_BIN_PATH).st_mode
                | stat.S_IXUSR
                | stat.S_IXGRP
                | stat.S_IXOTH,
            )
        except OSError:
            pass

        if _binary_is_valid():
            _LOGGER.debug("Existing speedtest binary is valid")
            _accept_license()
            return True
        _LOGGER.warning("Existing speedtest binary is invalid, re-downloading")
        try:
            os.remove(SPEEDTEST_BIN_PATH)
        except OSError:
            pass

    return False


async def _async_download_file(
    hass: HomeAssistant,
    url: str,
    dest_path: str,
    max_retries: int = 3,
) -> None:
    """Download remote archive using aiohttp with retries, and fallbacks to curl and urllib."""
    last_error: Exception | None = None

    # Method 1: aiohttp via Home Assistant's managed client session
    try:
        session = async_get_clientsession(hass)
        timeout = aiohttp.ClientTimeout(total=90, connect=15)
        headers = {
            "User-Agent": "HomeAssistant-OoklaSpeedtest (compatible; HomeAssistant)",
            "Accept": "*/*",
        }

        for attempt in range(1, max_retries + 1):
            try:
                _LOGGER.debug(
                    "Downloading speedtest binary from %s (attempt %d/%d via aiohttp)",
                    url,
                    attempt,
                    max_retries,
                )
                async with session.get(url, headers=headers, timeout=timeout) as resp:
                    if resp.status != 200:
                        raise RuntimeError(
                            f"HTTP status {resp.status} received when downloading from {url}"
                        )
                    with open(dest_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(64 * 1024):
                            f.write(chunk)

                if os.path.isfile(dest_path) and os.path.getsize(dest_path) > 0:
                    _LOGGER.debug("Successfully downloaded binary archive via aiohttp")
                    return
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as exc:
                last_error = exc
                _LOGGER.warning(
                    "aiohttp download attempt %d/%d failed: %s",
                    attempt,
                    max_retries,
                    exc,
                )
                if os.path.exists(dest_path):
                    try:
                        os.remove(dest_path)
                    except OSError:
                        pass
                if attempt < max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))
    except Exception as exc:
        last_error = exc
        _LOGGER.warning("aiohttp session download encountered an error: %s", exc)

    # Method 2: System curl fallback (handles tricky TLS/SSL configurations via libcurl)
    if shutil.which("curl"):
        _LOGGER.info("Attempting download fallback using system curl...")
        try:
            proc = await asyncio.create_subprocess_exec(
                "curl",
                "-fsSL",
                "--retry",
                "2",
                "--retry-delay",
                "1",
                "--max-time",
                "90",
                "-A",
                "HomeAssistant-OoklaSpeedtest",
                url,
                "-o",
                dest_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if (
                proc.returncode == 0
                and os.path.isfile(dest_path)
                and os.path.getsize(dest_path) > 0
            ):
                _LOGGER.info(
                    "Successfully downloaded binary archive using curl fallback"
                )
                return
            _LOGGER.warning(
                "curl fallback failed with code %d: %s",
                proc.returncode,
                stderr.decode(errors="replace").strip(),
            )
        except Exception as exc:
            last_error = exc
            _LOGGER.warning("curl fallback execution failed: %s", exc)

    # Method 3: urllib fallback in executor (with explicit User-Agent and SSL context)
    _LOGGER.info("Attempting download fallback using urllib...")
    try:
        def _urllib_download():
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; HomeAssistant-OoklaSpeedtest)"
                    )
                },
            )
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, context=ctx, timeout=60) as resp, open(
                dest_path, "wb"
            ) as out:
                shutil.copyfileobj(resp, out)

        await hass.async_add_executor_job(_urllib_download)
        if os.path.isfile(dest_path) and os.path.getsize(dest_path) > 0:
            _LOGGER.info("Successfully downloaded binary archive using urllib fallback")
            return
    except Exception as exc:
        last_error = exc
        _LOGGER.warning("urllib download fallback failed: %s", exc)

    raise RuntimeError(
        f"Failed to download speedtest binary from {url} after all attempts: {last_error}"
    )


def _extract_and_install(tgz_path: str) -> None:
    """Extract tarball and install the binary."""
    with tempfile.TemporaryDirectory() as extract_dir:
        with tarfile.open(tgz_path, "r:gz") as tar:
            if hasattr(tarfile, "data_filter"):
                tar.extractall(extract_dir, filter="data")
            else:
                tar.extractall(extract_dir)

        # Find the speedtest binary inside the extracted files
        binary_path = None
        for root, _dirs, files in os.walk(extract_dir):
            if "speedtest" in files:
                binary_path = os.path.join(root, "speedtest")
                break

        if binary_path is None:
            raise RuntimeError(
                "Could not find 'speedtest' binary in the downloaded archive."
            )

        os.makedirs(BIN_DIR, exist_ok=True)
        shutil.move(binary_path, SPEEDTEST_BIN_PATH)
        os.chmod(
            SPEEDTEST_BIN_PATH,
            os.stat(SPEEDTEST_BIN_PATH).st_mode
            | stat.S_IXUSR
            | stat.S_IXGRP
            | stat.S_IXOTH,
        )

    _accept_license()

    if not _binary_is_valid():
        raise RuntimeError(
            f"Installed speedtest binary at {SPEEDTEST_BIN_PATH} failed validation (--version)."
        )

    _LOGGER.info("Speedtest binary installed successfully to %s", SPEEDTEST_BIN_PATH)


def _setup_speedtest_sync() -> None:
    """Synchronous setup: check binary, download if needed (legacy fallback)."""
    if _check_existing_binary():
        return
    arch = detect_arch()
    url = f"{DOWNLOAD_BASE}/ookla-speedtest-{SPEEDTEST_VERSION}-linux-{arch}.tgz"
    with tempfile.TemporaryDirectory() as tmpdir:
        tgz_path = os.path.join(tmpdir, "speedtest.tgz")
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; HomeAssistant-OoklaSpeedtest)"
                )
            },
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp, open(
            tgz_path, "wb"
        ) as out:
            shutil.copyfileobj(resp, out)
        _extract_and_install(tgz_path)


async def async_setup_speedtest(hass: HomeAssistant) -> None:
    """Set up the speedtest binary.

    Creates the bin directory inside the integration folder, verifies existing binary,
    downloads the correct binary if missing or invalid using aiohttp/fallbacks,
    cleans up legacy files, and accepts the Ookla license/GDPR.
    """
    # 1. Clean legacy files and check if existing binary is already valid
    is_valid = await hass.async_add_executor_job(_check_existing_binary)
    if is_valid:
        return

    # 2. Detect architecture
    arch = detect_arch()
    url = f"{DOWNLOAD_BASE}/ookla-speedtest-{SPEEDTEST_VERSION}-linux-{arch}.tgz"
    _LOGGER.info("Setting up speedtest binary for %s from %s", arch, url)

    # 3. Download tarball to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tgz_path = os.path.join(tmpdir, "speedtest.tgz")
        await _async_download_file(hass, url, tgz_path)

        # 4. Extract and install in executor
        await hass.async_add_executor_job(_extract_and_install, tgz_path)
