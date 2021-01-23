# PolluComE MQTT
This project extends the great work of [Joe Seyfried](https://github.com/JoeSey/PolluComE).
It provide an MQTT interface for easy integration into your home automation.

# Installing
This guide is for running on a Raspberry Pi.
Make sure you have gcc and NodeJS installed.

```
cd ~
git clone git@github.com:magcode/mqtt-tools.git
cd mqtt-tools/pollumq
./install.sh
```

# Configuration

## before you start it the first time!
**Press the button** on your PolluCom E unit. After a short press, the unit will respond to IR signals for one hour.


# Uninstall
sudo service pollumq stop
cd ~/mqtt-tools/pollumq
sudo node uninstall.sh