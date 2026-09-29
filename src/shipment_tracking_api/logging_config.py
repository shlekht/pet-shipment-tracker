import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)

    formatter = jsonlogger.JsonFormatter( # type: ignore
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )