import logging
import os


def get_logger(name: str):
    log_level = os.environ.get('LOG_LEVEL', logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
