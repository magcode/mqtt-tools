# Panasonic Viera MQTT interface

This is a simple MQTT interface for Panasonic Viera TV's.
Based on [node-panasonic-viera](https://www.npmjs.com/package/node-panasonic-viera)


# Install
This guide is for running on linux.
You need to [install NodeJS before](https://nodejs.org/en/download/package-manager).

```
cd ~
git clone git@github.com:magcode/mqtt-tools.git
cd mqtt-tools/vieramq
npm install
sudo node install.js
```

# Configuration
Change the file `mqtt-tools/vieramq/config/default.json`

# Start/stop
```
sudo service vieramqtt start
sudo service vieramqtt stop
```


# Uninstall
```
sudo service vieramqtt stop
cd ~/mqtt-tools/vieramq
sudo node uninstall.
```