const { Retrier } = require('@jsier/retrier');
const { exec } = require("child_process");
const cron = require('node-cron');
const config = require('config');
var mqtt = require('mqtt')

const broker = config.get('mqtt.broker');
const binary = config.get('exec');
const usbport = config.get('usbport');
const topic = config.get('mqtt.topic');
const everyXMinutes = config.get('schedule');

var mqttClient = mqtt.connect(broker);

console.log("PolluComE MQTT interface");
console.log("Using broker: " + broker);
console.log("Using topic: " + topic);
console.log("Using binary: " + binary);
console.log("Sending data every: " + everyXMinutes + " minute");
console.log();

mqttClient.on('connect', function () {
    console.log("Connected to MQTT broker");
    mqttClient.subscribe(topic + '/set', function (err) {
        if (!err) {
            console.log("Subscribed");
        }
    })
})

const options = { limit: 5, delay: 20000 };
const retrier = new Retrier(options);

var timer = "*/" + everyXMinutes + ' * * * *';
cron.schedule(timer, function () {
    retrier.resolve(attempt => new Promise(
        function (resolve, reject) {
			exec(binary + " -d " + usbport, (error, stdout, stderr) => {
                if (error) {
                    console.error(`error: ${error.message}`);
                    reject("Error")
                }
                if (stderr) {
                    console.error(`stderr: ${stderr}`);
                    reject("Error")
                }
                var lines = stdout.toString().split('\n');

                if (lines.includes("No data")) {                    
                    reject("No data")
                }

                var data = {};
                lines.forEach(function (line) {
                    if (line != '' && !line.includes("No data")) {
                        var string = line.split(' ');
                        data[string[0]] = string[1];
                    }
                });
				resolve(data)
            });
        })
    )
    .then(
		result => {
                Object.keys(result).forEach(function (key, index) {
                    var top = topic + "/" + key
                    mqttClient.publish(top, result[key])
                });
		},
        error => console.error(error)
    );
});