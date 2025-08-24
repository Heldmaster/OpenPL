import logging


def setup_logger() -> logging.Logger:
    logger: logging.Logger = logging.getLogger("OpenDLLogger")
    logger.setLevel(logging.INFO)
    handler: logging.StreamHandler = logging.StreamHandler()
    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger
