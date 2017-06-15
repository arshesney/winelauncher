import os
import pathlib
import subprocess
import sys
import logger

from args import parser

args = log = None


def read_command_args():
    """ Read arguments from command line """
    global args
    arglist = sys.argv[1:]

    args = parser.parse_args(arglist)


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
    read_command_args()
    syslog_tag = args.prefix if args.prefix else 'wine'
    log = logger.logger_init(syslog_tag, args.log_output, args.log_level)
    log.debug("Logger initialized.")
    log.info("Args: {}".format(args))

    if not args.winecommand or args.list:
        list_wine_versions()

    sys.exit(0)


if __name__ == "__main__":
    main()
