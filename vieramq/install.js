var Service = require('node-service-linux').Service;

// Create a new service object
var svc = new Service({
  name:'Viera MQTT',
  description: 'Viera MQTT',
  script: __dirname + 'vieramq.js'
});

console.log(__dirname);

svc.on('install',function(){
  svc.start();
});

//svc.install();