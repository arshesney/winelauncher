winelauncher
============

Wrapper for WINE to manage multiple versions and multiple prefixes, written in Python.

Winelauncher sets the desired environment for a specific WINE version and bottle, much like GUI applications like PlayOnLinux and q4wine.

##### Command options
```shell
usage: winelauncher [-h] [-c FILE] [--prefix PREFIX]
                    [--prefix-base PREFIX_BASE] [--wine-base WINE_BASE]
                    [--wine-lib32 WINE_LIB32] [--wine-lib64 WINE_LIB64]
                    [--log-level LOG_LEVEL] [--log-output LOG_OUTPUT]
                    [--wine-version WINE_VERSION] [--wine-arch {32,64}]
                    [--list]
                    [winecommand [winecommand ...]]

winelauncher: command line WINE wrapper

positional arguments:
  winecommand           command to execute with WINE

optional arguments:
  -h, --help            show this help message and exit
  -c FILE, --config FILE
                        alternate config file
  --prefix PREFIX       WINEPREFIX name
  --wine-version WINE_VERSION
                        WINE version to use
  --wine-arch {32,64}   WINEARCH to use
  --list                list WINE versions available

WINE options:
  --prefix-base PREFIX_BASE
                        prefixes base directory
  --wine-base WINE_BASE
                        WINE installation base directory
  --wine-lib32 WINE_LIB32
                        lib directory for 32 bit libraries
  --wine-lib64 WINE_LIB64
                        lib directory for 64 bit libraries

Logger options:
  --log-level LOG_LEVEL
                        set log level
  --log-output LOG_OUTPUT
                        log messages detination

winelauncher will forward LD_PRELOAD, WINEDEBUG and NINEDEBUG environment
variables to WINE
```

Winelauncher configuration file defaults to *xdg_config_home*/winelauncher.conf

The program expects bottles under a common directory, defined by --prefix-base (~/wine by default),
likewise, additional WINE versions directory can be specified with --wine-base (/opt/wine by default).

The WINE version passed to the argument is the directory name that can be found under --wine-base,
usually contining the usr, lib, shared directories.
```
/opt/wine
└── 2.12-staging-nine
    ├── etc
    │   └── fonts
    │       ├── conf.avail
    │       └── conf.d
    └── usr
        ├── bin
        ├── include
        │   └── wine
        │       ├── msvcrt
        │       │   └── sys
        │       └── windows
        │           └── ddk
        ├── lib
        │   └── wine
        │       └── fakedlls
        ├── lib32
        │   └── wine
        │       └── fakedlls
        └── share
            ├── applications
            ├── man
            │   ├── de.UTF-8
            │   │   └── man1
            │   ├── fr.UTF-8
            │   │   └── man1
            │   ├── man1
            │   └── pl.UTF-8
            │       └── man1
            └── wine
                └── fonts
```
For the example above the --wine-version should be 2.12-staging-nine.
If --wine-version is omitted, or is set to system, the system-wide WINE is used.

##### Configuration file
On the first run the program will write a default configuration file:
```
[common]
prefix_base = /home/user/wine
wine_dir = /opt/wine
wine_lib32 = lib32
wine_lib64 = lib

[prefix_default]
log_dest = console
log_level = info
environment = {'WINEDEBUG': 'fixme-all', 'NINEDEBUG': 'fixme-all', 'mesa_glthread': 'true', 'PULSE_LATENCY_MSEC': '60', 'FREETYPE_PROPERTIES': 'truetype:interpreter-version=35'}
```
Command line switches can be specified on a per-prefix basis such as:
```
[mybottle]
log_dest = journal
log_level = error
environment = {'WINEDEBUG': '-all', 'NINEDEBUG': '-all'}
```
Any option not specified for the bottle will fallback to the prefix_default value.
Command line arguments always override the configuration file.

##### Examples
```
$ winelauncher --prefix mybottle c:\\windows\\system32\\notepad.exe

$ winelauncher --prefix otherbottle winetricks vcrun2010

$ winelauncher --prefix steam c:\\Steam\\Steam.exe -- -no-cef-sandbox
```
