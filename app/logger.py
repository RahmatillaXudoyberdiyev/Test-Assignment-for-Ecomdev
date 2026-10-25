import logging
import sys


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure system-wide logging format and handlers."""
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(level)

    return root_logger


setup_logging()
