import logging

from app.core.logging.log_handler import LogMongoHandler


def logging_init(app):
    set_logging_lvl(app, 'DEBUG')


def set_logging_lvl(app, level='DEBUG'):
    logging.basicConfig(level=level)
