var Service = require('node-linux').Service;
const config = require('config');

var svc = new Service({
  name: config.get('name'),
  script: __dirname + '/switchbotmq.js',
});

svc.on('uninstall', function () {
  console.log('Uninstall complete.');
  console.log('The service exists: ', svc.exists());
});

svc.uninstall();
