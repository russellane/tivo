"""TivoRemote.

Hand-held device that controls Tivo set-top devices remotely.

See https://github.com/RogueProeliator/IndigoPlugin-TiVo-Network-Remote/blob/master/Documentation/TiVo_TCP_Network_Remote_Control_Protocol.pdf  # noqa
"""

import curses
import re
import socket
import threading

import libcurses
from loguru import logger

from tivo.core import TivoCore
from tivo.device import TivoDevice
from tivo.ui import TivoUI


class TivoRemote:
    """Hand-held device that controls Tivo set-top devices remotely."""

    # pylint: disable=too-few-public-methods

    def __init__(self, core: TivoCore) -> None:
        """Initialize."""

        self.core = core

        # Add devices from config file.

        if identities := self.core.config.get("identity"):
            for identity, host in identities.items():
                device = TivoDevice(identity=identity, host=host)
                logger.info("{!r} Configured device", device.host)
                self.core.add_device(device)

    def run_application(self) -> None:
        """Run full-screen interactive application."""

        libcurses.wrapper(self._run_app)

    def _run_app(self, stdscr: curses.window) -> None:
        """Run application in curses main window `stdscr`."""

        # Listen for devices, update display.
        thread = threading.Thread(name="listener", target=self._listen_for_devices, daemon=True)
        thread.start()

        # Read keyboard/mouse, update display.
        threading.current_thread().name = "console"
        ui = TivoUI(self.core, stdscr)
        ui.main_menu()

    def _listen_for_devices(self) -> None:
        """Docstring."""

        # tivoconnect=1
        # swversion=20.7.4d.RC2-746-2-746
        # method=broadcast
        # identity=7460001902767F2
        # machine=DVR 67F2
        # platform=tcd/Series4
        # services=TiVoMediaServer:80/http

        beacon = 2190
        # sent by tivo devices
        regex = re.compile(r"identity=(?P<identity>[^\n]+)\n.*machine=(?P<machine>[^\n]+)")
        # extension: sent by our tivo device emulator.
        regex2 = re.compile(r"port=(?P<port>[^\n]+)")
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

            if match := regex2.search(msg):
                # sent from our emulator.
                port = int(match.group("port"))
            else:
                # sent from an actual tivo device.
                port = None

            if (device := self.core.get_device_by_name(identity)) is None:
                device = TivoDevice(
                    identity=identity,
                    machine=machine,
                    address=address,
                    port=port,
                )
                logger.info("{!r} New device", device.host)
                self.core.add_device(device)

            logger.debug("{!r} Hello", device.host)
            device.handle_hello_event(
                identity=identity,
                machine=machine,
                address=address,
                port=port,
            )
            if self.core.ui_update_status_callback:
                self.core.ui_update_status_callback()
