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
    emulator            Run a TiVo set-top device emulator.
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

## tivo emulator
```
usage: tivo emulator [-h] [-n NUM_DEVICES] [-s STAGGER] [-i INTERVAL] [-r]

Tivo Device Emulator.

This program emulates a TiVo set-top device, which:
    1. Sends a UDP broadcast message every minute or so,
    2. Listens for TCP connections, and responds to requests.

This is for testing basic features of the client application
without an actual device.

options:
  -h, --help            Show this help message and exit.
  -n NUM_DEVICES, --num_devices NUM_DEVICES
                        Number of TiVo devices to emulate (default: `1`).
  -s STAGGER, --stagger STAGGER
                        Delay the start of each device's TCP-listener in
                        seconds. Meaningful when NUM_DEVICES is greater than 1
                        (default: `0`).
  -i INTERVAL, --interval INTERVAL
                        Interval between broadcasts in seconds (default:
                        `60`).
  -r, --randomize       Randomize the interval, by 50-150%, between each
                        device's broadcast (default: `False`).
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

