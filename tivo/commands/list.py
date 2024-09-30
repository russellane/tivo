"""Tivo `list` command module."""

from tivo.cmd import TivoCmd


class TivoListCmd(TivoCmd):
    """Tivo `list` command class."""

    def init_command(self) -> None:
        """Initialize Tivo `listch` command instance."""

        self.add_subcommand_parser(
            "list",
            help="list `HOST`s",
            description="The `%(prog)s` command lists known `HOST`s.",
        )

    def run(self) -> None:
        """Perform the command."""

        for device in self.core.devices.values():
            parts = []
            if device.host:
                parts.append(f"host {device.host}")
            if device.identity:
                parts.append(f"identity {device.identity}")
            if device.machine:
                parts.append(f"machine {device.machine}")
            if device.address:
                parts.append(f"address {device.address}")
            print(" ".join(parts))
