var Service = require('node-linux').Service;
let os = require('os')
const config = require('config');

var svc = new Service({
  name: config.get('name'),
  description: 'Switchbot Sensor MQTT gateway',
  script: __dirname + '/switchbotmq.js',
  WorkingDirectory: __dirname,
  user: config.get('serviceuser')
});

svc.on('install', function () {
  console.log("Installed");
});

svc.install();