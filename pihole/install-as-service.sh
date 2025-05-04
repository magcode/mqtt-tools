user=`whoami`
homepath=`echo $HOME`
__service="
[Unit]
Description=Pi-hole MQTT
Wants=network-online.target

[Service]
Type=simple
User=$user
Group=input
WorkingDirectory=$homepath/mqtt-tools/pihole
ExecStart=$homepath/pythonenv/bin/python3 $homepath/mqtt-tools/pihole/pihole.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
"

echo "$__service" | sudo tee /etc/systemd/system/piholemqtt.service

sudo systemctl daemon-reload
sudo systemctl enable piholemqtt.service