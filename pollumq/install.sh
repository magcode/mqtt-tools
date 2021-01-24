gcc pollucom.c -o pollucom
cd mqtt
npm install

home=`pwd`
user=`whoami`

__service="
[Unit]
Description=Pollucom MQTT Gateway
After=network.target
[Service]
ExecStart=node $home/pollumq.js
WorkingDirectory=$home
SyslogIdentifier=pollumq
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$user
[Install]
WantedBy=multi-user.target
"

echo "$__service" | sudo tee /etc/systemd/system/pollumq.service
sudo systemctl daemon-reload
sudo systemctl enable pollumq.service

echo "Done. Configure in config/default.json and start with 'sudo service pollumq start' afterwards."