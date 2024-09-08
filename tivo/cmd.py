"""Tivo base command."""

import argparse
from typing import List

from libcli import BaseCLI, BaseCmd

from tivo.device import TivoDevice
from tivo.remote import TivoRemote


class TivoCmd(BaseCmd):
    """Tivo base command class."""

    remote: TivoRemote

    def add_host_argument(self, parser: argparse.ArgumentParser) -> None:
        """Add `HOST` argument to given `parser`."""

        host = parser.add_argument("host", metavar="HOST", help="target tivo device")
        host.completer = self._known_hosts_completer

    @staticmethod
    def _known_hosts_completer(**kwargs) -> List[str]:
        """Read `/etc/hosts` and return list of known hosts."""

        _ = kwargs  # unused

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

        return self.remote.getdevicebyname(name)


def main(cli: BaseCLI) -> None:
    """Command entry point (function)."""

    TivoCmd.remote = TivoRemote(cli.options, cli.config)

    if hasattr(cli.options, "cmd") and cli.options.cmd:
        cli.options.cmd()
    else:
        TivoCmd.remote.control()  # interactive
