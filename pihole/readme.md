# Pi-hole MQTT interface

This is a simple MQTT interface to control Pi-hole

# Install
This guide is for running on linux.
You need to [install NodeJS before](https://nodejs.org/en/download/package-manager).

```
cd ~
git clone git@github.com:magcode/mqtt-tools.git
cd mqtt-tools/pihole
npm install
sudo node install.js
```

# Configuration
Change the file `mqtt-tools/pihole/config/default.json`

# Start/stop
```
sudo service pihole-mqtt start
sudo service pihole-mqtt stop
```

# Sending en

This is an example how you can control Pi-hole with MQTT:

```
mosquitto_pub -h broker -t '<mytopic>/status/set' -m 'disabled'
mosquitto_pub -h broker -t '<mytopic>/status/set' -m 'enabled'
```

# Uninstall
```
sudo service pihole-mqtt stop
cd ~/mqtt-tools/pihole
sudo node uninstall.
```


# Openhab integration

Example things file
```
Thing mqtt:topic:pihole "Pihole" (mqtt:broker:mosquitto) {
    Channels:
        Type switch:enabled "Battery" [ commandTopic="home/pihole/status/set", stateTopic="home/pihole/status", on="enabled", off="disabled"]
}
```

Example items file
```
Switch switchPiHole "Pihole" { channel="mqtt:topic:pihole:enabled"}
```