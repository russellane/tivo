"""Tivo Device Emulator.

This program emulates a TiVo set-top device, which:
    1. Sends a UDP broadcast message every minute or so,
    2. Listens for TCP connections, and responds to requests.

This is for testing basic features of the client application
without an actual device.
"""

from __future__ import annotations

import random
import socket
import sys
from dataclasses import dataclass, field
from threading import Thread, current_thread
from time import sleep
from typing import ClassVar

from loguru import logger

from tivo.cmd import TivoCmd


class TivoEmulatorCmd(TivoCmd):
    """Tivo `emulator` command class."""

    def init_command(self) -> None:
        """Initialize Tivo `emulator` command instance."""

        parser = self.add_subcommand_parser(
            "emulator",
            help="run a TiVo set-top device emulator",
            description=__doc__,
        )

        arg = parser.add_argument(
            "-n",
            "--num_devices",
            type=int,
            default=1,
            help="Number of TiVo devices to emulate",
        )
        self.cli.add_default_to_help(arg, parser)

        arg = parser.add_argument(
            "-s",
            "--stagger",
            type=float,
            default=0,
            help=str(
                "Delay the start of each device's TCP-listener in seconds. "
                "Meaningful when NUM_DEVICES is greater than 1"
            ),
        )
        self.cli.add_default_to_help(arg, parser)

        arg = parser.add_argument(
            "-i",
            "--interval",
            type=float,
            default=60,
            help="Interval between broadcasts in seconds",
        )
        self.cli.add_default_to_help(arg, parser)

        arg = parser.add_argument(
            "-r",
            "--randomize",
            action="store_true",
            help="Randomize the interval, by 50-150%%, between each device's broadcast",
        )
        self.cli.add_default_to_help(arg, parser)

    def run(self) -> None:
        """Perform the command."""

        try:
            logger.remove()
        except ValueError:
            ...
        logger.add(
            sys.stderr,
            format=" | ".join(
                [
                    "<green>{time:HH:mm:ss.SSS}</green>",
                    "<level>{level: <8}</level>",
                    "<cyan>{thread.name}:{function}:{line}</cyan>",
                    "<level>{message}</level>",
                ]
            ),
            colorize=True,
            level="TRACE",
        )

        if self.options.num_devices < 1 or self.options.num_devices > Device.max_num_devices:
            self.cli.parser.error(f"num_devices must from 1 to {Device.max_num_devices}.")

        current_thread().name = "main"

        threads = []
        for device_id in range(1, self.options.num_devices + 1):

            # Each call to the constructor creates a unique device.
            device = Device(device_id)
            logger.info(f"Starting {device}")

            # Create a thread to run the device.
            thread = Thread(
                name=f"device-{device_id}",
                target=self.emulate_device,
                args=(device,),
                daemon=True,
            )
            threads.append(thread)
            thread.start()

            # Stagger the creation of each device/thread by a fixed amount.
            if self.options.stagger:
                sleep(self.options.stagger)

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            logger.info("\nStopping all devices...")

    def emulate_device(self, device: Device) -> None:
        """Create thread for tcp-server, and thread for hello broadcaster."""

        logger.info("Starting listener")

        tcp_thread = Thread(
            name=f"listener-{device.device_id}",
            target=self.tcp_listener,
            args=(device,),
            daemon=True,
        )
        tcp_thread.start()

        current_thread().name = f"beacon-{device.device_id}"
        self.broadcast_hello(device)

    def tcp_listener(self, device: Device) -> None:
        """Create listener socket, and create thread to handle each connection."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", device.tcp_port))
            s.listen()
            logger.info(f"TCP Listener started on port {device.tcp_port}")
            while True:
                device.sock, device.addr = s.accept()
                Thread(
                    name=f"server-{device.device_id}",
                    target=self.handle_tcp_connection,
                    args=(device,),
                ).start()

    def handle_tcp_connection(self, device: Device) -> None:
        """Handle new tcp connection on `device.sock`."""

        logger.trace(f"New connection from {device.addr}")

        # Respond to the connect with the current channel.
        self.send_channel_status(device)

        # Then enter a REPL.
        while True:
            try:
                data = device.sock.recv(1024)
                if not data:
                    break
            except socket.timeout:
                logger.warning("Timeout")
                break
            except ConnectionResetError:
                logger.error("Disconnected")
                break
            except OSError as err:
                logger.error(err)
                break

            message = data.decode("ASCII").rstrip()
            logger.info(f"Received {message!r}")

            if message == "IRCODE CHANNELUP":
                device.channel += 1
            elif message == "IRCODE CHANNELDOWN":
                device.channel -= 1
            else:
                logger.info(f"Unhandled {message!r}")

            self.send_channel_status(device)

        # device.sock.close()

    def send_channel_status(self, device: Device) -> None:
        """Docstring."""

        message = f"CH_STATUS {device.channel} REMOTE"
        logger.debug(f"Sending {message!r}")

        try:
            device.sock.send(message.encode())
        except OSError as err:
            logger.error(err)

    def broadcast_hello(self, device: Device) -> None:
        """Broadcast a 'hello' message peridically."""

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        port = 2190
        logger.info(f"Starting beacon on port {port}")

        while True:
            sock.sendto(device.hello_message, ("<broadcast>", port))
            logger.debug("Sent broadcast")

            if self.options.randomize:
                sleep_time = random.uniform(
                    self.options.interval * 0.5, self.options.interval * 1.5
                )
            elif self.options.interval == 0:
                sleep_time = device.device_id
            else:
                sleep_time = self.options.interval

            sleep(sleep_time)


@dataclass
class Device:
    """Docstring."""

    _identities: ClassVar[list[str]] = [
        "7460001902767F2",
        "A9000019022E28B",
        "75000019042F2CD",
        "66600099999AA11",
        "66600099999BB22",
        "66600099999CC33",
        "66600099999DD44",
    ]
    max_num_devices: ClassVar[int] = len(_identities)

    device_id: int
    identity: str = field(init=False)
    channel: int = field(init=False)
    tcp_port: int = field(init=False)
    sock: socket.socket = field(init=False, repr=False)
    addr: tuple[str, int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Docstring."""

        self.identity = self._identities[self.device_id - 1]
        self.channel = ((self.device_id) * 100) + 1  # 101, 201, 301, ...
        self.tcp_port = 31339 + self.device_id - 1  # 31339, 31340, 31341, ...

        self.hello_message = "\n".join(
            [
                "tivoconnect=1",
                "swversion=20.7.4d.RC2-746-2-746",
                "method=broadcast",
                f"identity={self.identity}",
                f"machine=DVR {self.identity[-4:]}",
                "platform=tcd/Series4",
                "services=TiVoMediaServer:80/http",
                # our extension; this device's tcp_listener port.
                f"port={self.tcp_port}",
            ]
        ).encode()
