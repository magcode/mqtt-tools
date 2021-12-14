var mqtt = require('mqtt');
var exec = require('child_process').exec;
var fs = require('fs');

eval(fs.readFileSync('config.js') + '');

const broker = config.broker;
const topic = config.topic;
const monitorId = config.monitorId;
const factor = config.factor;

console.log("Auto brightness for Windows");
console.log("Using broker: " + broker);
console.log("Using topic: " + topic);
console.log("Using factor: " + factor);
console.log("Using monitorId: " + monitorId);

var mqttClient = mqtt.connect(broker);
var currentValue = 0;

mqttClient.on("connect", function () {
	console.log("Connected to mqtt broker");
	mqttClient.subscribe(topic);
})

mqttClient.on('message', function (inTopic, message, packet) {
	switch (inTopic) {
		case topic:
			var val = parseFloat(message);
			val = val * factor;
			valInt = Math.round(val);
			if (valInt > 100) { valInt = 100 }
			if (currentValue != valInt) {
				var command = '%LOCALAPPDATA%\\Microsoft\\WindowsApps\\Monitorian.exe /set "' + monitorId + '" ' + valInt;
				console.log("Running: %s, orig value: %s", command, message);
				currentValue = valInt
				var child = exec(command, function (error, stdout, stderr) {
					console.log(stdout);
					if (error != null) {
						console.log(stderr);
					}
				});
			}

	}
});