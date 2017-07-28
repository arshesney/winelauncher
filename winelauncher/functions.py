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
        "mesa_glthread": "true", # Enable OpenGL multithread
        "PULSE_LATENCY_MSEC": "60", # Fix for crackling audio
        "FREETYPE_PROPERTIES": "truetype:interpreter-version=35", # Fix for ugly fonts
        }
}


ef list_wine_versions():
    """ Find installed WINE versions """
    system_wine = pathlib.Path("/usr/bin/wine")
    if system_wine.is_file():
        system_wine_version = str(subprocess.check_output(["/usr/bin/wine", "--version"]), "utf-8")
    else:
        system_wine = None

    if pathlib.Path(args.wine_base).exists():
        wine_versions_list = os.listdir(args.wine_base)
    else:
        wine_versions_list = None

    if system_wine or wine_versions_list:
        if system_wine:
            print("System WINE version:\n\t{}".format(system_wine_version))
        else:
            print("No system-wine WINE found\n")

        if wine_versions_list:
            print("WINE versions available in {}:\n\n".format(args.wine_base))
            for winedir in wine_versions_list:
                print("\t{}".format(winedir))
        else:
            print("No additional WINE installs available")
    else:
        print("No WINE found")
        sys.exit(1)


def consume_output(pipe, consume):
    with pipe:
        for line in iter(pipe.readline, b''):
            consume(line)
