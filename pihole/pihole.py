import asyncio
import os
import signal
import json
import logging
from pathlib import Path
from gmqtt import Client as MQTTClient
from pihole6api import PiHole6Client
from my_logging import setupLogging


STOP = asyncio.Event()


def on_connect(mqClient, flags, rc, properties):
    logger.info("MQTT Connected, subscribing to %s", config["MQTT_TOPIC"])
    mqClient.subscribe(config["MQTT_TOPIC"] + "/set", qos=0)


async def on_message(mqClient, topic, payload, qos, properties):
    payload_str = payload.decode()
    logger.info("Received message to turn %s", payload_str)
    if str(payload_str) == "ON":
        piHoleclient.dns_control.set_blocking_status(True)
    elif str(payload_str) == "OFF":
        piHoleclient.dns_control.set_blocking_status(False)


def on_disconnect(mqClient, packet, exc=None):
    logger.info("MQTT Disconnected")


def on_subscribe(mqClient, mid, qos, properties):
    logger.info("MQTT Subscribed ")


def ask_exit(*args):
    STOP.set()


def getConfig():
    configFile = Path(__file__).with_name("config.json")
    with configFile.open("r") as jsonfile:
        config = json.load(jsonfile)
        return config


async def main(broker_host, broker_port=1883, broker_username=None, broker_password=None):
    global mqClient
    mqClient = MQTTClient("pi-hole-mqtt-mqClient")

    mqClient.on_connect = on_connect
    mqClient.on_message = on_message
    mqClient.on_disconnect = on_disconnect
    mqClient.on_subscribe = on_subscribe
    if broker_username and broker_password:
        mqClient.set_auth_credentials(username=broker_username, password=broker_password)
    await mqClient.connect(host=broker_host, port=broker_port)
    await STOP.wait()
    await mqClient.disconnect()


async def periodic_task():
    global mqClient
    while True:
        await asyncio.sleep(60)
        if STOP.is_set():
            logger.info("STOP received, exiting periodic task")
            break
        try:
            status = piHoleclient.dns_control.get_blocking_status()
            sendStatus = "OFF"
            if status["blocking"] == "enabled":
                sendStatus = "ON"
            logger.debug("Pi-Hole status is currently: %s", sendStatus)
            if mqClient.is_connected:
                mqClient.publish(config["MQTT_TOPIC"], sendStatus, qos=0)
        except Exception as e:
            logger.error("Error getting Pi-Hole status: %s", e)


if __name__ == "__main__":
    config = getConfig()

    logger = logging.getLogger("piholemqtt")
    setupLogging(logger, config)
    logger.info("Started")

    piHoleclient = PiHole6Client(config["PIHOLE_URL"], config["PIHOLE_PASSWORD"])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    host = config["MQTT_HOST"]
    port = config["MQTT_PORT"]
    username = config["MQTT_USERNAME"]
    password = config["MQTT_PASSWORD"]

    token = os.environ.get("FLESPI_TOKEN")

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(asyncio.gather(main(host, port, username, password), periodic_task()))
