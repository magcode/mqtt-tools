# Monitor Control

This is simple tool to control the brightness of your monitor(s) attached to a Windows machine based on a MQTT-connected light sensor.

# Configuration
Create a copy of `configuration-sample.json` and call it `configuration.json`.
Adapt the configuration values as needed.

Under `monitors` you can define specific parameters for the monitors you own.
The names of the monitors will be printed to the console when you start the tool with `python.exe C:\<your path>\moco.py`.

The tool expects that the light sensor data is posted to a certain MQTT topic. You can define the JSON selector in the configuration.

`factor`and `offset` allows to fine tune the conversion from your light sensor value to a value between 0 and 100 for brightness control.
```
factor ... will apply a factor to the incoming value
offset ... allows to substract / add a fixed value
```

# Running on Windows
First install Python (tested with 3.12.8).

Then get the code and dependencies

```
git clone https://github.com/magcode/mqtt-tools.git
cd mqtt-tools\moco
pip install -r requirements.txt
```

Now create a shortcut
```
pythonw.exe C:\<your path>\moco.py
```

You will find a systray icon which provides some additional information when hovering.