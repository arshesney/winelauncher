import argparse

from textwrap import dedent
from xdg.BaseDirectory import xdg_config_home, xdg_data_home

parser = argparse.ArgumentParser(
    description="winelauncher: a WINE wrapper to handle multiple prefixes",
    epilog=dedent("""
        winelauncher will forward LD_PRELOAD, \
        WINEDEBUG and NINEDEBUG environment variables to WINE
        """))

configfile = parser.add_argument_group("Config options")
configfile.add_argument(
    "-c", "--config",
    help="alternate config file",
    default=xdg_config_home + "/winelauncher.conf",
    dest='config_file',
    metavar="FILE")

# WINE and prefixes locations
general = parser.add_argument_group("WINE options")
general.add_argument("--prefix-base",
                     default=xdg_data_home + "/wineprefixes",
                     help="prefixes base directory")
general.add_argument("--wine-base",
                     default="/opt/wine",
                     help="set WINE base directory")
general.add_argument("--wine-lib32",
                     default="lib32",
                     help="lib directory for 32 bit libraries")
general.add_argument("--wine-lib64",
                     default="lib",
                     help="lib directory for 64 bit libraries")

# Logger options
logger = parser.add_argument_group("Logger options")
logger.add_argument("--log-level",
                    help="set log level",
                    default="info")
logger.add_argument("--log-output",
                    default="console",
                    help="output to log file (or journal)")

# General WINE options
parser.add_argument("--wine-version",
                    default='system',
                    help="WINE version")
parser.add_argument("--prefix",
                    help="WINEPREFIX name (will be appended to prefix_base)",
                    default=None)
parser.add_argument("--wine-arch",
                    help="set WINEARCH (32 or 64 bit)",
                    choices=["32", "64"])
parser.add_argument("--list",
                    help="list WINE versions available",
                    action="store_true")
parser.add_argument("winecommand", nargs='*',
                    help="command to forward to WINE")
