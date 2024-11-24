import asyncio
import signal
import json
from pathlib import Path
import aiomqtt
import logging
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from my_logging import setupLogging


async def connectFireTv():
    global fireTV
    logger.info("Connect attempt")
    # Load the public and private keys
    adbkey = config["ADB_KEY_PATH"]
    with open(adbkey) as f:
        priv = f.read()
    with open(adbkey + ".pub") as f:
        pub = f.read()
    signer = PythonRSASigner(pub, priv)

    # Connect
    try:
        fireTV = AdbDeviceTcp(config["FIRETV_ADDRESS"], config["FIRETV_PORT"], default_transport_timeout_s=2)
        fireTV.connect(rsa_keys=[signer], auth_timeout_s=0.1)
        # Send a test shell command
        response1 = fireTV.shell("echo 'Connect OK'")
        logger.info(response1)
    except Exception as e:
        logger.info(f"Connection failed: {e}")


async def sendStatus(online, nowPlaying=None, app=None):
    if mqttClient:
        if nowPlaying:
            await mqttClient.publish(topic + "/status", payload=nowPlaying)
        if app:
            await mqttClient.publish(topic + "/app", payload=app)
        if online:
            logger.debug("Connection Watcher OK")
            await mqttClient.publish(topic + "/status", payload=nowPlaying)
        else:
            logger.error("Connection Watcher Not connected")
            await mqttClient.publish(topic + "/status", payload="offline")


async def watchConnection():
    global fireTV
    while True:
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            logger.debug("Connection Watcher shutdown")

        if fireTV and fireTV.available:
            try:
                playing = fireTV.shell(
                    "dumpsys media_session | grep -A 7 active=true | grep -A 4 state=PLAYING | grep metadata"
                )
                app = fireTV.shell(
                    "dumpsys activity top | grep ACTIVITY | tail -n 1 | awk '{print $2}' | cut -d '/' -f1 | cut -d ' ' -f4"
                )
                await sendStatus(online=True, nowPlaying=playing, app=app)
            except Exception as e:
                logger.info(f"Connection error: {e}")
                await connectFireTv()
            except aiomqtt.exceptions.MqttCodeError as err:
                logger.info("mqtt error: " + str(err))
        else:
            logger.info("connection not available")
            await connectFireTv()


async def setupMQTT(host, port, user, password):
    global mqttClient
    try:
        async with aiomqtt.Client(port=port, password=password, username=user, hostname=host) as client:
            mqttClient = client
            startTopic = topic + "/command/startapp"
            await client.subscribe(startTopic)
            async for message in client.messages:
                payload = message.payload.decode()
                logger.debug(f"received {payload} on {message.topic}")
                if message.topic.matches(startTopic) and payload == "disney":
                    fireTV.shell(
                        "am start -a android.intent.action.VIEW -n com.disney.disneyplus/com.bamtechmedia.dominguez.main.MainActivity"
                    )
                if message.topic.matches(startTopic) and payload == "prime":
                    fireTV.shell(
                        "am start com.amazon.avod.thirdpartyclient/com.amazon.avod.client.activity.HomeScreenActivity"
                    )

    except asyncio.CancelledError:
        logger.info("mqtt task cancelled")

    except Exception as e:
        logger.error("mqtt" + str(e))
        await ask_exit(signal.SIGINT)


async def ask_exit(signame):
    logger.info("got signal %s: exit" % signame)
    await sendStatus(online=False, nowPlaying=None, app=None)

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.sleep(1)
    loop.stop()
    logger.info("Exit")


def getConfig():
    configFile = Path(__file__).with_name("config.json")
    with configFile.open("r") as jsonfile:
        config = json.load(jsonfile)
        return config


mqttClient = None
fireTV = None
config = getConfig()

logger = logging.getLogger("firetv")
setupLogging(logger, config)
logger.info("Started")

topic = config["MQTT_TOPIC"]
stack = []
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
for signame in ("SIGINT", "SIGTERM"):
    loop.add_signal_handler(getattr(signal, signame), lambda signame=signame: asyncio.create_task(ask_exit(signame)))

loop.create_task(
    setupMQTT(
        host=config["MQTT_HOST"],
        port=config["MQTT_PORT"],
        user=config["MQTT_USERNAME"],
        password=config["MQTT_PASSWORD"],
    ),
    name="mqtt",
)
loop.create_task(connectFireTv(), name="connect")
loop.create_task(watchConnection(), name="watch")
loop.run_forever()
