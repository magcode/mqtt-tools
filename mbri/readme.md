# Auto brightness for Windows

This is a simple way to auto-control the brightness of your monitor attached to a Windows machine.
You need a light sensor which exposes the brightness value via MQTT.

It is using [Monitorian](https://github.com/emoacht/Monitorian).

# Install and compile
This guide is for running on linux.
You need to install [NodeJS](https://nodejs.org/en/download/package-manager) before.

```
cd ~
git clone git@github.com:magcode/mqtt-tools.git
cd mqtt-tools/mbri
npm install
./build.sh
```

# Running on Windows
Copy `mbri.exe` from the `build` subfolder to a folder in Windows.

Make a copy of `config.js` and place it beside `mbri.exe`.

Make changes to `config.js`.

```
config = {
	"broker": "mqtt://mybroker.host",
	"topic": "home/mysensor/brightness",
	"factor": 0.8,
	"monitorId": "DISPLAY\\LEN62\\5&23..."
}
```

You can get the value for `monitorId` by running the following command in Windows:

```
%LOCALAPPDATA%\Microsoft\WindowsApps\Monitorian.exe /get
```

`factor` allows you to apply a factor to the brightness value.

Now simply run `mbri.exe`. It will update the brightness each time the sensor sends a value.
