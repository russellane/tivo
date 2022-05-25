# tivo
```
usage: tivo [-h] [-H] [-v] [-V] [--config FILE] [--print-config] [--print-url]
            COMMAND ...

`tivo` controls remote TiVo™ devices. When no `COMMAND` is
given, `tivo` runs an interactive full-screen terminal application,
that listens for broadcasts from TiVo devices and displays their status.

Specify one of:
  COMMAND
    downch         Tune to previous channel on `HOST`.
    getch          Get and print channel from `HOST`.
    list           List `HOST`s.
    setch          Tune `HOST` to `CHANNEL`.
    upch           Tune to next channel on `HOST`.

Configuration file:
  TiVo devices broadcast a unique, non-readable `identity` string
  every few minutes. The `--config FILE` maps `identity` to `host`
  names, like `/etc/hosts`.

General options:
  -h, --help       Show this help message and exit.
  -H, --long-help  Show help for all commands and exit.
  -v, --verbose    `-v` for detailed output and `-vv` for more detailed.
  -V, --version    Print version number and exit.
  --config FILE    Use config `FILE` (default: `~/.tivo.toml`).
  --print-config   Print effective config and exit.
  --print-url      Print project url and exit.
```

## tivo downch
```
usage: tivo downch [-h] HOST

The `tivo downch` command tunes `HOST` down to previous channel.

positional arguments:
  HOST        Target tivo device.

options:
  -h, --help  Show this help message and exit.
```

## tivo getch
```
usage: tivo getch [-h] HOST

The `tivo getch` command gets and prints channel from `HOST`.

positional arguments:
  HOST        Target tivo device.

options:
  -h, --help  Show this help message and exit.
```

## tivo list
```
usage: tivo list [-h]

The `tivo list` command lists known `HOST`s.

options:
  -h, --help  Show this help message and exit.
```

## tivo setch
```
usage: tivo setch [-h] HOST CHANNEL

The `tivo setch` command tunes `HOST` to `CHANNEL`.

positional arguments:
  HOST        Target tivo device.
  CHANNEL     Change to `CHANNEL` on `HOST`.

options:
  -h, --help  Show this help message and exit.
```

## tivo upch
```
usage: tivo upch [-h] HOST

The `tivo upch` command tunes `HOST` up to next channel.

positional arguments:
  HOST        Target tivo device.

options:
  -h, --help  Show this help message and exit.
```

