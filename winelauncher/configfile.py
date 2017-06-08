import configparser

from xdg.BaseDirectory import xdg_config_home, xdg_data_home

config = configparser.ConfigParser(default_section="general")

# Default config
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
