const { createLogger, transports, format } = require("winston");
const { combine, timestamp, splat, colorize, printf } = format;
const LokiTransport = require("winston-loki");
require('winston-daily-rotate-file');

class LoggerFactory {
    constructor(config, appname) {
        this.logger = createLogger();
        if (config.loki.enabled) {
            const lokiTransport = new LokiTransport({
                host: config.loki.url,
                level: config.loki.level,
                batching: false,
                gracefulShutdown: false,
                format: format.combine(
                    format.splat(),
                    format.simple()
                ),
                labels: { appname: appname }
            });
            this.logger.add(lokiTransport)
        };
        if (config.file.enabled) {
            const fileTransport = new transports.DailyRotateFile({
                filename: appname + '-%DATE%.log',
                datePattern: 'YYYY-MM-DD',
                zippedArchive: true,
                maxSize: '20m',
                maxFiles: '10',
                "format": combine(
                    timestamp(),
                    splat(),
                    timestamp({
                        "format": "YYYY-MM-DD HH:mm:ss.SSS"
                    }),
                    printf(
                        info => `${info.timestamp} ${info.level} ${info.message}`
                    )
                ),
                level: config.file.level
            });
            this.logger.add(fileTransport)
        };
        if (config.console.enabled) {
            const consoleTransport = new transports.Console({
                "format": combine(
                    timestamp(),
                    splat(),
                    colorize({ message: false }),
                    timestamp({
                        "format": "YYYY-MM-DD HH:mm:ss.SSS"
                    }),
                    printf(
                        info => `${info.timestamp} ${info.level} ${info.message}`
                    )
                ),
                level: config.console.level
            });
            this.logger.add(consoleTransport)
        };
    }
    getLogger() {
        return this.logger;
    }
}

module.exports = LoggerFactory