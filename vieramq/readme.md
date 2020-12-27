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

# Sending commands

This is an example how you can control the Viera TV with MQTT:

```
mosquitto_pub -h broker -t '<mytopic>' -m 'num_0'
```
You can get the command names from [node-panasonic-viera](https://github.com/jens-maus/node-panasonic-viera/blob/main/viera.js#L480).


# Uninstall
```
sudo service vieramqtt stop
cd ~/mqtt-tools/vieramq
sudo node uninstall.
```