"""Tivo Device Emulator.

This program emulates a TiVo set-top device, which:
    1. Sends a UDP broadcast message every minute or so,
    2. Listens for TCP connections, and responds to requests.
"""

import argparse
import random
import socket
import time
from dataclasses import dataclass, field
from threading import Thread


@dataclass
class Device:
    """Docstring."""

    device_id: int
    identity: str
    channel: int
    tcp_port: int
    conn: socket.socket = field(init=False)
    addr: tuple[str, int] = field(init=False)

    def __post_init__(self) -> None:
        """Docstring."""

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


class Emulator:
    """Docstring."""

    devices: list[Device] = []

    def handle_tcp_connection(self, device: Device) -> None:
        """Docstring."""

        print(f"Device {device.device_id}: New connection from {device.addr}")

        # Respond with the current channel.
        self.send_channel_status(device)

        while True:
            try:
                data = device.conn.recv(1024)
                if not data:
                    break
            except socket.timeout:
                print(f"Device {device.device_id}: Timeout")
                break
            except ConnectionResetError:
                print(f"Device {device.device_id}: Disconnected")
                break

            message = data.decode("ASCII").rstrip()
            print(f"Device {device.device_id}: Received {message!r}")

            if message == "IRCODE CHANNELUP":
                device.channel += 1
            elif message == "IRCODE CHANNELDOWN":
                device.channel -= 1
            else:
                print(f"Device {device.device_id}: Unhandled {'-'*20}> {message!r}")

            self.send_channel_status(device)

        device.conn.close()

    def send_channel_status(self, device: Device) -> None:
        """Docstring."""

        message = f"CH_STATUS {device.channel} REMOTE"
        print(f"Device {device.device_id}: Sending {message!r}")
        device.conn.send(message.encode())

    def tcp_listener(self, device: Device) -> None:
        """Docstring."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", device.tcp_port))
            s.listen()
            print(f"Device {device.device_id}: TCP Listener started on port {device.tcp_port}")
            while True:
                device.conn, device.addr = s.accept()
                Thread(target=self.handle_tcp_connection, args=(device,)).start()

    def send_broadcast(
        self,
        device: Device,
        interval: float,
        randomize: bool,
    ) -> None:
        """Docstring."""

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            sock.sendto(device.hello_message, ("<broadcast>", 2190))
            print(f"Device {device.device_id}: Sent broadcast")
            # print(f"Device {device.device_id}: Sent {device.hello_message!r}")

            if randomize:
                sleep_time = random.uniform(interval * 0.5, interval * 1.5)
            elif interval == 0:
                sleep_times = [1, 2, 3]
                sleep_time = sleep_times[device.device_id - 1]
            else:
                sleep_time = interval

            time.sleep(sleep_time)

    def emulate_device(
        self,
        device: Device,
        interval: float,
        randomize: bool,
    ) -> None:
        """Docstring."""

        tcp_thread = Thread(target=self.tcp_listener, args=(device,))
        tcp_thread.daemon = True
        tcp_thread.start()

        self.send_broadcast(device, interval, randomize)

    def main(self) -> None:
        """Docstring."""

        parser = argparse.ArgumentParser(description="TiVo Set-Top Device Emulator")
        parser.add_argument(
            "-n", "--num_devices", type=int, default=1, help="Number of TiVo devices to emulate"
        )
        parser.add_argument(
            "-i",
            "--interval",
            type=float,
            default=60,
            help="Interval between broadcasts in seconds",
        )
        parser.add_argument(
            "-r",
            "--randomize",
            action="store_true",
            help="Randomize the interval between broadcasts",
        )

        args = parser.parse_args()
        if args.num_devices < 1 or args.num_devices > 3:
            parser.error("num_devices must from 1 to 3.")

        identities = [
            "7460001902767F2",
            "A9000019022E28B",
            "75000019042F2CD",
        ]

        threads = []
        for i in range(args.num_devices):
            device = Device(
                device_id=i + 1,
                identity=identities[i],
                channel=((i + 1) * 100) + 1,  # 101, 201, 301, ...
                tcp_port=31339 + i,
            )
            self.__class__.devices.append(device)

            thread = Thread(
                target=self.emulate_device,
                args=(
                    device,
                    args.interval,
                    args.randomize,
                ),
            )
            thread.daemon = True
            threads.append(thread)
            thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping all devices...")


if __name__ == "__main__":
    Emulator().main()
