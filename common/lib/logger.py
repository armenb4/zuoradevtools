import os
import sys
import logging
from common.config.__const__ import __APP_NAME__

""" 
Environment variables
"""
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
APP_NAME = os.getenv("APP_NAME", __APP_NAME__).upper()

if LOG_LEVEL == "DEBUG":
    log_level = logging.DEBUG
elif LOG_LEVEL == "INFO":
    log_level = logging.INFO
elif LOG_LEVEL == "WARNING":
    log_level = logging.WARNING
elif LOG_LEVEL == "ERROR":
    log_level = logging.ERROR
elif LOG_LEVEL == "CRITICAL":
    log_level = logging.CRITICAL
else:
    log_level = logging.INFO  # default logging level


class AppLogger(logging.Logger):
    """
    Call this method to create an instance of logger. A default logging format is set when this method is called.
    """

    def update(self):
        if self.hasHandlers():
            self.handlers.clear()

        handler = logging.StreamHandler(sys.stdout)
        log_format = "%(asctime)s [%(levelname)-8s][%(name)s][%(filename)s:%(lineno)d] - %(message)s"

        handler.setFormatter(logging.Formatter(log_format))
        self.addHandler(handler)
        self.setLevel(log_level)
        self.propagate = False

    def set_log_mdc(self, tracing_format: str):
        log_format = "%(asctime)s [%(levelname)-8s][%(name)s][%(filename)s:%(lineno)d] "
        if tracing_format:
            log_format += f"[{tracing_format}] - %(message)s"
        else:
            log_format += "- %(message)s"

        if self.hasHandlers():
            for handler in self.handlers:
                handler.setFormatter(logging.Formatter(log_format))


logger = AppLogger(APP_NAME)
logger.update()
