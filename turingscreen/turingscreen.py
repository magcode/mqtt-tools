from gmqtt import Client as MQTTClient
from library.lcd.lcd_comm_rev_a import LcdCommRevA, Orientation
from library.lcd.lcd_simulated import LcdSimulated
from malog import setupLogging
from pathlib import Path
import asyncio
import signal
import time
import json
from typing import Coroutine
from datetime import datetime

background = "backgrounds/black.png"
listen_topic = "home/qdisplay"

# sudo usbreset 1a86:5722

def on_connect(client, flags, rc, properties):
    logger.info("MQTT Connected")
    client.subscribe(listen_topic + "/#", qos=0)


async def on_message(client, topic, payload, qos, properties):
    global lcd_comm
    try:
        decoded_payload = payload.decode("utf-8")
        if topic == listen_topic + "/status":
            try:
                logger.debug(f"Received status update: {decoded_payload}")
                # Parse the payload as JSON
                json_data = json.loads(decoded_payload)
                time = json_data.get("time", "")
                temp1 = json_data.get("temp1", "")
                temp2 = json_data.get("temp2", "")
                col = json_data.get("col", "#FFFFFF")
                if col and col.startswith("#") and len(col) == 7:
                    try:
                        r = int(col[1:3], 16)
                        g = int(col[3:5], 16)
                        b = int(col[5:7], 16)
                        font_color = (r, g, b)
                    except ValueError:
                        logger.warning(f"Invalid color format: {col}")
                lcd_comm.DisplayText(
                    time,
                    1,
                    1,
                    font="fonts/Matrixtype-lxMZX.ttf",
                    font_size=140,
                    font_color=font_color,
                    background_color=(0, 0, 0),
                )

                lcd_comm.DisplayText(
                    temp1,
                    1,
                    235,
                    font="fonts/Roboto-Regular.ttf",
                    font_size=90,
                    font_color=font_color,
                    background_color=(0, 0, 0),
                )

                lcd_comm.DisplayText(
                    temp2,
                    290,
                    235,
                    font="fonts/Roboto-Regular.ttf",
                    font_size=90,
                    font_color=font_color,
                    background_color=(0, 0, 0),
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")

        if topic == listen_topic + "/bri":
            try:
                brightness = int(decoded_payload)
                # Ensure brightness is within valid range (0-100)
                brightness = max(0, min(brightness, 100))
                lcd_comm.SetBrightness(level=brightness)
            except ValueError:
                print(f"Invalid brightness value: {decoded_payload}")
        if topic == listen_topic + "/power":
            if decoded_payload == "OFF":
                lcd_comm.ScreenOff()
            elif decoded_payload == "ON":
                lcd_comm.ScreenOn()

    except Exception as e:
        print(f"Error decoding payload: {e}")
    # await process()


def on_disconnect(client, packet, exc=None):
    logger.info("MQTT Disconnected")


def on_subscribe(client, mid, qos, properties):
    logger.info("MQTT SUBSCRIBED")


async def process():
    await asyncio.sleep(10)
    print("Processing Done")


async def main():
    logger.info("Application started. Press Ctrl+C to exit.")

    # Create an asyncio.Event that will be used to signal shutdown.
    shutdown_event = asyncio.Event()

    # The function that will be called when a signal is received.
    # It simply sets the event.
    def signal_handler(*args):
        logger.info("Shutdown signal received. Exiting gracefully...")
        shutdown_event.set()

    # Register the signal handler for SIGINT (Ctrl+C).
    signal.signal(signal.SIGINT, signal_handler)

    # You can start other background tasks here
    # E.g., task = asyncio.create_task(do_work())
    client = MQTTClient("turing")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    await client.connect("broker.marko.lan")

    COM_PORT = "/dev/ttyUSB0"
    WIDTH, HEIGHT = 320, 480
    global lcd_comm
    if config["simulated"]:
        lcd_comm = LcdSimulated(logger=logger, display_width=WIDTH, display_height=HEIGHT)
    else:
        lcd_comm = LcdCommRevA(logger=logger, com_port=COM_PORT, display_width=WIDTH, display_height=HEIGHT)

    # Reset screen in case it was in an unstable state (screen is also cleared)
    lcd_comm.Reset()

    # Send initialization commands
    lcd_comm.InitializeComm()

    # Set brightness in % (warning: revision A display can get hot at high brightness! Keep value at 50% max for rev. A)
    lcd_comm.SetBrightness(level=50)

    # Set backplate RGB LED color (for supported HW only)
    lcd_comm.SetBackplateLedColor(led_color=(0, 0, 0))

    # Set orientation (screen starts in Portrait)
    lcd_comm.SetOrientation(orientation=Orientation.REVERSE_LANDSCAPE)
    # Wait here until the shutdown_event is set by the signal handler.

    lcd_comm.DisplayBitmap(background)

    await shutdown_event.wait()
    await lcd_comm.closeSerial()
    await client.disconnect()

    # Perform cleanup here if needed
    # E.g., task.cancel()
    # await task

    print("Application has shut down.")


if __name__ == "__main__":
    try:
        configFile = Path(__file__).with_name("config.json")
        with configFile.open("r") as jsonfile:
            config = json.load(jsonfile)
        logger = setupLogging(config)

        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # The main() function already handles the graceful shutdown.
        # This block can be left empty.
        pass
