winelauncher
============

Wrapper for WINE to manage multiple versions and multiple prefixes, written in Python.

Winelauncher sets the desired environment for a specific WINE version and bottle, much like GUI applications like PlayOnLinux and q4wine.

##### Command options
```shell
usage: main.py [-h] [-c FILE] [--prefix PREFIX] [--prefix-base PREFIX_BASE]
               [--wine-base WINE_BASE] [--wine-lib32 WINE_LIB32]
               [--wine-lib64 WINE_LIB64] [--log-level LOG_LEVEL]
               [--log-output LOG_OUTPUT] [--wine-version WINE_VERSION]
               [--wine-arch {32,64}] [--list]
               [winecommand [winecommand ...]]

winelauncher: a WINE wrapper to handle multiple prefixes

positional arguments:
  winecommand           command to forward to WINE

optional arguments:
  -h, --help            show this help message and exit
  -c FILE, --config FILE
                        alternate config file
  --prefix PREFIX       WINEPREFIX name
  --wine-version WINE_VERSION
                        WINE version
  --wine-arch {32,64}   set WINEARCH (32 or 64 bit)
  --list                list WINE versions available

WINE options:
  --prefix-base PREFIX_BASE
                        prefixes base directory
  --wine-base WINE_BASE
                        set WINE base directory
  --wine-lib32 WINE_LIB32
                        lib directory for 32 bit libraries
  --wine-lib64 WINE_LIB64
                        lib directory for 64 bit libraries

Logger options:
  --log-level LOG_LEVEL
                        set log level
  --log-output LOG_OUTPUT
                        output to log file (or journal)

winelauncher will forward LD_PRELOAD, WINEDEBUG and NINEDEBUG environment
variables to WINE
```

Winelauncher configuration file defaults to 
