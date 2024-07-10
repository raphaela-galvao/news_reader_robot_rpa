import logging


def setup_logger(name):
    # specific name
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # sends messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # defines how log messages will be formatted
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s ')

    # Associates formatting with the handler
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger