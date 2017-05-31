#!/usr/bin/env python
import logging
import logging.handlers
import argparse
import configparser
import pathlib
import sys
import os
import subprocess
from xdg.BaseDirectory import xdg_config_home
from systemd.journal import JournalHandler


#
# DEFAULTS
#
config_file = xdg_config_home + '/winelauncher.conf'


#
# Command line arguments
#
parser = argparse.ArgumentParser(
        description="winelauncher command line arguments")
parser.add_argument("-c", "--config", help="Alternate config file")
parser.add_argument("-p", "--prefix", help="WINEPREFIX")
parser.add_argument("-a", "--arch", help="WINEARCH (32 or 64 bit)")
parser.add_argument("-w", "--wine", help="WINE version")
parser.add_argument("-d", "--wine-dir", help="WINE directory")
parser.add_argument("-l", "--list", help="List WINE versions available")

args = parser.parse_args()

if args.config:
    config_file = args.config

if args.prefix:
    prefix = args.prefix
else:
    prefix = None

if args.wine:
    wine_version = args.wine

# Read config file or generate a default one if file doesn't exists
config_p = pathlib.Path(config_file)
if config_p.exists() and config_p.is_file():
    config = configparser.BasicInterpolation()
    config.read(config_file)
else:
    try:
        with config_p.open(mode='w') as newfile:
            newfile.write("""\
[general]
prefix_path = %(my_dir)s/.local/wineprefixes
wine_dir = /opt/wine

[logging]
log = syslog
log_level = info
wine_debug = -all
nine_debug = -all
                    """)
            print("Generated a new config file at {}".format(config_file))
            sys.exit(0)
    except OSError as err:
        print("Cannot open file {}".format(config_file))
        print("OSError: {0}".format(err))

if args.wine-dir:
    wine_dir = args.wine-dir
else:
    wine_dir = config.get('general', 'wine_dir')


#
# List WINE versions installed
#
if pathlib.Path(wine_dir):
    wine_versions_list = os.listdir(wine_dir)
    system_wine = pathlib.Path('/usr/bin/wine')
    if system_wine.is_file():
        system_wine_version = str(subprocess.check_output(
            ['/usr/bin/wine', '--version']), 'utf-8')
    else:
        system_wine = None
else:
    wine_versions_list = None

if system_wine or wine_versions_list:
    if system_wine:
        print("System WINE version: {}".format(system_wine_version))
    else:
        print("No system-wine WINE found")

    if wine_versions_list:
        print("WINE versions available in {}:".format(wine_dir))
        for winedir in wine_versions_list:
            print("{}".format(winedir))
    else:
        print("No additional WINE installs available")
    sys.exit(0)
else:
    print("No WINE found")
    sys.exit(1)


#
# Logging configuration
#
def log_level(level):
    set_level = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARN,
            "warn": logging.WARN,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
            }
    return set_level.get(level, logging.INFO)


logger = logging.getLogger(__name__)
logger.setLevel(log_level)

if config.has_option('logging', 'log'):
    log_dest = config.get('logging', 'log')
else:
    log_dest = 'syslog'

if log_dest == 'syslog':
    logger.addHandler(JournalHandler(SYSLOG_IDENTIFIER=prefix))
else:
    try:
        log_handler = logging.handlers.FileHandler(log_dest)
        log_handler.setFormatter('%(asctime)s %(levelname)-8s %(message)s')
        logger.addHandler(log_handler)
    except OSError as err:
        print("Cannot open file {}".format(log_dest))
        print("OSError: {0}".format(err))

logger.debug("Logger initialized.")
