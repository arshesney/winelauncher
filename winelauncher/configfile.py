import configparser
import pathlib
import sys

from xdg.BaseDirectory import xdg_config_home, xdg_data_home

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
