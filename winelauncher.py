#!/usr/bin/env python
import logging
import logging.handlers
import argparse
import configparser
from xdg.BaseDirectory import xdg_config_home


# DEFAULTS
CONFIG = xdg_config_home + '/winelauncher.conf'


# define log levels
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


parser = argparse.ArgumentParser(description="WINE launcher command arguments")
parser.add_argument("-c", "--config", help="Alternate config file")
parser.add_argument("-p", "--prefix", help="WINEPREFIX")
parser.add_argument("-a", "--arch", help="WINEARCH 32 or 64 bit")

args = parser.parse_args()

if args.config:
    CONFIG = args.config

config = configparser.RawConfigParser()
config.read(CONFIG)
