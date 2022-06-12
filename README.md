# tivo
```
usage: tivo [-h] [-H] [-v] [-V] [--config FILE] [--print-config] [--print-url]
            [--completion [SHELL]]
            COMMAND ...

`tivo` controls remote TiVo™ devices. When no `COMMAND` is given,
tivo listens for broadcasts from remote devices, and presents an
interactive terminal application to display their status, change
channels, navigate menus, enter text into search box, etc. with the
full computer keyboard.

Channels may also be changed from the command line.

Specify one of:
  COMMAND
    downch              Tune to previous channel on `HOST`.
    getch               Get and print channel from `HOST`.
    list                List `HOST`s.
    setch               Tune `HOST` to `CHANNEL`.
    upch                Tune to next channel on `HOST`.

Configuration file:
  TiVo devices broadcast a unique, non-readable `identity` string
  every few minutes. The `--config FILE` maps `identity` to `host`
  names, like `/etc/hosts`.

General options:
  -h, --help            Show this help message and exit.
  -H, --long-help       Show help for all commands and exit.
  -v, --verbose         `-v` for detailed output and `-vv` for more detailed.
  -V, --version         Print version number and exit.
  --config FILE         Use config `FILE` (default: `~/.tivo.toml`).
  --print-config        Print effective config and exit.
  --print-url           Print project url and exit.
  --completion [SHELL]  Print completion scripts for `SHELL` and exit
                        (default: `bash`).
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

