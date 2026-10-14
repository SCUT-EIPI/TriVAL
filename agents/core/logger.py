import logging
import sys

LOGGER_NAMESPACE = "agents"
LOG_FORMAT = "%(asctime)s | %(message)s"
TIME_FORMAT = "%H:%M:%S"


def project_log_filter(record: logging.LogRecord) -> bool:
    """Allow logs that come from this project's namespace."""
    return record.name.startswith(LOGGER_NAMESPACE)


def get_logger(name: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """Create a stdout logger scoped to this project."""
    logger_name = name or LOGGER_NAMESPACE
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=TIME_FORMAT))
    handler.addFilter(project_log_filter)
    logger.addHandler(handler)

    return logger


logger = get_logger()
__all__ = ["get_logger", "logger"]
