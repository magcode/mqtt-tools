const http = require('http');
const config = require('config');
var mqtt = require('mqtt');
const cron = require('node-cron');

const piHoleIP = config.get('piHoleIP');
const broker = config.get('mqtt.broker');
const topic = config.get('mqtt.topic');
const statusTopic = topic + "/status";
const piHolePassword = config.get('piHolePassword');
const everyXMinutes = 1;

console.log("Pihole MQTT interface");
console.log("Using broker: " + broker);
console.log("Using topic: " + topic);
console.log("Using Pihole: " + piHoleIP);
console.log();

var mqttClient = mqtt.connect(broker);

mqttClient.on("connect", function () {
	console.log("Connected to mqtt broker");
	mqttClient.subscribe(statusTopic + "/set");
})

mqttClient.on('message', (topic, message) => {
	var param = (message == 'disabled') ? 'disable' : 'enable';
	return setStatus(param)
})

var timer = "*/" + everyXMinutes + ' * * * *';
cron.schedule(timer, function () {
	getStatus();
});

function setStatus(enable) {
	http.get('http://' + piHoleIP + '/admin/api.php?' + enable + '&auth=' + piHolePassword, (resp) => {
		let data = '';

		// A chunk of data has been received.
		resp.on('data', (chunk) => {
			data += chunk;
		});

		// The whole response has been received. Print out the result.
		resp.on('end', () => {
			var enabled = JSON.parse(data).status;
			mqttClient.publish(statusTopic, enabled);
		});

	}).on("error", (err) => {
		console.log("Error: " + err.message);
	});
}


function getStatus() {
	http.get('http://' + piHoleIP + '/admin/api.php?summary&auth=' + piHolePassword, (resp) => {
		let data = '';

		// A chunk of data has been received.
		resp.on('data', (chunk) => {
			data += chunk;
		});

		// The whole response has been received. Print out the result.
		resp.on('end', () => {
			var enabled = JSON.parse(data).status;
			mqttClient.publish(statusTopic, enabled);
		});

	}).on("error", (err) => {
		console.log("Error: " + err.message);
	});
}