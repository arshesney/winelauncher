import argparse
import configparser
import pathlib
import sys

from textwrap import dedent
from xdg.BaseDirectory import xdg_config_home, xdg_data_home


def init_config(config_file):
    """ Check if config file exists, otherwise generate a default one """
    if pathlib.Path(config_file) and config.read(config_file):
        print("Using configuration from {}".format(config_file))
    else:
        try:
            with open(config_file, mode="w") as newfile:
                config.write(newfile)
            print("Saved default config file {}".format(config_file))
            sys.exit(0)
        except OSError as err:
            print("Cannot open file {}".format(config_file))
            print("OSError: {0}".format(err))


config = configparser.ConfigParser(default_section="general")

# Default config
config['general'] = {
    "prefix_base": xdg_data_home + "/wineprefixes",
    "wine_dir": "/opt/wine",
    "wine_lib32": "lib32",
    "wine_lib64": "lib",
    "wine_debug": "fixme-all",
    "nine_debug": "fixme-all"
}
config['logging'] = {
    "log_dest": "console",
    "log_level": "info"
}

configfile = argparse.ArgumentParser(
    description=__doc__,
    add_help=False)
configfile.add_argument(
    "-c", "--config",
    help="alternate config file",
    default=xdg_config_home + "/winelauncher.conf",
    dest='config_file',
    metavar="FILE")
args, remaining_argv = configfile.parse_known_args()

if config.read(args.config_file):
    print("Using config from: {}".format(args.config_file))
else:
    print("No config file found, \
        generating a default one at: {}".format(args.config_file))
    init_config(args.config_file)

parser = argparse.ArgumentParser(
    description="winelauncher: a WINE wrapper to handle multiple prefixes",
    parents=[configfile],
    epilog=dedent("""
        winelauncher will forward LD_PRELOAD, \
        WINEDEBUG and NINEDEBUG environment variables to WINE
        """))

# WINE and prefixes locations
general = parser.add_argument_group("WINE options")
general.add_argument("--prefix-base",
                     default=config.get('general', 'prefix_base'),
                     help="prefixes base directory")
general.add_argument("--wine-base",
                     default=config.get('general', 'wine_dir'),
                     help="set WINE base directory")
general.add_argument("--wine-lib32",
                     default=config.get('general', 'wine_lib32'),
                     help="lib directory for 32 bit libraries")
general.add_argument("--wine-lib64",
                     default=config.get('general', 'wine_lib64'),
                     help="lib directory for 64 bit libraries")

# Logger options
logger = parser.add_argument_group("Logger options")
logger.add_argument("--log-level",
                    help="set log level",
                    default=config.get('logging', 'log_level'))
logger.add_argument("--log-output",
                    default=config.get('logging', 'log_dest'),
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
args = parser.parse_args(remaining_argv)
