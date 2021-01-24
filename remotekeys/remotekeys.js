var yaml_config = require('node-yaml-config');
const ExclusiveKeyboard = require('exclusive-keyboard');
var mqtt = require('mqtt')
var moment = require('moment');

var buffer = []
var testmode = false

var config = yaml_config.load(__dirname + '/config.yaml');
const topic = config.mqtt.topic;
const broker = config.mqtt.broker;


console.log("Remotekeys MQTT interface");
console.log("Using broker: " + broker);
console.log("Using topic: " + topic);
console.log();

var mqttClient = mqtt.connect(config.mqtt.broker);

mqttClient.on('connect', function () {
  console.log("Connected to MQTT broker");
})

const keyboard1 = new ExclusiveKeyboard(config.event1, true);
const keyboard2 = new ExclusiveKeyboard(config.event2, true);
const keyboard3 = new ExclusiveKeyboard(config.event3, true);

var longPressTime = 400
var repeatTime = 250

customkeys = {
  '582': 'KEY_MIC',
  '163': 'KEY_NEXTSONG',
  '164': 'KEY_PLAYPAUSE',
  '165': 'KEY_PREVIOUSSONG',
  '158': 'KEY_BACK',
  '172': 'KEY_HOMEPAGE'
};

multiSupport = ['KEY_VOLUMEDOWN',
  'KEY_VOLUMEUP',
  'KEY_DOWN',
  'KEY_UP',
  'KEY_LEFT',
  'KEY_RIGHT']

keyboard1.on('keyup', keyup);
keyboard2.on('keyup', keyup);
keyboard3.on('keyup', keyup);

keyboard1.on('keypress', keydown);
keyboard2.on('keypress', keydown);
keyboard3.on('keypress', keydown);

console.log("Started");

function keydown(keyboardEvent) {
  var timestamp = moment().format('x')
  var keyId = keyboardEvent.keyId
  if (!keyId) {
    keyId = customkeys[keyboardEvent.keyCode];
  }

  var bevent = { key: keyId, time: timestamp }
  //console.log('Added ' + keyId + ' with timestamp ' + timestamp)
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
        console.log("Shortpress " + keyId)
      } else {
        mqttClient.publish(topic + '/' + keyId, 'trigger')
      }
      setTimeout(function () {
        checkRelease(keyId)
      }, repeatTime);
    } else {
      if (testmode) {
        console.log("Longpress " + keyId)
      } else {
        mqttClient.publish(topic + '/' + keyId + '-LONG', 'trigger')
      }
      buffer = buffer.filter(keyboardEvent => keyboardEvent.key !== keyId)
    }
  }
}

function keyup(keyboardEvent) {
  var keyId = keyboardEvent.keyId
  //console.log(keyboardEvent.keyCode);
  if (!keyId) {
    keyId = customkeys[keyboardEvent.keyCode];
  }

  const result = buffer.find(keyboardEvent => keyboardEvent.key === keyId);
  if (result) {
    buffer = buffer.filter(keyboardEvent => keyboardEvent.key !== keyId)

    //if (! multiSupport.includes(keyId)) {
    if (testmode) {
      console.log("Shortpress " + keyId)
    } else {
      mqttClient.publish(topic + '/' + keyId, 'trigger')
    }
    //}
  }
}
