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
config_file = xdg_config_home + "/winelauncher.conf"
home_dir = os.path.expanduser("~")


#
# Command line arguments
#
parser = argparse.ArgumentParser(
    description="%(prog)s: a WINE wrapper to handle multiple prefixes",
    epilog="%(prog)s will forward LD_PRELOAD, \
            WINEDEBUG and NINEDEBUG environment variables to WINE")
parser.add_argument("-c", "--config",
                    help="alternate config file")
parser.add_argument("-p", "--prefix",
                    help="WINEPREFIX name (will be appended to prefix_base)")
parser.add_argument("-b", "--base",
                    help="prefixes base directory")
parser.add_argument("-a", "--arch",
                    help="set WINEARCH (32 or 64 bit)",
                    choices=["32", "64"])
parser.add_argument("-w", "--wine",
                    help="WINE version")
parser.add_argument("-d", "--winedir",
                    help="set WINE base directory")
parser.add_argument("-L", "--loglevel",
                    help="ste log level",
                    default="info")
parser.add_argument("-o", "--logoutput",
                    help="output to log file (or syslog)")
parser.add_argument("-l", "--list",
                    help="list WINE versions available",
                    action="store_true")
parser.add_argument("winecommand", nargs='+',
                    help="command to forward to WINE")

# Parse command line arguments: will override config_file values
args = parser.parse_args()
config_file = args.config if args.config else config_file

# Read config file or generate a default one it doesn't exists
config = configparser.ConfigParser()
if pathlib.Path(config_file) and config.read(config_file):
    print("Using configuration from {}".format(config_file))
else:
    config["general"] = {
        "prefix_base": xdg_data_home + "/wineprefixes",
        "wine_dir": "/opt/wine",
        "wine_lib32": "lib32",
        "wine_lib64": "lib",
        "wine_debug": "-all",
        "nine_debug": "-all"
    }
    config["logging"] = {
        "log": "syslog",
        "log_level": "info"
    }
    try:
        with open(config_file, mode="w") as newfile:
            config.write(newfile)
        print("Saved default config file {}".format(config_file))
        sys.exit(0)
    except OSError as err:
        print("Cannot open file {}".format(config_file))
        print("OSError: {0}".format(err))

# Other comman line arguments
prefix = args.prefix if args.prefix else None
prefix_base = args.base if args.base else config.get("general", "prefix_base")
wine_arch = args.arch if args.arch else None
wine_version = args.wine if args.wine else None
wine_dir = args.winedir if args.winedir else config.get("general", "wine_dir")
log_level = args.loglevel if args.loglevel \
        else config.get("logging", "log_level")
log_dest = args.logoutput if args.logoutput else config.get("logging", "log")
winecommand = args.winecommand


#
# List WINE versions installed
#
if args.list:
    system_wine = pathlib.Path("/usr/bin/wine")
    if system_wine.is_file():
        system_wine_version = str(subprocess.check_output(
            ["/usr/bin/wine", "--version"]), "utf-8")
    else:
        system_wine = None

    if pathlib.Path(wine_dir).exists():
        wine_versions_list = os.listdir(wine_dir)
    else:
        wine_versions_list = None

    if system_wine or wine_versions_list:
        if system_wine:
            print("System WINE version:\n\t{}".format(system_wine_version))
        else:
            print("No system-wine WINE found\n")

        if wine_versions_list:
            print("WINE versions available in {}:\n\n".format(wine_dir))
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
logger.setLevel(set_log_level(log_level))

if log_dest == "syslog":
    logger.addHandler(JournalHandler(SYSLOG_IDENTIFIER=prefix))
else:
    try:
        log_handler = logging.handlers.FileHandler(log_dest)
        log_handler.setFormatter("%(asctime)s %(levelname)-8s %(message)s")
        logger.addHandler(log_handler)
    except OSError as err:
        print("Cannot open file {}".format(log_dest))
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

wine_prefix = prefix_base + "/" + prefix if prefix else None
wine_env_ldlibpath = "LD_LIBRARY_PATH="

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

if wine_prefix:
    wine_env_prefix = "WINEPREFIX=" + wine_prefix

if wine_version:
    wine_path = wine_dir
    wine_env_path = "PATH=" + wine_dir + ":" + current_env_path
else:
    wine_path = "/usr"
    wine_env_path = "PATH=" + current_env_path

if wine_arch == "32":
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
if wine_env_prefix:
    launcher_env.append(wine_env_prefix)
launcher_env.append(wine_env_arch)
launcher_env.append(wine_env_server)
launcher_env.append(wine_env_loader)
launcher_env.append(wine_env_dllpath)
launcher_env.append(wine_env_winedebug)
launcher_env.append(wine_env_ninedebug)

print("Env:\n{}".format(launcher_env))
print("Command to run: {}".format(winecommand))

sys.exit(0)
