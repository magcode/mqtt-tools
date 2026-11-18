python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
git submodule add https://github.com/mathoudebine/turing-smart-screen-python.git vendor/turing-screen



user=`whoami`
homepath=`echo $HOME`
__service="
[Unit]
Description=Turing
Wants=network-online.target

[Service]
Type=simple
User=$user
Group=input
WorkingDirectory=$homepath/mqtt-tools/turingscreen
ExecStart=$homepath/mqtt-tools/turingscreen/venv/bin/python3 $homepath/mqtt-tools/turingscreen/turingscreen.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
"

echo "$__service" | sudo tee /etc/systemd/system/turing.service

sudo systemctl daemon-reload
sudo systemctl enable turing.service