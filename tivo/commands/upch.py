"""Tivo `upch` command module."""

from tivo.cmd import TivoCmd


class TivoUpchCmd(TivoCmd):
    """Tivo `upch` command class."""

    def init_command(self) -> None:
        """Initialize Tivo `upch` command instance."""

        parser = self.add_subcommand_parser(
            "upch",
            help="tune to next channel on `HOST`",
            description="The `%(prog)s` command tunes `HOST` up to next channel.",
        )

        self.add_host_argument(parser)

    def run(self) -> None:
        """Perform the command."""

        device = self.getdevicebyname(self.cli.options.host)
        device.upch()
        print(f"{self.cli.options.host} is tuned to channel {device.channel}")
