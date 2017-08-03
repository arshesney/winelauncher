import argparse
import configparser
import os
import pathlib
import subprocess
import sys

from textwrap import dedent
from threading import Thread
from ast import literal_eval
from xdg.BaseDirectory import xdg_config_home
from winelauncher.functions import *
from winelauncher.winelog import *

log = None
wine_env = wine_exec = config_env = {}

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
                        default="")
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
    description="winelauncher: command line WINE wrapper",
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
                     help="WINE installation base directory")
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
                    help="log messages detination")

# General WINE options
parser.add_argument("--wine-version",
                    default=None,
                    help="WINE version to use")
parser.add_argument("--wine-arch",
                    help="WINEARCH to use",
                    choices=["32", "64"],
                    default=lookup(config, config_section, 'wine_arch'))
parser.add_argument("--list",
                    help="list WINE versions available",
                    action="store_true")
parser.add_argument("winecommand", nargs='*',
                    help="command to execute with WINE")
parser.parse_args(remaining_argv, namespace=args)


def main():
    syslog_tag = args.prefix if args.prefix else 'wine'
    log = logger_init(syslog_tag, args.log_output, args.log_level)
    log.debug("Logger initialized.")
    log.info("Args: {}".format(args))
    # Load config from file or generate a default one

    if not args.winecommand or args.list:
        list_wine_versions(args.wine_base)
        sys.exit(0)

    # Set the executables to use and populate the environment
    # check if LD_LIBRARY_PATH is set
    cur_ld_path = os.environ.get('LD_LIBRARY_PATH', None)
    # Add the : delimiter before the eventual existing variable to avoid
    # including the current path in LD_LIBRARY_PATH
    cur_ld_path = ':' + cur_ld_path if cur_ld_path else ""
    wine_env = os.environ
    if lookup(config, args.prefix, "wine_version") and not args.wine_version:
        wine_base = args.wine_base + '/' + lookup(config, args.prefix, "wine_version")
        try:
            subprocess.check_output([wine_base + "/bin/wine", "--version"])
        except subprocess.CalledProcessError:
            print("Unable to find WINE in {}".format(wine_base))
            sys.exit(1)
        wine_env['PATH'] = wine_base + '/bin:' + os.environ.get('PATH')
    elif args.wine_version == "system" or not args.wine_version:
        wine_base = '/usr'
    else:
        wine_base = args.wine_base + '/' + args.wine_version
        try:
            subprocess.check_output([wine_base + "/bin/wine", "--version"])
        except subprocess.CalledProcessError:
            print("Unable to find WINE in {}".format(wine_base))
            sys.exit(1)
        wine_env['PATH'] = wine_base + '/bin:' + os.environ.get('PATH')

    wine_env['WINEPREFIX'] = config.get('common', 'prefix_base') + "/" + args.prefix
    wine_env['WINEVERPATH'] = wine_base
    wine_env['WINELOADER'] = wine_base + '/bin/wine'
    wine_env['WINESERVER'] = wine_base + '/bin/wineserver'

    if args.wine_arch == "32":
        wine_env['WINEARCH'] = 'win32'
        wine_env['WINEDLLPATH'] = wine_base + '/' + args.wine_lib32 + '/wine'
        wine_env['LD_LIBRARY_PATH'] = wine_base + '/' + args.wine_lib32 + cur_ld_path
    else:
        #wine_env['WINEARCH'] = 'win64'
        wine_env['WINEDLLPATH'] = wine_base + '/' + args.wine_lib64 + '/wine'
        wine_env['LD_LIBRARY_PATH'] = wine_base + '/' + args.wine_lib32 + ':' + wine_base + '/' + args.wine_lib64 + cur_ld_path

    config_env = literal_eval(lookup(config, config_section, 'environment'))
    if config_env:
        for env_var, value in config_env.items():
            wine_env[env_var] = os.environ.get(env_var, value)

    log.info('Enviroment: {}'.format(wine_env))
    wine_exec = args.winecommand
    if wine_exec[0] == 'winetricks':
        log.info('Running winetricks')
    else:
        wine_exec.insert(0, wine_base + '/bin/wine')
        log.info('WINE command: {}'.format(wine_exec))

    # Spawn WINE process
    wine_p = subprocess.Popen(
        wine_exec,
        bufsize=1,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=wine_env)

    consume = lambda line: log.info(line.decode('utf-8', 'replace'))
    Thread(target=consume_output, args=[wine_p.stdout, consume]).start()
    Thread(target=consume_output, args=[wine_p.stderr, consume]).start()
    wine_p.wait()

    sys.exit(0)


if __name__ == "__main__":
    main()
