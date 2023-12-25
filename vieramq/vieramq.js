const {VieraKeys, Viera} = require('node-panasonic-viera');
const config = require('config');
var mqtt = require('mqtt');

const viera = new Viera();

const vieraIP = config.get('vieraIP');
const broker = config.get('mqtt.broker');
const topic = config.get('mqtt.topic');
const topicCommand = topic+"/command/set";
const topicAppCommand = topic+"/appcommand/set";
const volumeCommand = topic+"/volume/set";


console.log("Viera MQTT interface");
console.log("Using broker: " + broker);
console.log("Using topic: " + topic);
console.log("Using viera: " + vieraIP);
console.log();

var mqttClient  = mqtt.connect(broker);

mqttClient.on("connect",function(){	
  console.log("Connected to mqtt broker");
  mqttClient.subscribe(topicCommand);
  mqttClient.subscribe(topicAppCommand);
  mqttClient.subscribe(volumeCommand);
})

mqttClient.on('message', (topic, message) => {
  //console.log("topic:" + topic + " message:" + message)
  switch (topic) {
    case topicCommand:
      return handleVieraCommand("key",message)
    case volumeCommand:
      return handleVieraCommand("volume",message)
    case topicAppCommand:
      return handleVieraCommand("appcommand","" + message)
  } 
  console.warn('No handler for topic %s', topic)
})

function handleVieraCommand (type, message) {
    viera.connect(vieraIP).then(() => {
        if (type=="key") {
          return viera.sendKey(VieraKeys[message]);
        } else if (type=="appcommand") {
          return viera.sendAppCommand(message);
        } else if (type=="volume") {
          return viera.setVolume(parseInt(message));
        }
    }).catch((error) => {
        console.log(error);
    });
}