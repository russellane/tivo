"""Tivo base command."""

import argparse

from libcli import BaseCmd

from tivo.core import TivoCore
from tivo.device import TivoDevice


class TivoCmd(BaseCmd):
    """Tivo base command class."""

    core: TivoCore

    def add_host_argument(self, parser: argparse.ArgumentParser) -> None:
        """Add `HOST` argument to given `parser`."""

        host = parser.add_argument("host", metavar="HOST", help="target tivo device")
        host.completer = self._known_hosts_completer  # type: ignore[attr-defined]

    @staticmethod
    def _known_hosts_completer(**_kwargs: str) -> list[str]:
        """Read `/etc/hosts` and return list of known hosts."""

        hosts = []
        with open("/etc/hosts", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if len(line) < 1 or line[0] == "#":
                    continue
                value = line.split()
                if "::" in value[0]:
                    continue

                for name in value[1:]:
                    if len(name) > 0 and name[0] == "#":
                        break
                    hosts.append(name)

        return sorted(hosts)

    def getdevicebyname(self, name: str) -> TivoDevice:
        """Return the device with the matching `name`."""

        device = self.core.get_device_by_name(name)
        assert device
        return device
