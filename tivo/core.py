"""Docstring."""

from argparse import Namespace
from typing import Any, Callable

from tivo.device import TivoDevice


class TivoCore:
    """Docstring."""

    def __init__(self, options: Namespace, config: dict[str, Any]) -> None:
        """Docstring."""

        self.options = options
        self.config = config
        self.devices: dict[str, TivoDevice] = {}
        self.ui_add_device_callback: Callable[[TivoDevice], None] | None = None
        self.ui_update_status_callback: Callable[[], None] | None = None

    def set_ui_add_device_callback(self, callback: Callable[[TivoDevice], None]) -> None:
        """Docstring."""

        self.ui_add_device_callback = callback

    def set_ui_update_status_callback(self, callback: Callable[[], None]) -> None:
        """Docstring."""

        self.ui_update_status_callback = callback

    def add_device(self, device: TivoDevice) -> None:
        """Docstring."""

        self.devices[device.identity] = device
        if self.ui_add_device_callback:
            self.ui_add_device_callback(device)

    def get_device_by_name(self, name: str) -> TivoDevice | None:
        """Docstring."""

        for device in self.devices.values():
            if name in (device.identity, device.machine, device.address, device.host):
                return device
        # raise NameError(f"Can't find tivo device `{name}`")
        return None
