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
```

Now configure the file `mqtt-tools/vieramq/config/default.json`

```
npm install
sudo node install.js
```

# Start/stop
```
sudo service vieramqtt start
sudo service vieramqtt stop
```

# Sending commands

This is an example how you can control the Viera TV with MQTT:

```
mosquitto_pub -h broker -t '<mytopic>/command/set' -m 'num_0'
```
You can get the command names from [node-panasonic-viera](https://github.com/jens-maus/node-panasonic-viera/blob/main/viera.js#L480).

App commands are supported via

```
mosquitto_pub -h broker -t '<mytopic>/appcommand/set' -m 'num_0'
```

# Uninstall
```
sudo service vieramqtt stop
cd ~/mqtt-tools/vieramq
sudo node uninstall.
```


# Openhab integration

Example things file
```
Thing mqtt:topic:panasonic "Panasonic TV" (mqtt:broker:mosquitto) {
    Channels:
        Type string : command "Panasonic TV Command" [ commandTopic="home/tv/command/set"]        
}
```

Example items file
```
String tvCommand "Panasonic TV command"  {channel="mqtt:topic:panasonic:command"}
```

Example rules file
```
rule "example"
    when
        Channel "<whatever>" triggered
    then        
        tvCommand.sendCommand("home")        
end
```