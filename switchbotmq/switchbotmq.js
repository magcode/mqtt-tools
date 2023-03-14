// sudo apt-get install libcap2-bin
// sudo setcap cap_net_raw+eip $(eval readlink -f `which node`)

let Switchbot = require('node-switchbot');
var mqtt = require('mqtt');
const schedule = require('node-schedule');
const LoggerFactory = require("./Logger.js");
const config = require('config');

const loggingConfig = config.get('logging');
const progName = config.get('name');
const logFac = new LoggerFactory(loggingConfig, progName);
const logger = logFac.getLogger();

let switchbot = new Switchbot();

const mqttConfig = config.get('mqtt');
const broker = mqttConfig.get('broker');
const topic = mqttConfig.get('topic');
const mqUser = mqttConfig.get('user');
const mqPort = mqttConfig.get('port');
const mqPass = mqttConfig.get('password');
var mqttClient = mqtt.connect(broker, { "clientId": progName, "port": mqPort, "username": mqUser, "password": mqPass });

logger.info("switchbotmq started.");

mqttClient.on("connect", function () {
  logger.info("Connected to MQTT broker");
})

mqttClient.on("close", function () {
  logger.info("MQTT disconnected");
})

mqttClient.on('error', function (error) {
  console.error('MQTT error: ' + error);
});

const job = schedule.scheduleJob('*/' + config.get('schedule') + ' * * * *', scanAndPublish)

async function scanAndPublish() {
  logger.debug("startScan");
  await switchbot.startScan({ "model": "i", "id": "f55307f0ff3d" });
  switchbot.onadvertisement = (ad) => {
    //logger.debug(JSON.stringify(ad, null, '  '));
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
    }
    switchbot.stopScan();
  };
  await switchbot.wait(20000);

  logger.debug("stopscan");
  switchbot.stopScan();
}

process.on('SIGINT', function () {
  console.log("Caught interrupt signal");
  mqttClient.end();
  switchbot.stopScan();

  setTimeout(function () {
    console.log("Exit");
    process.exit();
  }, 3000);
});

// (async () => {
//   // Start to monitor advertisement packets
//   console.log("startScan");
//   await switchbot.startScan({"model":"i","id":"f55307f0ff3d"});
//   // Set an event hander
//   switchbot.onadvertisement = (ad) => {
//     console.log(JSON.stringify(ad, null, '  '));
//     mqttClient.publish(topic + '/hello', 'trigger');
//     switchbot.stopScan();
//   };
//   // Wait 10 seconds
//   await switchbot.wait(10000);
//   // Stop to monitor
//   switchbot.stopScan();
//   process.exit();
// })();