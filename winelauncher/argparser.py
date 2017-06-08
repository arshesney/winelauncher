import argparse
import os

from textwrap import dedent

config_parser = argparse.ArgumentParser(
    description="%(prog)s: a WINE wrapper to handle multiple prefixes",
    epilog=dedent("""
        %(prog)s will forward LD_PRELOAD, \
        WINEDEBUG and NINEDEBUG environment variables to WINE
        """))

config_parser.add_argument(
    "-c", "--config",
    help="alternate config file",
    default=xdg_config_home + "/winelauncher.conf",
    dest='config_file',
    metavar="FILE")
args, remaining_argv = config_parser.parse_known_args()

if pathlib.Path(args.config_file) and config.read(args.config_file):
    print("Using configuration from {}".format(args.config_file))
else:
    try:
        with open(args.config_file, mode="w") as newfile:
            config.write(newfile)
        print("Saved default config file {}".format(args.config_file))
        sys.exit(0)
    except OSError as err:
        print("Cannot open file {}".format(args.config_file))
        print("OSError: {0}".format(err))

parser = argparse.ArgumentParser(
    parents=[config_parser],
    description=__doc__)

general = parser.add_argument_group("WINE options")
general.set_defaults(**config['general'])
