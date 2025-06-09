import colorlog
import logging
from colorlog import ColoredFormatter
from logging_loki import LokiHandler, emitter


def setupLogging(config):
    logger = logging.getLogger(config["LOG_APP"])
    logger.setLevel(config["LOG_LEVEL"])
    lokiEnabled = config["LOG_LOKI"]
    lokiUrl = config["LOKI_URL"]
    if lokiEnabled:
        emitter.LokiEmitter.level_tag = "level"
        loggingHandler = LokiHandler(
            url=lokiUrl + "/loki/api/v1/push", tags={"monitor": "grafana", "appname": config["LOG_APP"]}, version="1"
        )
        logger.addHandler(loggingHandler)

    consoleEnabled = config["LOG_CONSOLE"]
    if consoleEnabled:
        handler = colorlog.StreamHandler()
        formatter = ColoredFormatter(
            "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )
        handler.setFormatter(formatter)
        # handler.setLevel(consoleLevel.upper())
        logger.addHandler(handler)
    return logger
