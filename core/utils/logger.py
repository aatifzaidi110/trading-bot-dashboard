# utils/logger.py

import logging
import os

def setup_logger(name, log_file=None, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler = logging.FileHandler(log_file) if log_file else logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)

    return logger