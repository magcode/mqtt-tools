
import colorlog
from colorlog import ColoredFormatter
from logging_loki import LokiHandler, emitter

def setupLogging(logger, config):
    logger.setLevel(config["LOG_LEVEL"])
    lokiEnabled = config["LOG_LOKI"]
    lokiUrl = config["LOKI_URL"]
    if lokiEnabled:
        emitter.LokiEmitter.level_tag = "level"
        loggingHandler = LokiHandler(url=lokiUrl + "/loki/api/v1/push", tags={"monitor": "grafana"}, version="1")
        # loggingHandler.setLevel(lokiLevel.upper())
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