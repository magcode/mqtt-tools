# RF and Bluetooth remote MQTT gateway

This tool allows you to use RF or Bluetooth remote controls as an universal input for your home automation.

Tested with 

["G20 remote control"](https://www.google.com/search?q=G20+remote+control)

["G20s pro remote control"](https://www.google.com/search?q=G20s+pro+remote+control)

["Xiaomi XMRM-010 Bluetooth"](https://www.google.com/search?q=xiaomi+XMRM-010)

You need a linux machine. It is verified working with Debian 10.

# Step 1: Download
You need to [install NodeJS >=v16 before](https://nodejs.org/en/download/package-manager).

```
cd ~
git clone git@github.com:magcode/mqtt-tools.git
cd mqtt-tools/remotekeys
```

# Step 2: Configure
You need to configure the tool in the file `config.yaml`.

```
default:
  mqtt:
    broker: mqtt://brokerIP       # your mqtt broker connection
                                  # you can also use 
                                  # mqtt://username:password@brokerIP
    topic: home/room/remote       # mqtt topic
  deviceNameFilter: Xiaomi        # Part of the device name as shows up under /proc/bus/input/devices
  customKeys:                     # see below
    582: KEY_MIC
    163: KEY_NEXTSONG
    164: KEY_PLAYPAUSE
    165: KEY_PREVIOUSSONG
    158: KEY_BACK
    172: KEY_HOMEPAGE
    240: KEY_NETFLIX
    207: KEY_PRIME
  autoRepeat:                     # see below
    - KEY_VOLUMEDOWN
    - KEY_VOLUMEUP
    - KEY_DOWN
    - KEY_UP
    - KEY_LEFT
    - KEY_RIGHT
  serviceuser: <me>               # user name for the linux service
  testmode: false                 # enable test mode
  logging:
    console: false                # enable console logging
    loki: true                    # enable Loki logging
    level: info                   # loglevel (info|debug)
    lokiUrl: http://my.loki:3100  # URL of loki server

```
## Custom keys
In case your remote sends unknown key id's you can map them in this section.

## Auto repeat
For some keys (e.g. `KEY_VOLUMEUP`) you may want auto-repeat. If you hold the key multiple MQTT messages will be triggered.

## deviceNameFilter
Provide a part of the device name as shown under /proc/bus/input/devices.
Examples: `Xiaomi` or `SG.Ltd`

## Get Bluetooth remote connected
You need to pair and connect your Bluetooth remote before you can use it with this tool.

Best is to use Linux' `bluetoothctl` tool.

## Hint for proxmox/lxc
You can run the G20 in an LXC container.

Use something like this in your lxc `*.conf` file:
```
lxc.cgroup.devices.allow: c 13:67 rwm
lxc.mount.entry: /dev/input/event3 dev/input/event10 none bind,optional,create=file
lxc.cgroup.devices.allow: c 13:69 rwm
lxc.mount.entry: /dev/input/event5 dev/input/event13 none bind,optional,create=file
lxc.cgroup.devices.allow: c 13:70 rwm
lxc.mount.entry: /dev/input/event6 dev/input/event14 none bind,optional,create=file
```

You may need to change permissions in the container:
```
sudo chmod 666 /dev/input/event10
sudo chmod 666 /dev/input/event13
sudo chmod 666 /dev/input/event14
```

Bluetooth remotes cannot run in LXC, they need a dedicated VM.

# Step 3: Install
```
npm install
sudo node install.js
```

# Start/stop
```
sudo service remotekeys start
sudo service remotekeys stop
```

# Uninstall
```
sudo service remotekeys stop
cd ~/mqtt-tools/remotekeys
sudo node uninstall.
```

# Using it

## Normal key press
If you press a button you will find the following MQTT message triggered:

```
home/room/remote/KEY_MUTE trigger
```
## Long press with "autoRepeat"
If you keep pressing one of the supported "autoRepeat" buttons you will trigger multiple MQTT messages

```
home/room/remote/KEY_VOLUMEUP trigger
home/room/remote/KEY_VOLUMEUP trigger
home/room/remote/KEY_VOLUMEUP trigger
```

## Long press
Long pressing (400ms) a button will trigger the following MQTT message:
```
home/room/remote/KEY_MUTE-LONG trigger
```

# Notes
* You cannot use the mouse feature of the G20 remotes with this tool.
* The "mic" button is not useable.
* In case the G20 remote does not send keys, press the "mouse" button once.

You should disable the power key handling in Linux. Otherwise your system may shut down if you press the "Power" button on the remote.

For Debian the following must be set in `/etc/systemd/logind.conf`

```
HandlePowerKey=ignore
HandleSuspendKey=ignore
```

# Openhab integration

Example things file
```
Thing mqtt:topic:RoomRemote "Room Remote" (mqtt:broker:mosquitto) {
    Channels:
        Type string : KEY_UP "KEY_UP" [ stateTopic="home/room/remote/KEY_UP", trigger=true]
        Type string : KEY_DOWN "KEY_DOWN" [ stateTopic="home/room/remote/KEY_DOWN", trigger=true]
        Type string : KEY_ENTER "KEY_ENTER" [ stateTopic="home/room/remote/KEY_ENTER", trigger=true]
        Type string : KEY_LEFT "KEY_LEFT" [ stateTopic="home/room/remote/KEY_LEFT", trigger=true]
        Type string : KEY_RIGHT "KEY_RIGHT" [ stateTopic="home/room/remote/KEY_RIGHT", trigger=true]
        Type string : KEY_HOMEPAGE "KEY_HOMEPAGE" [ stateTopic="home/room/remote/KEY_HOMEPAGE", trigger=true]
        Type string : KEY_VOLUMEUP "KEY_VOLUMEUP" [ stateTopic="home/room/remote/KEY_VOLUMEUP", trigger=true]
        Type string : KEY_VOLUMEDOWN "KEY_VOLUMEDOWN" [ stateTopic="home/room/remote/KEY_VOLUMEDOWN", trigger=true]
        Type string : KEY_BACK "KEY_BACK" [ stateTopic="home/room/remote/KEY_BACK", trigger=true]
        Type string : KEY_PREVIOUSSONG "KEY_PREVIOUSSONG" [ stateTopic="home/room/remote/KEY_PREVIOUSSONG", trigger=true]
        Type string : KEY_NEXTSONG "KEY_NEXTSONG" [ stateTopic="home/room/remote/KEY_NEXTSONG", trigger=true]
        Type string : KEY_POWER "KEY_POWER" [ stateTopic="home/room/remote/KEY_POWER", trigger=true]
        Type string : KEY_PLAYPAUSE "KEY_PLAYPAUSE" [ stateTopic="home/room/remote/KEY_PLAYPAUSE", trigger=true]
        Type string : KEY_MUTE "KEY_MUTE" [ stateTopic="home/room/remote/KEY_MUTE", trigger=true]
        Type string : KEY_MUTE-LONG "KEY_MUTE-LONG" [ stateTopic="home/room/remote/KEY_MUTE-LONG", trigger=true]
        Type string : KEY_BACKSPACE "KEY_BACKSPACE" [ stateTopic="home/room/remote/KEY_BACKSPACE", trigger=true]
        Type string : KEY_COMPOSE "KEY_COMPOSE" [ stateTopic="home/room/remote/KEY_COMPOSE", trigger=true]        
}
```

Example rules file
```
rule "KEY_BACK"
    when
        Channel "mqtt:topic:RoomRemote:KEY_BACK" triggered
    then
        // what you want
end
```
