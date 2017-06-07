#!/usr/bin/env python3
import logging
import logging.handlers
import argparse
import configparser
import pathlib
import sys
import os
import subprocess
from xdg.BaseDirectory import xdg_config_home, xdg_data_home
from systemd.journal import JournalHandler


#
# DEFAULTS
#
config = configparser.ConfigParser(default_section="general")
home_dir = os.path.expanduser("~")
config['general'] = {
    "prefix_base": xdg_data_home + "/wineprefixes",
    "wine_dir": "/opt/wine",
    "wine_lib32": "lib32",
    "wine_lib64": "lib",
    "wine_debug": "-all",
    "nine_debug": "-all"
}
config['logging'] = {
    "log_dest": "syslog",
    "log_level": "info"
}


#
# Command line arguments
#
# Handle an explicit config file
config_parser = argparse.ArgumentParser(
    description="%(prog)s: a WINE wrapper to handle multiple prefixes",
    epilog="%(prog)s will forward LD_PRELOAD, \
            WINEDEBUG and NINEDEBUG environment variables to WINE",
    add_help=False)
config_parser.add_argument("-c", "--config",
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

# General section arguments override
general_parser = argparse.ArgumentParser(parents=[config_parser],
                                         description=__doc__,
                                         add_help=False)
general_parser.set_defaults(**config['general'])
general_parser.add_argument("-b", "--base",
                            help="prefixes base directory")
general_parser.add_argument("-d", "--wine-dir",
                            help="set WINE base directory")
args, remaining_argv = general_parser.parse_known_args(remaining_argv)

logging_parser = argparse.ArgumentParser(parents=[general_parser],
                                         description=__doc__,
                                         add_help=False)
logging_parser.set_defaults(**config['logging'])
logging_parser.add_argument("-L", "--log-level",
                            help="ste log level",
                            default="info")
logging_parser.add_argument("-o", "--log-output",
                            help="output to log file (or syslog)")
args, remaining_argv = logging_parser.parse_known_args(remaining_argv)

parser = argparse.ArgumentParser(parents=[logging_parser],
                                 description=__doc__)
parser.add_argument("-w", "--wine-version",
                    default='system',
                    help="WINE version")
parser.add_argument("-p", "--prefix",
                    help="WINEPREFIX name (will be appended to prefix_base)",
                    default=None)
parser.add_argument("-a", "--wine-arch",
                    help="set WINEARCH (32 or 64 bit)",
                    choices=["32", "64"])
parser.add_argument("-l", "--list",
                    help="list WINE versions available",
                    action="store_true")
parser.add_argument("winecommand", nargs='*',
                    help="command to forward to WINE")

# Parse command line arguments: will override config_file values
args = parser.parse_args(remaining_argv)
print("Args: {}".format(args))


#
# List WINE versions installed
#
if args.list or not args.winecommand:
    system_wine = pathlib.Path("/usr/bin/wine")
    if system_wine.is_file():
        system_wine_version = str(subprocess.check_output(
            ["/usr/bin/wine", "--version"]), "utf-8")
    else:
        system_wine = None

    if pathlib.Path(args.wine_dir).exists():
        wine_versions_list = os.listdir(args.wine_dir)
    else:
        wine_versions_list = None

    if system_wine or wine_versions_list:
        if system_wine:
            print("System WINE version:\n\t{}".format(system_wine_version))
        else:
            print("No system-wine WINE found\n")

        if wine_versions_list:
            print("WINE versions available in {}:\n\n".format(args.wine_dir))
            for winedir in wine_versions_list:
                print("\t{}".format(winedir))
        else:
            print("No additional WINE installs available")
    else:
        print("No WINE found")
        sys.exit(1)


#
# Logging configuration
#
def set_log_level(level):
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
logger.setLevel(set_log_level(args.log_level))

if args.log_dest == "syslog":
    syslog_tag = args.prefix if args.prefix else 'wine'
    logger.addHandler(JournalHandler(SYSLOG_IDENTIFIER=syslog_tag))
else:
    try:
        log_handler = logging.handlers.FileHandler(args.log_dest)
        log_handler.setFormatter("%(asctime)s %(levelname)-8s %(message)s")
        logger.addHandler(log_handler)
    except OSError as err:
        print("Cannot open file {}".format(args.log_dest))
        print("OSError: {0}".format(err))

logger.debug("Logger initialized.")


#
# Read current environment and preapre WINE specific one
#
current_env_path = os.environ.get("PATH", default=None)
current_env_ldpreload = os.environ.get("LD_PRELOAD", default=None)
current_env_ldlibpath = os.environ.get("LD_LIBRARY_PATH", default="")
current_env_winedebug = os.environ.get("WINEDEBUG")
current_env_ninedebug = os.environ.get("NINEDEBUG")

wine_prefix = args.prefix_base + "/" + args.prefix if args.prefix else \
        home_dir + "/" + ".wine"
# wine_env_ldlibpath = "LD_LIBRARY_PATH="

# Populating environment
launcher_env = []
if current_env_ldpreload:
    wine_env_ldpreload = "LD_PRELOAD=" + current_env_ldpreload
    launcher_env.append(wine_env_ldpreload)

if current_env_winedebug:
    wine_env_winedebug = "WINEDEBUG=" + current_env_winedebug
else:
    wine_env_winedebug = "WINEDEBUG=" + config.get("general", "wine_debug")

if current_env_ninedebug:
    wine_env_ninedebug = "NINEDEBUG=" + current_env_ninedebug
else:
    wine_env_ninedebug = "NINEDEBUG=" + config.get("general", "nine_debug")

wine_env_prefix = "WINEPREFIX=" + wine_prefix

if args.wine_version == "system":
    wine_path = "/usr"
    wine_env_path = "PATH=" + current_env_path
else:
    wine_path = args.wine_dir
    wine_env_path = "PATH=" + args.wine_dir + ":" + current_env_path

if args.wine_arch == "32":
    wine_env_ldlibpath = "LD_LIBRARY_PATH=" + \
        wine_path + "/" + \
        config.get("general", "wine_lib32") + ":" + \
        current_env_ldlibpath
    wine_env_dllpath = "WINEDLLPATH=" +\
        wine_path + "/" + \
        config.get("general", "wine_lib32") + "/wine"
    wine_env_arch = "win32"
else:
    wine_env_ldlibpath = "LD_LIBRARY_PATH=" + \
        wine_path + "/" + \
        config.get("general", "wine_lib32") + ":" + \
        wine_path + "/" + \
        config.get("general", "wine_lib64") + ":" + \
        current_env_ldlibpath
    wine_env_dllpath = "WINEDLLPATH=" +\
        wine_path + "/" + \
        config.get("general", "wine_lib64") + "/wine"
    wine_env_arch = "win64"

wine_env_server = wine_path + "/bin/wineserver"
wine_env_loader = wine_path + "/bin/wine"

launcher_env.append(wine_env_ldlibpath)
launcher_env.append(wine_env_path)
launcher_env.append(wine_env_prefix)
launcher_env.append(wine_env_arch)
launcher_env.append(wine_env_server)
launcher_env.append(wine_env_loader)
launcher_env.append(wine_env_dllpath)
launcher_env.append(wine_env_winedebug)
launcher_env.append(wine_env_ninedebug)

print("Env:\n{}".format(launcher_env))
print("Command to run: {}".format(args.winecommand))

sys.exit(0)
