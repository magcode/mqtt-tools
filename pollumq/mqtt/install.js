var Service = require('node-linux').Service;
let os = require('os')
const config = require('config');

// Create a new service object
var svc = new Service({
  name: 'pollumq',
  description: 'Pollucom MQTT Gateway',
  script: __dirname + '/pollumq.js',
  WorkingDirectory: __dirname,
  StandardOutput: 'inherit',
  StandardError: 'inherit',
  user: config.get('serviceuser')
});

svc.on('install', function () {
  console.log("Installed");
});

svc.install();