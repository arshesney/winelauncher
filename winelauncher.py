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
    description='%(prog)s: a WINE wrapper to handle multiple prefixes')
parser.add_argument('-c', '--config',
                    help='alternate config file')
parser.add_argument('-p', '--prefix',
                    help='WINEPREFIX name (will be appended to prefix_base)')
parser.add_argument('-b', '--base',
                    help='prefixes abse directory')
parser.add_argument('-a', '--arch',
                    help='set WINEARCH (32 or 64 bit)')
parser.add_argument('-w', '--wine',
                    help='WINE version')
parser.add_argument('-d', '--winedir',
                    help='set WINE base directory')
parser.add_argument('-l', '--list',
                    help='list WINE versions available',
                    action='store_true')
parser.add_argument('-s', '--save',
                    help='save configuration',
                    action='store_true')
parser.epilog('%(prog)s will forward LD_PRELOAD, WINEDEBUG and NINEDEBUG environment variables to WINE')

# Parse command line arguments: config_file first, other values will
# override conf settings after reading config_file
args = parser.parse_args()
config_file = args.config if args.config else config_file

# Read config file or generate a default one if file doesn't exists
config_p = pathlib.Path(config_file)
config = configparser.ConfigParser()
config['general'] = {
    'prefix_base': '%(my_dir)s/.local/wineprefixes',
    'wine_dir': '/opt/wine'
}
config['logging'] = {
    'log': 'syslog',
    'log_level': 'info',
    'wine_debug': '-all',
    'nine_debug': '-all'
}
config.read(config_file)

# Other comman line arguments
prefix = args.prefix if args.prefix else None
prefix_base = args.base if args.base else config.get('general', 'prefix_base')
wine_arch = args.arch if args.arch else None
wine_version = args.wine if args.wine else None
wine_dir = args.winedir if args.winedir else config.get('general', 'wine_dir')

if prefix:
    config[prefix] = {
    }

if args.save:
    try:
        with open(config_file, mode='w') as newfile:
            config.write(newfile)
        print('Saved config file {}'.format(config_file))
        sys.exit(0)
    except OSError as err:
        print('Cannot open file {}'.format(config_file))
        print('OSError: {0}'.format(err))


#
# List WINE versions installed
#
system_wine = pathlib.Path('/usr/bin/wine')
if system_wine.is_file():
    system_wine_version = str(subprocess.check_output(
        ['/usr/bin/wine', '--version']), 'utf-8')
else:
    system_wine = None

if pathlib.Path(wine_dir).exists():
    wine_versions_list = os.listdir(wine_dir)
else:
    wine_versions_list = None

if system_wine or wine_versions_list:
    if system_wine:
        print('System WINE version:\n\t{}'.format(system_wine_version))
    else:
        print('No system-wine WINE found\n')

    if wine_versions_list:
        print('WINE versions available in {}:\n\n'.format(wine_dir))
        for winedir in wine_versions_list:
            print('\t{}'.format(winedir))
    else:
        print('No additional WINE installs available')
    sys.exit(0)
else:
    print('No WINE found')
    sys.exit(1)


#
# Logging configuration
#
def log_level(level):
    set_level = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARN,
        'warn': logging.WARN,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
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
        print('Cannot open file {}'.format(log_dest))
        print('OSError: {0}'.format(err))

logger.debug('Logger initialized.')


#
# Read current environment and preapre WINE specific one
#
current_env_path = os.environ.get('PATH', default=None)
current_env_ldpreload = os.environ.get('LD_PRELOAD', default=None)
current_env_winedebug = os.environ.get('WINEDEBUG', default='-all')
current_env_ninedebug = os.environ.get('NINEDEBUG', default='-all')

wine_prefix = config.read('general', 'prefix_base') + '/' + prefix if prefix else None
launcher_env = {}

