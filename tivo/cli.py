"""Tivo command line interface."""

from pathlib import Path
from typing import List, Optional

from libcli import BaseCLI

import tivo.cmd


class TivoCLI(BaseCLI):
    """Tivo command line interface."""

    config = {
        # name of config file.
        "config-file": Path.home().joinpath(".tivo.toml"),
        # toml [section-name].
        "config-name": "tivo",
        # distribution name, not importable package name
        "dist-name": "rlane-tivo",
    }

    def init_parser(self) -> None:
        """Initialize argument parser."""

        self.parser = self.ArgumentParser(
            prog=__package__,
            description=self.dedent(
                """
        `%(prog)s` controls remote TiVo™ devices. When no `COMMAND` is
        given, `%(prog)s` runs an interactive full-screen terminal application,
        that listens for broadcasts from TiVo devices and displays their status.
                """
            ),
        )

    def add_arguments(self) -> None:
        """Add arguments to parser."""
        self.add_subcommand_modules("tivo.commands", prefix="Tivo", suffix="Cmd")

        self.parser.add_argument_group(
            title="Configuration file",
            description=self.dedent(
                """
        TiVo devices broadcast a unique, non-readable `identity` string
        every few minutes. The `--config FILE` maps `identity` to `host`
        names, like `/etc/hosts`.
                """
            ),
        )

    def main(self) -> None:
        """Command line interface entry point (method)."""
        tivo.cmd.main(self)


def main(args: Optional[List[str]] = None) -> None:
    """Command line interface entry point (function)."""
    return TivoCLI(args).main()
