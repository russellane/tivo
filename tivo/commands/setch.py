"""Tivo `setch` command module."""

from tivo.cmd import TivoCmd


class TivoSetchCmd(TivoCmd):
    """Tivo `setch` command class."""

    def init_command(self) -> None:
        """Initialize Tivo `setch` command instance."""

        parser = self.add_subcommand_parser(
            "setch",
            help="tune `HOST` to `CHANNEL`",
            description="The `%(prog)s` command tunes `HOST` to `CHANNEL`.",
        )

        self.add_host_argument(parser)

        parser.add_argument("channel", metavar="CHANNEL", help="change to `CHANNEL` on `HOST`")

    def run(self) -> None:
        """Perform the command."""

        device = self.getdevicebyname(self.cli.options.host)
        device.send_setch(self.cli.options.channel)
        print(f"{self.cli.options.host} is tuned to channel {device.channel}")
