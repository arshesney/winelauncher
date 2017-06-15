import os
import pathlib
import subprocess
import sys
import logger

from args import parser, config

args = log = None
wine_env = {}


def list_wine_versions():
    """ Find installed WINE versions """
    system_wine = pathlib.Path("/usr/bin/wine")
    if system_wine.is_file():
        system_wine_version = str(subprocess.check_output(
            ["/usr/bin/wine", "--version"]), "utf-8")
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


def main():
    syslog_tag = args.prefix if args.prefix else 'wine'
    log = logger.logger_init(syslog_tag, args.log_output, args.log_level)
    log.debug("Logger initialized.")
    log.info("Args: {}".format(args))
    # Load config from file or generate a default one

    if not args.winecommand or args.list:
        list_wine_versions()

    # Set the executables to use and populate the environment
    # check if LD_LIBRARY_PATH is set
    cur_ld_path = os.environ.get('LD_LIBRARY_PATH', None)
    # Add the : limiter before the eventual existing variable to avoid
    # including the current path in LD_LIBRARY_PATH
    cur_ld_path = ':' + cur_ld_path if cur_ld_path else ""
    if args.wine_version == "system":
        wine_base = '/usr'
        wine_env['PATH'] = os.environ.get('PATH')
    else:
        wine_base = args.wine_base
        wine_env['PATH'] = wine_base + '/bin:' + os.environ.get('PATH')

    wine_env['WINEPREFIX'] = args.prefix
    wine_env['WINEVERPATH'] = wine_base
    wine_env['WINELOADER'] = wine_base + '/bin/wine'
    wine_env['WINESERVER'] = wine_base + '/bin/wineserver'

    if args.wine_arch == "32":
        wine_env['WINEARCH'] = 'win32'
        wine_env['WINEDLLPATH'] = wine_base + '/' + args.wine_lib32 + '/wine'
        wine_env['LD_LIBRARY_PATH'] = wine_base + '/' + args.wine_lib32 \
            + cur_ld_path
    else:
        wine_env['WINEARCH'] = 'win64'
        wine_env['WINEDLLPATH'] = wine_base + '/' + args.wine_lib64 + '/wine'
        wine_env['LD_LIBRARY_PATH'] = wine_base + '/' + args.wine_lib32 + ':' \
            + wine_base + '/' + args.wine_lib64 + cur_ld_path

    if os.environ.get('LD_PRELOAD'):
        wine_env['LD_PRELOAD'] = os.environ.get('LD_PRELOAD')

    wine_env['WINEDEBUG'] = os.environ.get('WINEDEBUG', args.wine_debug)
    wine_env['NINEDEBUG'] = os.environ.get('NINEDEBUG', args.wine_debug)

    logger.info('Enviroment: {}'.format(wine_env))
    # wine_p = subprocess.Popen()

    sys.exit(0)


if __name__ == "__main__":
    main()
