const {VieraKeys, Viera} = require('node-panasonic-viera');
const config = require('config');
var mqtt = require('mqtt');

const viera = new Viera();

const vieraIP = config.get('vieraIP');
const broker = config.get('mqtt.broker');
const topic = config.get('mqtt.topic');


console.log("Viera MQTT interface");
console.log("Using broker: " + broker);
console.log("Using topic: " + topic);
console.log("Using viera: " + vieraIP);
console.log();

var mqttClient  = mqtt.connect(broker);

mqttClient.on("connect",function(){	
  console.log("Connected to mqtt broker");
  mqttClient.subscribe(topic);
})

mqttClient.on('message', (topic, message) => {
  switch (topic) {
    case topic:
      return handleVieraCommand(message)
  } 
  console.warn('No handler for topic %s', topic)
})

function handleVieraCommand (message) {
    console.log(VieraKeys.hasOwnProperty(message));
    console.log(VieraKeys[message]);
    viera.connect(vieraIP).then(() => {
        return viera.sendKey(VieraKeys[message]);
    }).catch((error) => {
        console.log(error);
    });
}