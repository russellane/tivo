"""Tivo `getch` command module."""

from tivo.cmd import TivoCmd


class TivoGetchCmd(TivoCmd):
    """Tivo `getch` command class."""

    def init_command(self) -> None:
        """Initialize Tivo `getch` command instance."""

        parser = self.add_subcommand_parser(
            "getch",
            help="get and print channel from `HOST`",
            description="The `%(prog)s` command gets and prints channel from `HOST`.",
        )

        self.add_host_argument(parser)

    def run(self) -> None:
        """Perform the command."""

        device = self.getdevicebyname(self.cli.options.host)
        device.getch()
        print(f"{self.cli.options.host} is tuned to channel {device.channel}")
