var Service = require('node-linux').Service;
let os = require('os')
const config = require('config');

// Create a new service object
var svc = new Service({
  name: 'pihole-mqtt',
  description: 'Pi-hole MQTT',
  script: __dirname + '/pihole.js',
  WorkingDirectory: __dirname,
  user: config.get('serviceuser')
});

svc.on('install', function () {
  //svc.start();
  console.log("Installed");
});

svc.install();