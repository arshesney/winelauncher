import argparse
import configparser
import pathlib
import sys

from textwrap import dedent
from xdg.BaseDirectory import xdg_config_home, xdg_data_home


class Args:
    pass


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


def lookup(config, prefix, option):
    if config.has_option(prefix, option):
        return config.get(prefix, option)
    else:
        return config.get('prefix_default', option)


config = configparser.ConfigParser(default_section='common')

# Default config
config['common'] = {
    "prefix_base": xdg_data_home + "/wineprefixes",
    "wine_dir": "/opt/wine",
    "wine_lib32": "lib32",
    "wine_lib64": "lib",
}
config['prefix_default'] = {
    "log_dest": "console",
    "log_level": "info"
    "environment": {
        "WINEDEBUG": "fixme-all",
        "NINEDEBUG": "fixme-all",
        "mesa_glthread": "true",
        "PULSE_LATENCY_MSEC": "60",
        }
}

args = Args()
configfile = argparse.ArgumentParser(
    description=__doc__,
    add_help=False)
configfile.add_argument(
    "-c", "--config",
    help="alternate config file",
    default=xdg_config_home + "/winelauncher.conf",
    dest='config_file',
    metavar="FILE")
configfile.add_argument("--prefix",
                        help="WINEPREFIX name",
                        default=None)
args, remaining_argv = configfile.parse_known_args(namespace=args)

if config.read(args.config_file):
    print("Using config from: {}".format(args.config_file))
else:
    print("No config file found, generating a default one at: {}".format(args.config_file))
    init_config(args.config_file)

if config.has_section(args.prefix):
    config_section = args.prefix
else:
    config_section = 'prefix_default'

parser = argparse.ArgumentParser(
    description="winelauncher: a WINE wrapper to handle multiple prefixes",
    parents=[configfile],
    epilog=dedent("""
        winelauncher will forward LD_PRELOAD, WINEDEBUG and NINEDEBUG environment variables to WINE
        """))

# WINE and prefixes locations
general = parser.add_argument_group("WINE options")
general.add_argument("--prefix-base",
                     default=config.get('common', 'prefix_base'),
                     help="prefixes base directory")
general.add_argument("--wine-base",
                     default=config.get('common', 'wine_dir'),
                     help="set WINE base directory")
general.add_argument("--wine-lib32",
                     default=config.get('common', 'wine_lib32'),
                     help="lib directory for 32 bit libraries")
general.add_argument("--wine-lib64",
                     default=config.get('common', 'wine_lib64'),
                     help="lib directory for 64 bit libraries")

# Logger options
logger = parser.add_argument_group("Logger options")
logger.add_argument("--log-level",
                    default=lookup(config, config_section, 'log_level'),
                    help="set log level")
logger.add_argument("--log-output",
                    default=lookup(config, config_section, 'log_dest'),
                    help="output to log file (or journal)")

# General WINE options
parser.add_argument("--wine-version",
                    default='system',
                    help="WINE version")
parser.add_argument("--wine-arch",
                    help="set WINEARCH (32 or 64 bit)",
                    choices=["32", "64"])
parser.add_argument("--list",
                    help="list WINE versions available",
                    action="store_true")
parser.add_argument("winecommand", nargs='*',
                    help="command to forward to WINE")
parser.parse_args(remaining_argv, namespace=args)
