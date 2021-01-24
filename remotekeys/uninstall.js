var Service = require('node-linux').Service;

var svc = new Service({
  name:'remotekeys',
  script: __dirname + '/remotekeys.js',  
});

svc.on('uninstall',function(){
  console.log('Uninstall complete.');
  console.log('The service exists: ', svc.exists());
});

svc.uninstall();
