var Service = require('node-linux').Service;
let os = require('os')
const config = require('config');

// Create a new service object
var svc = new Service({
  name:'vieramqtt',
  description: 'Viera MQTT',
  script: __dirname + '/vieramq.js',
  WorkingDirectory: __dirname,
  user: config.get('serviceuser')
});

svc.on('install',function(){
  //svc.start();
  console.log("Installed");
});

svc.install();