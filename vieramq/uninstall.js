var Service = require('node-service-linux').Service;

var svc = new Service({
  name:'vieramqtt',
  script: __dirname + 'vieramq.js',  
});

svc.on('uninstall',function(){
  console.log('Uninstall complete.');
  console.log('The service exists: ', svc.exists());
});

svc.uninstall();
