var Service = require('node-linux').Service;
let os = require('os')
var yaml_config = require('node-yaml-config');
var config = yaml_config.load(__dirname + '/config.yaml');

// Create a new service object
var svc = new Service({
  name:'remotekeys',
  description: 'Remote Keyboard MQTT Gateway',
  script: __dirname + '/remotekeys.js',
  WorkingDirectory: __dirname,
  user: config.serviceuser
});

svc.on('install',function(){
  console.log("Installed");
});

svc.install();