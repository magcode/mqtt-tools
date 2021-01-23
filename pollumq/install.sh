gcc pollucom.c -o pollucom
cd mqtt
npm install

home=`pwd`
user=`whoami`

__service="
[Unit]
Description=PolluComE MQTT
After=network.target
[Service]
ExecStart=node $home/mqtt-tools/pollumq/mqtt/pollumq.js
WorkingDirectory=$home/mqtt-tools/pollumq/mqtt
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

echo "Done. Start with 'sudo service pollumq start'."