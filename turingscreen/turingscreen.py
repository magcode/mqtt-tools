import sys
from pathlib import Path

turing_path = Path(__file__).resolve().parent / "vendor" / "turing-screen"
if str(turing_path) not in sys.path:
    sys.path.insert(0, str(turing_path))
import asyncio
import json
import random
import signal
from io import BytesIO
from urllib.request import urlopen

from gmqtt import Client as MQTTClient
from library.lcd.lcd_comm_rev_a import LcdCommRevA, Orientation
from library.lcd.lcd_simulated import LcdSimulated
from malog import setupLogging
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

listen_topic = "home/qdisplay"
PANEL_WIDTH = 320
PANEL_HEIGHT = 480
DISPLAY_WIDTH = PANEL_HEIGHT
DISPLAY_HEIGHT = PANEL_WIDTH
RESERVED_BOTTOM_HEIGHT = 40
ARTWORK_SIZE = DISPLAY_HEIGHT - RESERVED_BOTTOM_HEIGHT
TEXT_BACKGROUND = (60, 60, 60, 210)
TEXT_COLOR = (255, 255, 255, 255)
TEXT_STROKE_COLOR = (30, 30, 30, 255)

# sudo usbreset 1a86:5722


def on_connect(client, flags, rc, properties):
    logger.info("MQTT Connected")
    client.subscribe(config["TOPIC"] + "/#", qos=0)


def draw_track_label(draw, text, top, height, font_size):
    if not text:
        return

    draw.rectangle(
        (0, top, DISPLAY_WIDTH - 1, top + height - 1),
        fill=TEXT_BACKGROUND,
    )

    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", font_size)
    while font_size > 16:
        left, _, right, _ = draw.textbbox((0, 0), text, font=font)
        if right - left <= DISPLAY_WIDTH - 16:
            break
        font_size -= 2
        font = ImageFont.truetype("fonts/Roboto-Regular.ttf", font_size)

    draw.text(
        (DISPLAY_WIDTH // 2, top + height // 2),
        text,
        font=font,
        fill=TEXT_COLOR,
        anchor="mm",
        stroke_width=1,
        stroke_fill=TEXT_STROKE_COLOR,
    )


def draw_bluetooth_indicator(screen, btdevice):
    if not isinstance(btdevice, str) or not btdevice:
        return

    icon_x = 12
    icon_y = DISPLAY_HEIGHT - RESERVED_BOTTOM_HEIGHT + 7
    with Image.open(Path(__file__).with_name("bluetooth.png")) as icon_file:
        bluetooth_icon = icon_file.resize((24, 24), Image.Resampling.LANCZOS)
    screen.paste(bluetooth_icon, (icon_x, icon_y), bluetooth_icon)

    draw = ImageDraw.Draw(screen, "RGBA")
    draw.text(
        (icon_x + 26, DISPLAY_HEIGHT - RESERVED_BOTTOM_HEIGHT // 2),
        btdevice[:4],
        font=ImageFont.truetype("fonts/Roboto-Regular.ttf", 20),
        fill=TEXT_COLOR,
        anchor="lm",
        stroke_width=1,
        stroke_fill=TEXT_STROKE_COLOR,
    )


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
                musicstate = json_data.get("musicstate", "stopped")
                imageURL = json_data.get("imageURL", "")
                title = json_data.get("title", "")
                artist = json_data.get("artist", "")
                btdevice = json_data.get("btdevice", "")

                if musicstate == "playing":
                    playing_screen = Image.new(
                        "RGB",
                        (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                        (0, 0, 0),
                    )
                    if imageURL:
                        with urlopen(imageURL, timeout=10) as response:
                            image_data = response.read(10 * 1024 * 1024 + 1)
                        if len(image_data) > 10 * 1024 * 1024:
                            raise ValueError("Cover image exceeds the 10 MB limit")
                        with Image.open(BytesIO(image_data)) as cover_image:
                            cover_image = ImageEnhance.Brightness(cover_image.convert("RGB")).enhance(0.55)
                            cover_image = ImageOps.fit(
                                cover_image,
                                (ARTWORK_SIZE, ARTWORK_SIZE),
                                Image.Resampling.LANCZOS,
                            )
                            x = (DISPLAY_WIDTH - ARTWORK_SIZE) // 2
                            playing_screen.paste(cover_image, (x, 0))

                    draw = ImageDraw.Draw(playing_screen, "RGBA")
                    draw_track_label(draw, title, 65, 70, 80)
                    draw_track_label(draw, artist, 155, 50, 50)
                    if time:
                        draw.text(
                            (
                                DISPLAY_WIDTH // 2,
                                DISPLAY_HEIGHT - RESERVED_BOTTOM_HEIGHT // 2,
                            ),
                            time,
                            font=ImageFont.truetype(
                                "fonts/Matrixtype-lxMZX.ttf",
                                28,
                            ),
                            fill=TEXT_COLOR,
                            anchor="mm",
                            stroke_width=1,
                            stroke_fill=TEXT_STROKE_COLOR,
                        )
                    draw_bluetooth_indicator(playing_screen, btdevice)
                    lcd_comm.DisplayPILImage(playing_screen, x=0, y=0)

                else:
                    lcd_comm.DisplayPILImage(
                        Image.new(
                            "RGB",
                            (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                            (0, 0, 0),
                        ),
                        x=0,
                        y=0,
                    )
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
    client = MQTTClient("turing" + str(random.randint(0, 1000)))

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    await client.connect("broker.marko.lan")

    global lcd_comm
    if config["simulated"]:
        lcd_comm = LcdSimulated(
            display_width=PANEL_WIDTH,
            display_height=PANEL_HEIGHT,
        )
    else:
        lcd_comm = LcdCommRevA(
            logger=logger,
            com_port=config["COM_PORT"],
            display_width=PANEL_WIDTH,
            display_height=PANEL_HEIGHT,
        )

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
