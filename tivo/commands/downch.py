"""Tivo `downch` command module."""

from tivo.cmd import TivoCmd


class TivoDownchCmd(TivoCmd):
    """Tivo `downch` command class."""

    def init_command(self) -> None:
        """Initialize Tivo `downch` command instance."""

        parser = self.add_subcommand_parser(
            "downch",
            help="tune to previous channel on `HOST`",
            description="The `%(prog)s` command tunes `HOST` down to previous channel.",
        )

        self.add_host_argument(parser)

    def run(self) -> None:
        """Perform the command."""

        device = self.getdevicebyname(self.cli.options.host)
        device.downch()
        print(f"{self.cli.options.host} is tuned to channel {device.channel}")
