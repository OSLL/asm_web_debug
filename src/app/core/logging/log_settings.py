import logging

from app.core.logging.log_handler import LogMongoHandler


def logging_init(app):
    app.logger.addHandler(LogMongoHandler())
    set_logging_lvl(app, "DEBUG")


def set_logging_lvl(app, level="DEBUG"):
    app.logger.debug(f"Set logging level to {level}")
    app.logger.setLevel(level)
