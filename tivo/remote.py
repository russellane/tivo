"""TivoRemote.

Hand-held device that controls Tivo set-top devices remotely.
"""

import argparse
import re
import socket
import threading
from typing import Dict

import libcurses
from loguru import logger

from tivo.device import TivoDevice
from tivo.ui import TivoUI

# https://github.com/RogueProeliator/IndigoPlugin-TiVo-Network-Remote/blob/master/Documentation/TiVo_TCP_Network_Remote_Control_Protocol.pdf


class TivoRemote:
    """Hand-held device that controls Tivo set-top devices remotely."""

    def __init__(self, options: argparse.Namespace, config: {}) -> None:
        """Initialize TivoRemote given `options` and `config`."""

        self.options = options  # from cli
        self.config = config  # from cli
        self.devices: Dict(TivoDevice) = {}
        self.ui: TivoUI = None

        if identities := self.config.get("identity"):
            for identity, host in identities.items():
                self.devices[identity] = TivoDevice(identity=identity, host=host)

    def getdevicebyname(self, name: str) -> TivoDevice:
        """Return the device with the matching `name`."""

        for device in self.devices.values():
            if name in (device.identity, device.machine, device.address, device.host):
                return device
        return None

    def control(self):
        """Operate remote."""
        libcurses.wrapper(self._control)

    def _control(self, stdscr):
        """Operate remote in curses main window `stdscr`."""

        # Listen for devices, update display.
        thread = threading.Thread(name="listener", target=self._listen_for_devices, daemon=True)
        thread.start()

        # Read keyboard/mouse, update display.
        threading.current_thread().name = "console"
        self.ui = TivoUI(self, stdscr)
        self.ui.main_menu()

    def _listen_for_devices(self):

        # tivoconnect=1
        # swversion=20.7.4d.RC2-746-2-746
        # method=broadcast
        # identity=7460001902767F2
        # machine=DVR 67F2
        # platform=tcd/Series4
        # services=TiVoMediaServer:80/http'

        beacon = 2190
        regex = re.compile(r"identity=(?P<identity>[^\n]+)\n.*machine=(?P<machine>[^\n]+)")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", beacon))
        logger.info(f"Listening on UDP port {beacon!r}")

        while True:
            try:
                data, address = sock.recvfrom(1024)
            except socket.timeout:
                logger.debug("timeout")
                return

            logger.trace(f"data {data!r}, address {address!r}")
            msg = data.decode("ASCII").rstrip()

            if not (match := regex.search(msg)):
                logger.error("Can't parse {!r}", msg)
                continue

            identity = match.group("identity")
            machine = match.group("machine")
            address = address[0]

            if (device := self.devices.get(identity)) is None:
                device = TivoDevice(identity=identity, machine=machine, address=address)
                logger.info("{!r} New device", device.host)
                self.devices[identity] = device
                if self.ui:
                    self.ui.add_device(device)

            logger.debug("{!r} Hello", device.host)
            device.handle_hello_event(identity=identity, machine=machine, address=address)
            if self.ui:
                self.ui.update_status()
