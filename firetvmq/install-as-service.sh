user=`whoami`
homepath=`echo $HOME`
__service="
[Unit]
Description=FireTV MQTT
Wants=network-online.target

[Service]
Type=simple
User=$user
Group=input
WorkingDirectory=$homepath/mqtt-tools/firetvmq
ExecStart=$homepath/pythonenv/bin/python3 $homepath/mqtt-tools/firetvmq/firetvmq.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
"

echo "$__service" | sudo tee /lib/systemd/system/firetvmq.service

sudo systemctl daemon-reload
sudo systemctl enable firetvmq.service