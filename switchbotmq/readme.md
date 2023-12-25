# Switchbot Temperature Sensor BLE MQTT gateway

This tool reads Switchbot Temperature Sensor data and publishes it via MQTT.

# Step 1: Download
You need to [install NodeJS >=v16 before](https://nodejs.org/en/download/package-manager).

```
cd ~
git clone git@github.com:magcode/mqtt-tools.git
cd mqtt-tools/switchbotmq
```

# Step 2: Configure
You need to configure the tool in the file `config/default.json`

Example file:
```
{
  "name": "switchbotmq",
  "mqtt": {
    "broker": "tcp://broker",
    "port": 1883,
    "user": "",
    "password": "",
    "topic": "home/temperaturessb"
  },
  "logging": {
    "console": {
      "enabled": false,
      "level": "debug"
    },
    "file": {
      "enabled": false,
      "level": "debug"
    },
    "syslog": {
      "enabled": false,
      "level": "debug",
      "host": "localhost",
      "port": 50514,
      "protocol": "udp4",
      "type": "5424"
    },
    "loki": {
      "enabled": true,
      "level": "info",
      "url": "http://loggingserver:3100",
      "labels": {
        "monitor": "grafana"
      }
    }
  }
}
```

# Step 4: Run
The process will run, wait for sensor values and exit.

```
/usr/bin/node switchbotmqs.js
```

Example for your crontab file
```
*/5 * * * * cd /home/me/mqtt-tools/switchbotmq && /usr/bin/node /home/me/mqtt-tools/switchbotmq/switchbotmqs.js
```