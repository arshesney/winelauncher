import logging

from systemd import journal


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


def logger_init(tag, dest, level):
    logger = logging.getLogger(__name__)
    logger.setLevel(set_log_level(level))

    if dest == "journal":
        # FIXME: currently not working, no output to journal
        log_handler = journal.JournalHandler(SYSLOG_IDENTIFIER=tag)
        log_format = logging.Formatter("%(levelname)-8s - %(message)s")
    elif dest == "console":
        log_handler = logging.StreamHandler()
        log_format = logging.Formatter(
            "%(asctime)s - %(levelname)-8s - %(message)s")
    else:
        try:
            log_handler = logging.FileHandler(dest)
            log_format = logging.Formatter(
                "%(asctime)s %(levelname)-8s {} %(message)s".format(tag))
        except OSError as err:
            print("Cannot open file {}".format(dest))
            print("OSError: {0}".format(err))

    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    return logger
