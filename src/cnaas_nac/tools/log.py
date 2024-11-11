import logging

from flask import current_app


def get_logger():
    if current_app:
        logger = current_app.logger
    else:
        logger = logging.getLogger('cnaas-nac')
        if not logger.handlers:
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger
