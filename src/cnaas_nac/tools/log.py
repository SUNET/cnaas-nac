import logging

from flask import current_app


def get_logger():
    if current_app:
        logger = current_app.logger
    else:
        logger = logging.getLogger('cnaas-nms')
        if not logger.handlers:
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
            # stdout logging
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    logger.setLevel(logging.DEBUG) #TODO: get from /etc config ?
    return logger
