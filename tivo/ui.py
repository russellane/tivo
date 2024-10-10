"""TivoUI.

User interface for TiVo remote control.
"""

import curses
import curses.ascii
from typing import Any

from libcurses import LogSink, getkey, getline, preserve_cursor
from libcurses.bw import BorderedWindow
from libcurses.menu import Menu, MenuItem
from libcurses.stack import WindowStack
from loguru import logger

from tivo.core import TivoCore
from tivo.device import TivoDevice


class TivoUI:
    """User Interface."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, core: TivoCore, stdscr: curses.window) -> None:
        """Create user interface on `stdscr`."""

        self.core = core
        self.core.set_ui_add_device_callback(self.add_device)
        self.core.set_ui_update_status_callback(self.update_status)

        # index of the device that has the focus
        self._ifocus: int | None = None

        maxy, maxx = stdscr.getmaxyx()
        padding_y, padding_x = 0, 0
        maxy -= padding_y * 2
        maxx -= padding_x * 2
        begin_y = padding_y
        begin_x = padding_x

        # build screen with two full-height columns

        ncols1 = 37
        self.ncols2 = maxx - ncols1
        if self.ncols2 < 3:
            raise RuntimeError(f"Screen is {abs(self.ncols2-3)} columns too narrow")

        # column 1: menu window
        self.menu_win = BorderedWindow(maxy, ncols1, begin_y, begin_x)

        # column 2: stacked status windows, logger window
        self.wstack = WindowStack(neighbor_left=self.menu_win, padding_y=padding_y)
        self.status_window_nlines = 7

        # logger window
        # nlines=0 consumes all remaining lines
        self.logger_win = self.wstack.append(0, self.ncols2)

        # start logging to the logger window
        self.logwin = LogSink(self.logger_win.w)
        self.logwin.set_location("{module}:{function}:{line}")
        self.logwin.set_verbose(self.core.options.verbose)

        # device status window fields, attributes of TivoDevice(object), in its order.

        self._attrs = {
            "host": {"key": "Host", "width": 15},  # len('192.168.123.123')
            "machine": {"key": "Machine", "width": 15},
            "identity": {"key": "Identity", "width": 15},
            "address": {"key": "Address", "width": 15},
            "port": {"key": "Port", "width": 5},
            "timeout": {"key": "Timeout", "width": 5},
            "screen": {"key": "Screen", "width": len("NOWPLAYING")},
            "last_msg_sent": {"key": "Last msg sent", "width": 0},
            "last_msg_rcvd": {"key": "Last msg rcvd", "width": 0},
            "status": {"key": "Status", "width": len("MISSING_TELEPORT_NAME")},
            "channel": {"key": "Channel", "width": 5},
            "subchannel": {"key": "Subchannel", "width": 5},
            "reason": {"key": "Reason", "width": len("MALFORMED_CHANNEL")},
            "npings": {"key": "Pings", "width": 5},
            "last_msg_rcvd_time": {"key": "Last Time", "width": len("hh:mm:ss")},
        }

        # Device status window, displayed in column 2, which is self.ncols2 wide.

        # 3 columns, ordering attributes as we please
        self._cols = [
            ["host", "machine", "identity", "address", "port"],
            ["screen", "channel", "subchannel", "timeout", "npings"],
            ["last_msg_sent", "last_msg_rcvd", "status", "reason", "last_msg_rcvd_time"],
        ]

        self._rows = list(map(list, zip(*self._cols)))  # transpose 2d array
        assert len(self._rows) == self.status_window_nlines - 2  # 2 for borders

        # Each column has 2 subcolumns: a key/value pair.
        # Keys and values are vertically aligned.
        # Determine the widths of each subcolumn.
        # The last column consumes to end of line.

        self._key_widths = []  # of each column
        self._val_widths = []  # of each column
        self._col_gutter = " "  # between the columns
        self._attr_gutter = " "  # between keys and values

        ncols = len(self._cols)

        # widths of all 'key' subcolumns
        for col in range(ncols):
            self._key_widths.append(
                max(len(str(self._attrs[a]["key"])) for a in self._cols[col] if a is not None)
            )

        # widths of all but the last 'value' subcolumns
        for col in range(ncols - 1):
            self._val_widths.append(
                max(int(self._attrs[a]["width"]) for a in self._cols[col] if a is not None)  # type: ignore # noqa
            )

        # width of the last 'value' subcolumn
        self._val_widths.append(
            self.ncols2
            - sum(
                [
                    sum(self._key_widths),
                    sum(self._val_widths),
                    ncols * len(self._attr_gutter),
                    (ncols - 1) * len(self._col_gutter),
                    3,
                ]
            )
        )

        # Add device status windows.
        if self.core.devices:
            for device in self.core.devices.values():
                self.add_device(device)
        else:
            self.redraw()

    def add_device(self, device: TivoDevice) -> None:
        """Add device between last device and logger window."""
        self.wstack.insert(self.status_window_nlines, self.ncols2, -1)
        device.window = self.wstack.windows[-2]
        self.update_status()
        self.redraw()

    @property
    def _focus(self) -> TivoDevice | None:
        """The device that has the focus."""

        if self._ifocus is None:
            return None

        return self.core.devices[list(self.core.devices.keys())[self._ifocus]]

    def update_status(self) -> None:
        """Update the status of all devices."""

        for device in self.core.devices.values():
            self.update_device_status(device)

    def update_device_status(self, device: TivoDevice) -> None:
        """Build status window for device."""

        with preserve_cursor():
            self._update_device_status(device)

    def _update_device_status(self, device: TivoDevice) -> None:
        """Build status window for device."""

        if not device.window:
            return

        bwin = device.window
        bwin.w.clear()

        color_names = curses.color_pair(3)
        color_values = curses.color_pair(1)

        if device == self._focus:
            color_values = curses.color_pair(4)
        else:
            color_names |= curses.A_DIM
            # color_values |= curses.A_BOLD

        for row, _ in enumerate(self._rows):
            bwin.w.move(row, 0)
            for col in range(len(self._cols)):
                #
                attrname = self._rows[row][col]
                if attr := self._attrs.get(attrname):
                    key = str(attr["key"])
                    value = str(getattr(device, attrname))
                else:
                    key = value = ""
                #
                if col > 0:
                    bwin.w.addstr(self._col_gutter, color_values)
                bwin.w.addstr(key.rjust(self._key_widths[col]), color_names)
                bwin.w.addstr(self._attr_gutter, color_names)
                bwin.w.addstr(value.ljust(self._val_widths[col]), color_values)
            #
        #
        # bwin.w.scroll(-1)
        bwin.w.refresh()

    def main_menu(self) -> None:
        """Main menu."""

        menu = Menu(title="Main menu", instructions="Choose")

        menu.add_item("g", "get channel", self._get_channel)

        for screen in TivoDevice.screens:
            menu.add_item(screen[0], f"TELEPORT {screen}", "send_teleport")
            # menu.add_item(screen[0], screen, "send_teleport")

        #             curses        tivo or description action
        menu.add_item("u", "CHANNELUP", "send_ircode")
        menu.add_item("d", "CHANNELDOWN", "send_ircode")
        menu.add_item("c", "CC_ON", "send_ircode")
        menu.add_item("x", "CC_OFF", "send_ircode")
        menu.add_item("e", "EXIT", "send_ircode")
        menu.add_item("+", "VOLUMEUP", "send_key")
        menu.add_item("-", "VOLUMEDOWN", "send_key")
        menu.add_item("m", "MUTE", "send_key")
        menu.add_item(curses.KEY_UP, "UP", "send_key")
        menu.add_item(curses.KEY_DOWN, "DOWN", "send_key")
        menu.add_item(curses.KEY_LEFT, "LEFT", "send_key")
        menu.add_item(curses.KEY_RIGHT, "RIGHT", "send_key")
        menu.add_item(curses.KEY_ENTER, "SELECT", "send_key")
        menu.add_item(ord("\n"), "ENTER", "send_key")
        menu.add_item("s", "Set channel", self._set_channel)
        menu.add_item("i", "IRCODE menu", self._ircode_menu)
        menu.add_item("k", "send Keystrokes", self._keyboard_shell)
        menu.add_item("[", "Previous device", self._prev_device)
        menu.add_item("]", "Next device", self._next_device)
        menu.add_item("t", "Test menu", self._test_menu)
        menu.add_item(ord("\f"), "Redraw", self.redraw)
        menu.add_item(curses.KEY_RESIZE, "Resize", lambda: False)
        menu.add_item(curses.KEY_F2, "INFO", lambda: self._set_verbose(0))
        menu.add_item(curses.KEY_F3, "DEBUG", lambda: self._set_verbose(1))
        menu.add_item(curses.KEY_F4, "TRACE", lambda: self._set_verbose(2))
        menu.add_item(curses.KEY_F5, "ACTION_A", "send_key")
        menu.add_item(curses.KEY_F6, "ACTION_B", "send_key")
        menu.add_item(curses.KEY_F7, "ACTION_C", "send_key")
        menu.add_item(curses.KEY_F8, "ACTION_D", "send_key")
        menu.add_item(curses.KEY_F9, "CLEAR", "send_key")
        menu.add_item("q", "Quit", lambda: True)

        while True:
            self.update_status()
            menu.win = self.menu_win.w
            if not (item := menu.prompt()):
                logger.debug("break not menu.prompt")
                break
            if self._run(item):
                logger.debug("break _run")
                break

    def _run(self, item: MenuItem) -> bool:

        if isinstance(item.payload, str):
            # invoke the named method on the device in focus
            # pylint: disable=no-else-return
            if not self._focus:
                logger.error("No device in focus")
                return False  # continue looping
            else:
                func = getattr(self._focus, item.payload)
                func(item.text)
                return False  # continue looping
        else:
            return bool((item.payload)())

        return True  # stop looping

    def _get_channel(self) -> None:
        """Get current channel."""

        if not self._focus:
            logger.error("No device in focus")
            return

        self._focus.getch()

    def _set_channel(self) -> None:
        """Prompt for channel and change it."""

        if not self._focus:
            logger.error("No device in focus")
            return

        self.menu_win.w.addstr("[^D, Backspace] Enter channel: ")

        if channel := getline(self.menu_win.w):
            self._focus.send_setch(channel)

    def _ircode_menu(self) -> bool:
        """Full list of IRCODE's.

        Other menus, like the main menu, may have duplicates.
        """

        if not self._focus:
            logger.error("No device in focus")
            return False

        menu = Menu(title="IRCODE menu", instructions="Choose IRCODE to send")

        for _ in "0123456789":
            menu.add_item(_, "NUM" + _, "send_ircode")

        for screen in TivoDevice.screens:
            menu.add_item(screen[0], screen, "send_ircode")

        menu.add_item("+", "VOLUMEUP", "send_ircode")
        menu.add_item("-", "VOLUMEDOWN", "send_ircode")
        menu.add_item("m", "MUTE", "send_ircode")
        menu.add_item(curses.KEY_UP, "UP", "send_ircode")
        menu.add_item(curses.KEY_DOWN, "DOWN", "send_ircode")
        menu.add_item(curses.KEY_LEFT, "LEFT", "send_ircode")
        menu.add_item(curses.KEY_RIGHT, "RIGHT", "send_ircode")
        menu.add_item(curses.KEY_ENTER, "SELECT", "send_ircode")
        menu.add_item(ord("\n"), "ENTER", "send_ircode")
        menu.add_item(curses.KEY_RESIZE, "Resize", lambda: False)
        menu.add_item("q", "Quit", lambda x: True)
        # ENTER
        # CLEAR
        # ACTION_A, B, C, D

        menu.win = self.menu_win.w
        if item := menu.prompt():
            return self._run(item)

        return False

    def _keyboard_shell(self) -> None:

        if not self._focus:
            logger.error("No device in focus")
            return

        self.menu_win.w.addstr("[^D] Enter text: ")
        while True:
            if not (key := getkey(self.menu_win.w)):
                break

            if curses.ascii.isalpha(key):
                self.menu_win.w.addch(key)
                self._focus.send_key(chr(key))
            elif _ := self.keymap.get(key):
                self.menu_win.w.addstr(f"<{_}>")
                self._focus.send_key(_)
            else:
                logger.error(f"Can't map: {key!r}")

    keymap = {  # from curses to tivo
        "0": "NUM0",
        "1": "NUM1",
        "2": "NUM2",
        "3": "NUM3",
        "4": "NUM4",
        "5": "NUM5",
        "6": "NUM6",
        "7": "NUM7",
        "8": "NUM8",
        "9": "NUM9",
        "-": "MINUS",
        "+": "PLUS",
        "=": "EQUALS",
        "[": "LBRACKET",
        "]": "RBRACKET",
        "\\": "BACKSLASH",
        ";": "SEMICOLON",
        "“": "QUOTE",
        ",": "COMMA",
        ".": "PERIOD",
        "/": "SLASH",
        "`": "BACKQUOTE",
        "~": "BACKQUOTE",
        " ": "SPACE",
        curses.KEY_UP: "UP",
        curses.KEY_DOWN: "DOWN",
        curses.KEY_LEFT: "LEFT",
        curses.KEY_RIGHT: "RIGHT",
        curses.KEY_HOME: "HOME",
        curses.KEY_END: "END",
        curses.KEY_PPAGE: "PAGEUP",
        curses.KEY_NPAGE: "PAGEDOWN",
        # curses.kUP5: "KBDUP",
        # curses.kDN5: "KBDDOWN",
        # curses.kLFT5: "KBDLEFT",
        # curses.kRIT5: "KBDRIGHT",
        ord("\n"): "ENTER",
        ord("\b"): "BACKSPACE",
        curses.KEY_BACKSPACE: "DELETE",
        curses.KEY_ENTER: "SELECT",
    }

    def _prev_device(self) -> None:

        if not (ndevices := len(self.core.devices)):
            logger.error("There are no devices")
            return

        self._ifocus = ndevices - 1 if not self._ifocus else self._ifocus - 1
        assert self._focus
        logger.info(f"Current device: {self._focus.host!r}")

    def _next_device(self) -> None:

        if not (ndevices := len(self.core.devices)):
            logger.error("There are no devices")
            return

        self._ifocus = (
            0 if self._ifocus is None or self._ifocus == ndevices - 1 else self._ifocus + 1
        )
        assert self._focus
        logger.info(f"Current device: {self._focus.host!r}")

    def _test_menu(self) -> Any:

        menu = Menu(title="Test menu", instructions="Choose test")

        for loc in "0123456":
            menu.add_item(loc, "insert before " + loc)

        menu.add_item("C", "critical message!")
        menu.add_item("Q", "Quit")

        menu.win = self.menu_win.w
        while item := menu.prompt():
            assert isinstance(item.key, int)
            if chr(item.key) in "0123456":
                _loc = item.key - ord("0")
                self.wstack.insert(self.status_window_nlines, self.ncols2, _loc)
            elif chr(item.key) == "C":
                logger.critical(item.text)
            elif chr(item.key) == "Q":
                return False

        return True

    def _set_verbose(self, verbose: int) -> None:
        logger.info("Setting verbose to {}", verbose)
        self.logwin.set_verbose(verbose)

    def redraw(self) -> None:
        """Redraw everything."""

        self.menu_win.redraw()
        self.menu_win.refresh()
        self.wstack.redraw()
        self.wstack.refresh()
