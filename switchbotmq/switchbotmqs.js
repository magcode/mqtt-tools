// sudo apt-get install libcap2-bin
// sudo setcap cap_net_raw+eip $(eval readlink -f `which node`)

let Switchbot = require('node-switchbot');
var mqtt = require('mqtt');
const LoggerFactory = require("./Logger.js");
const config = require('config');

const loggingConfig = config.get('logging');
const progName = config.get('name');
const logFac = new LoggerFactory(loggingConfig, progName);
const logger = logFac.getLogger();

const mqttConfig = config.get('mqtt');
const broker = mqttConfig.get('broker');
const topic = mqttConfig.get('topic');
const mqUser = mqttConfig.get('user');
const mqPort = mqttConfig.get('port');
const mqPass = mqttConfig.get('password');

var mqttClient = mqtt.connect(broker, { "clientId": progName, "port": mqPort, "username": mqUser, "password": mqPass });
mqttClient.on("connect", function () {
  logger.debug("Connected to MQTT broker");
})

mqttClient.on("close", function () {
  logger.debug("MQTT disconnected");
})

mqttClient.on('error', function (error) {
  console.error('MQTT error: ' + error);
});

logger.info("switchbotmq started.");
logger.debug("startScan");

let switchbot = new Switchbot();

switchbot
  .startScan({ "model": "i", "id": "f55307f0ff3d", "quick": true })
  .then(() => {
    // Set an event hander
    switchbot.onadvertisement = (ad) => {
      logger.debug(JSON.stringify(ad, null, '  '));
      if (ad.serviceData &&
        ad.serviceData.temperature &&
        ad.serviceData.temperature.c &&
        ad.serviceData.humidity &&
        ad.serviceData.battery) {

        var mtopic = topic + '/' + ad.id + "/temperature";
        var val = ad.serviceData.temperature.c.toString();
        logger.debug("Publishing %s to %s", val, mtopic);
        mqttClient.publish(mtopic, val);

        mtopic = topic + '/' + ad.id + "/humidity";
        val = ad.serviceData.humidity.toString();
        logger.debug("Publishing %s to %s", val, mtopic);
        mqttClient.publish(mtopic, val);

        mtopic = topic + '/' + ad.id + "/battery";
        val = ad.serviceData.battery.toString();
        logger.debug("Publishing %s to %s", val, mtopic);
        mqttClient.publish(mtopic, val);
        logger.info("OK, sent data.");
      };
    }
    // Wait 10 seconds
    return switchbot.wait(6000);
  })
  .then(() => {
    logger.debug("Done");
    mqttClient.end(true);
    switchbot.stopScan();
    logger.debug("stopscan");
    setTimeout(function () {
      process.exit();
    }, 1500);
  });