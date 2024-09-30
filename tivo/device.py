"""TivoDevice.

Set-top Tivo device.
"""

import socket
import time

from libcurses.bw import BorderedWindow
from loguru import logger

# https://github.com/RogueProeliator/IndigoPlugin-TiVo-Network-Remote/blob/master/Documentation/TiVo_TCP_Network_Remote_Control_Protocol.pdf


# pylint: disable=too-many-instance-attributes
class TivoDevice:
    """Tivo Device."""

    screens = ["LIVETV", "TIVO", "NOWPLAYING", "GUIDE"]
    timeout = 2.0

    def __init__(
        self,
        identity: str,
        machine: str | None = None,
        address: str | None = None,
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-positional-arguments
        """Init."""

        self.identity = identity
        self.machine = machine
        self.address = address
        self.host = host
        self.port = 31339 if port is None else port

        self._map_host()

        self.window: BorderedWindow | None = None
        self.screen = self.screens[0]  # the screen we think it's on
        self.last_msg_sent: str | None = None
        self.last_msg_rcvd: str | None = None
        self._last_msg_rcvd_time: float = 0
        self.status: str | None = None  # from last response
        self.channel: str | None = None  # from last CH_STATUS response
        self.subchannel: str | None = None  # from last CH_STATUS response
        self.reason: str | None = None  # from last CH_STATUS or CH_FAILED response
        self.sock: socket.socket | None = None  # connection
        self.npings = 0  # number of broadcasts heard from device

    def _map_host(self) -> None:

        if not self.host and self.address:
            # use case: heartbeat from new device.
            #   TivoDevice(identity=identity, machine=machine, address=address)
            try:
                self.host = socket.gethostbyaddr(self.address)[0]
                logger.debug("gethostbyaddr({!r}) => host {!r}", self.address, self.host)
            except socket.herror as err:
                logger.error("{!r} Can't gethostbyaddr; {}", self.address, err)
                self.host = self.address

        elif not self.address and self.host:
            # use case: startup, from config file.
            #   TivoDevice(identity=identity, host=host)
            try:
                self.address = socket.gethostbyname(self.host)
                logger.debug("gethostbyname({!r}) => address {!r}", self.host, self.address)
            except socket.gaierror as err:
                logger.debug("{!r} Can't gethostbyname; {}", self.host, err)
                # wait for beacon

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    @property
    def last_msg_rcvd_time(self) -> str:
        """Return last_msg_rcvd_time formatted for display."""

        if not self._last_msg_rcvd_time:
            return "00:00:00 00:00:00"

        diff = time.strftime("%H:%M:%S", time.gmtime(time.time() - self._last_msg_rcvd_time))
        then = time.strftime("%H:%M:%S", time.localtime(self._last_msg_rcvd_time))
        return f"{diff} ({then})"

    def handle_hello_event(
        self,
        identity: str,
        machine: str,
        address: str,
        port: int | None = None,
    ) -> None:
        """Handle received hello message broadcast from device."""

        self.last_msg_rcvd = "HELLO"
        self._last_msg_rcvd_time = time.time()
        self.npings += 1

        assert self.identity == identity
        if not self.machine:
            self.machine = machine
        if not self.address:
            self.address = address
        if port is not None:
            self.port = port
        self._map_host()
        self.getch()

    def getch(self) -> None:
        """Get current channel."""

        # Connecting to the device causes it to send its current state
        if self.sock:
            self.sock.close()
            self.sock = None
        self._connect()

    def upch(self) -> None:
        """Move up to next channel."""
        self.send_ircode("CHANNELUP")

    def downch(self) -> None:
        """Move down to previous channel."""
        self.send_ircode("CHANNELDOWN")

    def _connect(self) -> None:

        if not self.address:
            logger.warning("{!r} No address yet", self.host)
            return

        assert not self.sock

        logger.trace("{!r} Connecting to TCP {!r}:{!r}", self.host, self.address, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.timeout:
            self.sock.settimeout(self.timeout)

        try:
            self.sock.connect((self.address, self.port))
            logger.debug("{!r} Connected to TCP {!r}:{!r}", self.host, self.address, self.port)

        except socket.timeout:
            logger.warning("{!r} timeout", self.host)
            self.sock.close()
            self.sock = None
            self.status = "Can't connect"
            self.reason = "timeout"
            return

        except socket.herror as err:
            logger.error("{!r}:{!r} Can't connect; {}", self.host, self.port, err)
            self.sock.close()
            self.sock = None
            self.status = "Can't connect"
            self.reason = str(err)
            return

        self._recv()  # should respond with the current channel

    def send_key(self, text: str) -> None:
        """Send key."""

        self._send("KEYBOARD " + text)

    def send_teleport(self, text: str) -> None:
        """Send teleport."""

        assert text.startswith("TELEPORT ")
        self._send(text)
        self._recv()

    def send_ircode(self, text: str) -> None:
        """Send ircode."""

        self._send("IRCODE " + text)
        self._recv()

    def send_setch(self, text: str) -> None:
        """Send setch."""

        self._send("SETCH " + text)
        self._recv()

    def _send(self, msg: str) -> None:

        if not self.sock:
            self._connect()

        if self.sock:
            logger.warning("{!r} Sending {!r}", self.host, msg)
            try:
                self.sock.send((msg + "\r").encode("ASCII"))
                self.last_msg_sent = msg
            except Exception as err:  # noqa
                logger.error("{!r} Can't send; {}", self.host, err)
                self.sock.close()
                self.sock = None

    def _recv(self) -> None:

        if not self.sock:
            return

        try:
            data = self.sock.recv(1024)
            self.last_msg_rcvd = data.decode("ASCII").rstrip()
            self._last_msg_rcvd_time = time.time()
            logger.trace("{!r} Received {!r}", self.host, self.last_msg_rcvd)
            self._parse()

        except socket.timeout:
            logger.warning("{!r} timeout", self.host)
            self.last_msg_rcvd = None
            self.status = "Can't receive"
            self.reason = "timeout"

    def _parse(self) -> None:

        # Expecting one of:
        #   CH_STATUS channel reason
        #   CH_STATUS channel sub-channel reason
        #   CH_FAILED reason

        words = self.last_msg_rcvd.split(" ") if self.last_msg_rcvd else []

        if nwords := len(words):
            if words[0] == "CH_STATUS":
                self.status = words[0]

                if nwords == 3:
                    self.channel = words[1]
                    self.reason = words[2]
                elif nwords == 4:
                    self.channel = words[1]
                    self.subchannel = words[2]
                    self.reason = words[3]

                if self.reason not in ("REMOTE", "LOCAL", "RECORDING"):
                    # haven't seen this and don't know how to produce; squawk but don't fail.
                    logger.warning("{!r} unknown reason {!r}", self.host, self.reason)

                if self.channel:
                    logger.debug(
                        "{!r} status {!r} channel {!r} subchannel {!r}; reason {!r}",
                        self.host,
                        self.status,
                        self.channel,
                        self.subchannel,
                        self.reason,
                    )
                    return

            elif words[0] == "CH_FAILED":
                self.status = words[0]

                if nwords > 1:
                    self.reason = words[1]
                    if self.reason not in (
                        "NO_LIVE",
                        "RECORDING",
                        "MISSING_CHANNEL",
                        "MALFORMED_CHANNEL",
                        "INVALID_CHANNEL",
                    ):
                        # haven't seen this and don't know how to produce; squawk but don't fail.
                        logger.warning("{!r} unknown reason {!r}", self.host, self.reason)
                    logger.error(
                        "{!r} status {!r} reason {!r}", self.host, self.status, self.reason
                    )
                    return

            elif words[0] == "LIVETV_READY":
                self.status = words[0]
                logger.success("{!r} status {!r}", self.host, self.status)
                return

            elif words[0] in (
                "MISSING_TELEPORT_NAME",
                "INVALID_KEY",  # undocumented, seen in the wild
            ):
                self.status = words[0]
                logger.error("{!r} status {!r}", self.host, self.status)
                return

            elif words[0] in self.screens:
                self.screen = words[0]

        logger.error("{!r} Can't parse {!r}", self.host, self.last_msg_rcvd)
        self.status = "ERROR"
