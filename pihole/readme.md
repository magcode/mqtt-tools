# Pi-hole 6 MQTT interface

This is a simple MQTT interface to control Pi-hole

# Install
This guide is for running on linux.
Check below code and file `install-as-service.sh` and adapt to your needs.

```
cd ~
source ~/pythonenv/bin/activate
git clone git@github.com:magcode/mqtt-tools.git
cd mqtt-tools/pihole
pip install -r /path/to/requirements.txt
sudo install-as-service.sh

```

# Configuration
Create a copy `config.json` from file `mqtt-tools/pihole/config-example.json` and make your changes.

# Start/stop
```
sudo service piholemqtt start
sudo service piholemqtt stop
```

# Control Pi-hole

This is an example how you can control Pi-hole with MQTT:

```
mosquitto_pub -h broker -t '<mytopic>/status/set' -m 'ON'
mosquitto_pub -h broker -t '<mytopic>/status/set' -m 'OFF'
```

# Uninstall
```
sudo service piholemqtt stop
sudo systemctl disable piholemqtt.service
sudo systemctl daemon-reload
sudo rm /etc/systemd/system/piholemqtt.service
```


# Openhab integration

Example things file
```
Thing mqtt:topic:pihole "Pihole" (mqtt:broker:mosquitto) {
    Channels:
        Type switch:enabled "Pihole enabled" [ commandTopic="home/pihole/status/set", stateTopic="home/pihole/status"]
}
```

Example items file
```
Switch switchPiHole "Pihole Blocking" {channel="mqtt:topic:pihole:enabled"}
```
