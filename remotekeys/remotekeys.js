var yamlConfig = require('node-yaml-config');
const { createLogger, transports, format } = require('winston');
const ExclusiveKeyboard = require('exclusive-keyboard');
const LokiTransport = require('winston-loki');
const process = require('node:process');
var mqtt = require('mqtt')
var moment = require('moment');

var buffer = []
var keyboards = []

const longPressTime = 400
const repeatTime = 250

var config = yamlConfig.load(__dirname + '/config.yaml');

const testmode = config.testmode
const topic = config.mqtt.topic;
const broker = config.mqtt.broker;
const loggingConsole = config.logging.console
const loggingLoki = config.logging.loki
const loggingLevel = config.logging.level

var loggingTransports = []
if (loggingConsole || !loggingLoki) {
  var transportCon = new transports.Console({
    format: format.combine(
      format.colorize(),
      format.timestamp(),
      format.printf(({ level, message, timestamp }) => {
        return `${timestamp} ${level}: ${message}`;
      }),
    )
  });
  loggingTransports.push(transportCon);
}

if (loggingLoki) {
  var transportLok = new LokiTransport({
    host: config.logging.lokiUrl,
    labels: { appname: "remotekeys", monitor: "grafana" },
    batching: false,
    gracefulShutdown: false
  });
  loggingTransports.push(transportLok);
}

const logger = createLogger({ level: loggingLevel, transports: loggingTransports });

logger.info("Remotekeys MQTT interface");
logger.info("Using broker: " + broker);
logger.info("Using topic: " + topic);
if (testmode) logger.info("Testmode enabled, will not send MQTT messages.");
customkeys = config.customKeys
multiSupport = config.multiSupport


config.events.forEach(element => {
  try {
    logger.info("Adding keyboard " + element)
    const keyboard = new ExclusiveKeyboard(element, true);
    keyboard.on('error', keyboardError);
    keyboard.on('keyup', keyup);
    keyboard.on('keypress', keydown);
    keyboard.on('close', keyboardClose);
    keyboards.push(keyboard);
  } catch (error) {
    logger.error(error);
  }
});


var mqttClient = mqtt.connect(config.mqtt.broker);

mqttClient.on('connect', function () {
  logger.info("Connected to MQTT broker");
})

mqttClient.on('close', function () {
  logger.info("MQTT connection closed")
})

mqttClient.on('error', function (error) {
  logger.error("MQTT connection error " + error)
})

function keyboardError(error) {
  logger.error("Got keyboard error %s", error)
  console.error("Got keyboard error %s", error)
}

function keyboardClose() {
  logger.info("Keyboard closed");
}

function keydown(keyboardEvent) {
  var timestamp = moment().format('x')
  var keyId = keyboardEvent.keyId

  if (customkeys[keyboardEvent.keyCode] || !keyId) {
    keyId = customkeys[keyboardEvent.keyCode];
  }

  var bevent = { key: keyId, time: timestamp }
  logger.debug(`keydown Added ${keyId} with timestamp ${timestamp}`);
  buffer.push(bevent)

  if (multiSupport.includes(keyboardEvent.keyCode)) {
    setTimeout(function () {
      checkRelease(keyId)
    }, repeatTime);
  } else {
    setTimeout(function () {
      checkRelease(keyId)
    }, longPressTime);
  }
}


// checks if the key is still waiting to be released
// if yes, release it and send "Longpress"
function checkRelease(keyId) {
  const result = buffer.find(keyboardEvent => keyboardEvent.key === keyId);
  if (result) {
    if (multiSupport.includes(keyId)) {
      if (testmode) {
        logger.info("Shortpress " + keyId)
      } else {
        mqttClient.publish(topic + '/' + keyId, 'trigger')
      }
      setTimeout(function () {
        checkRelease(keyId)
      }, repeatTime);
    } else {
      if (testmode) {
        logger.info("Longpress " + keyId)
      } else {
        mqttClient.publish(topic + '/' + keyId + '-LONG', 'trigger')
      }
      buffer = buffer.filter(keyboardEvent => keyboardEvent.key !== keyId)
    }
  }
}

function keyup(keyboardEvent) {
  var keyId = keyboardEvent.keyId
  logger.debug(`keyup ${keyId}`);
  if (customkeys[keyboardEvent.keyCode] || !keyId) {
    keyId = customkeys[keyboardEvent.keyCode];
  }

  const result = buffer.find(keyboardEvent => keyboardEvent.key === keyId);
  if (result) {
    buffer = buffer.filter(keyboardEvent => keyboardEvent.key !== keyId)

    //if (! multiSupport.includes(keyId)) {
    if (testmode) {
      logger.info("Shortpress " + keyId)
    } else {
      mqttClient.publish(topic + '/' + keyId, 'trigger')
    }
    //}
  }
}


process.on('exit', () => {
  // Workaround for the process not terminating on process.exit() due to input-event
  // calling fs.createReadStream() (which, for unknown reason, prevents exit).
  process.kill(process.pid, 'SIGTERM');
});

function handleExit(signal) {
  logger.info(`Received ${signal}. Shutdown.`)
  mqttClient.end();
  keyboards.forEach(element => {
    logger.info(`Closing ${element.dev}`);
    element.close();
  })

  setTimeout(function () {
    logger.info("Stopped.");
    logger.close();
    process.exit(0);
  }, 2000);
}
process.on('SIGINT', handleExit);
process.on('SIGQUIT', handleExit);