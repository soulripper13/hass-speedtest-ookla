import asyncio
import aiohttp
import os
import stat
import logging
import zipfile
import io
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, DOWNLOAD_URL, BINARY_PATH

_LOGGER = logging.getLogger(__name__)

class SpeedtestRtCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session: aiohttp.ClientSession):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=1))
        self.session = session

    async def _async_update_data(self):
        if not os.path.exists(BINARY_PATH):
            _LOGGER.info("Downloading QMS speedtest binary from %s", DOWNLOAD_URL)
            await self._download_binary()

        proc = await asyncio.create_subprocess_exec(
            BINARY_PATH, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if stderr:
            _LOGGER.warning("Speedtest error output: %s", stderr.decode())

        return self._parse_output(stdout.decode())

    async def _download_binary(self):
        async with self.session.get(DOWNLOAD_URL) as resp:
            data = await resp.read()

        # Extract the binary from the zip archive
        os.makedirs(os.path.dirname(BINARY_PATH), exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(os.path.dirname(BINARY_PATH))

        # Make the extracted binary executable
        if os.path.exists(BINARY_PATH):
            os.chmod(BINARY_PATH, os.stat(BINARY_PATH).st_mode | stat.S_IEXEC)
            _LOGGER.info("QMS speedtest binary downloaded and made executable.")
        else:
            _LOGGER.error("Failed to find extracted binary at %s", BINARY_PATH)

    def _parse_output(self, text: str):
        result = {}
        for line in text.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                result[key.strip()] = val.strip()
        _LOGGER.debug("Parsed speedtest output: %s", result)
        return result
