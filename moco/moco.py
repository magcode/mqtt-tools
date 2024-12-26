import asyncio
import aiomqtt
import os
import sys
import logging
import json
import screen_brightness_control as sbc

from infi.systray import SysTrayIcon

quit_selected = False


def get_config():
    root = os.path.dirname(os.path.abspath(__file__))
    configPath = root + "/configuration.json"
    with open(configPath, "r") as file:
        return json.loads(file.read())


class logginghandler(logging.StreamHandler):
    colors = {
        logging.DEBUG: "\033[37m",
        logging.INFO: "\033[36m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[101m",
    }
    reset = "\033[0m"
    fmtr = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")

    def format(self, record):
        color = self.colors[record.levelno]
        log = self.fmtr.format(record)
        reset = self.reset
        return color + log + reset


def quit(tray):
    logger.info("QUIT: Quit called")
    global quit_selected
    quit_selected = True
    os._exit(0)


async def main(config):
    logger.info("moco Started")
    icon_base_path = os.path.dirname(__file__) + "/icons"
    icon_path_g = os.path.join(icon_base_path, "grey.ico")
    icon_path_y = os.path.join(icon_base_path, "yellow.ico")
    icon_path_gl = os.path.join(icon_base_path, "glow.ico")
    systray = SysTrayIcon(icon_path_g, "Monitor Control", on_quit=quit)
    systray.start()

    client = aiomqtt.Client(hostname=config["mqtt"]["brokerHost"], port=config["mqtt"]["brokerPort"])

    reconnect_interval = 20  # Seconds
    while not quit_selected:
        try:
            async with client:
                await client.subscribe(config["mqtt"]["topic"])
                logger.info(f"Subscribed to {config['mqtt']['topic']}")
                systray.update(icon=icon_path_y)
                async for message in client.messages:
                    systray.update(icon=icon_path_gl)
                    jsono = json.loads(message.payload.decode())
                    mes = ""
                    for monitor in sbc.list_monitors():
                        factor, offset = getParametersForMonitor(config, monitor)
                        val = int(jsono[config["sensor"]["jsonPath"]])
                        val = round(val * factor)
                        val = val + offset

                        if val > 100:
                            val = 100

                        if val < 1:
                            val = 1

                        sbc.set_brightness(val, display=monitor)
                        mes = mes + f"{monitor}: {str(val)}%" + "\n"
                    logger.info(mes)
                    systray.update(hover_text=mes)
                    await asyncio.sleep(0.1)
                    systray.update(icon=icon_path_y)
        except aiomqtt.MqttError:
            logger.info(f"Connection lost; Reconnecting in {reconnect_interval} seconds ...")
            systray.update(icon=icon_path_g, hover_text="Disconnected")
            await asyncio.sleep(reconnect_interval)
        except Exception as ex:
            logger.warning(f"MAIN(): Exception {ex.__class__.__name__}. PC maybe woke up from sleep {str(ex)}.")

    systray.shutdown()
    sys.exit(0)


def getParametersForMonitor(configuration, monitor_name):
    for monitor in configuration["monitors"]:
        if monitor_name == monitor:
            return (configuration["monitors"][monitor]["factor"], configuration["monitors"][monitor]["offset"])
    return (configuration["monitors"]["default"]["factor"], configuration["monitors"]["default"]["offset"])


logging.basicConfig(level=logging.INFO, handlers=[logginghandler()])
logger = logging.getLogger(__name__)
logging.getLogger("screen_brightness_control.windows").setLevel(logging.ERROR)

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy

    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
config = get_config()
asyncio.run(main(config))
