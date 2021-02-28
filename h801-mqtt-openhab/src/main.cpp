#include <MQTT.h>
#include <IotWebConf.h>
#include <IotWebConfUsing.h>
#include <ESP8266HTTPUpdateServer.h>
#include "gamma.h"
#include "hsb.h"

const char thingName[] = "h801";
const char wifiInitialApPassword[] = "0000000000";

// you can only set this to true if you connect to H801 using an (FDTI) adapter.
// if you start 801 normally with debug enabled it will NOT work
const bool debug = false;

#define STRING_LEN 128
#define NUMBER_LEN 32
#define CONFIG_VERSION "h801-1"
#define VERSION "v0.2"

#define topWhite1 "/white1"
#define topWhite2 "/white2"
#define topHsb "/hsb"
#define topStatus "/online"

// LED pin configurations
const unsigned int PIN_RGB_RED = 15;
const unsigned int PIN_RGB_GREEN = 13;
const unsigned int PIN_RGB_BLUE = 12;
const unsigned int PIN_WHITE1 = 14;
const unsigned int PIN_WHITE2 = 4;
// Internal status LED pin configurations
const unsigned int STATUS_PIN_LED_GREEN = 1;
const unsigned int STATUS_PIN_LED_RED = 5;

unsigned long BOOTTIME;

void handleRoot();
void mqttMessageReceived(String &topic, String &payload);
bool connectMqtt();
bool connectMqttOptions();
void wifiConnected();
void configSaved();
bool formValidator(iotwebconf::WebRequestWrapper *webRequestWrapper);

DNSServer dnsServer;
WebServer server(80);
ESP8266HTTPUpdateServer httpUpdater;
WiFiClient net;
MQTTClient mqttClient;

char mqttServerValue[STRING_LEN];
char mqttUserNameValue[STRING_LEN];
char mqttUserPasswordValue[STRING_LEN];
char mqttTopicValue[STRING_LEN];
char delayValueC[NUMBER_LEN];
unsigned long delayValue = 600;
unsigned long lastRunColors = 0L;
unsigned long redLEDMarker = 0L;

Hsb hsb;
unsigned int currentRed = 0;
unsigned int currentGreen = 0;
unsigned int currentBlue = 0;
unsigned int currentWhite1 = 0;
unsigned int currentWhite2 = 0;

unsigned int targetRed = 0;
unsigned int targetGreen = 0;
unsigned int targetBlue = 0;
unsigned int targetWhite1 = 0;
unsigned int targetWhite2 = 0;

IotWebConf iotWebConf(thingName, &dnsServer, &server, wifiInitialApPassword, CONFIG_VERSION);

IotWebConfParameterGroup mqttGroup = IotWebConfParameterGroup("MQTT configuration");
IotWebConfTextParameter mqttServerParam = IotWebConfTextParameter("MQTT server", "mqttServer", mqttServerValue, STRING_LEN);
IotWebConfTextParameter mqttUserNameParam = IotWebConfTextParameter("MQTT user", "mqttUser", mqttUserNameValue, STRING_LEN);
IotWebConfPasswordParameter mqttUserPasswordParam = IotWebConfPasswordParameter("MQTT password", "mqttPass", mqttUserPasswordValue, STRING_LEN);
IotWebConfTextParameter mqttTopicParam = IotWebConfTextParameter("MQTT topic", "mqttTopic", mqttTopicValue, STRING_LEN);
IotWebConfNumberParameter delayParam = IotWebConfNumberParameter("Delay", "delay", delayValueC, NUMBER_LEN);

bool needMqttConnect = false;
bool needReset = false;
int pinState = HIGH;
unsigned long lastReport = 0;
unsigned long lastMqttConnectionAttempt = 0;

void log(String message)
{
  if (debug)
  {
    Serial.println(message);
  }
}

void initLEDPins()
{
  pinMode(PIN_RGB_RED, OUTPUT);
  pinMode(PIN_RGB_GREEN, OUTPUT);
  pinMode(PIN_RGB_BLUE, OUTPUT);
  pinMode(PIN_WHITE1, OUTPUT);
  pinMode(PIN_WHITE2, OUTPUT);

  analogWrite(PIN_RGB_RED, 0);
  analogWrite(PIN_RGB_GREEN, 0);
  analogWrite(PIN_RGB_BLUE, 0);
  analogWrite(PIN_WHITE1, 0);
  analogWrite(PIN_WHITE2, 0);
}

void setColor(unsigned int r, unsigned int g, unsigned int b)
{
  char buffer[50];
  sprintf(buffer, "setting color to %d %d %d\n", r, g, b);
  log(buffer);

  targetRed = constrain(r, 0, 1023);
  targetGreen = constrain(g, 0, 1023);
  targetBlue = constrain(b, 0, 1023);
}

bool processColor(unsigned int target, unsigned int *current)
{
  bool update = false;
  if (*current != target)
  {
    update = true;
    if (*current < target)
    {
      (*current)++;
    }
    else if (*current > target)
    {
      (*current)--;
    }
  }
  return update;
}

void setup()
{
  if (debug)
  {
    Serial.begin(115200);
    Serial.set_tx(2);
  }

  BOOTTIME = millis();
  log("Starting up...");
  initLEDPins();

  mqttGroup.addItem(&mqttServerParam);
  mqttGroup.addItem(&mqttUserNameParam);
  mqttGroup.addItem(&mqttUserPasswordParam);
  mqttGroup.addItem(&mqttTopicParam);
  mqttGroup.addItem(&delayParam);

  iotWebConf.setStatusPin(STATUS_PIN_LED_GREEN);
  //iotWebConf.disableBlink();
  iotWebConf.setupUpdateServer(
      [](const char *updatePath) { httpUpdater.setup(&server, updatePath); },
      [](const char *userName, char *password) { httpUpdater.updateCredentials(userName, password); });
  iotWebConf.addParameterGroup(&mqttGroup);
  iotWebConf.setConfigSavedCallback(&configSaved);
  iotWebConf.setFormValidator(&formValidator);
  iotWebConf.setWifiConnectionCallback(&wifiConnected);

  bool validConfig = iotWebConf.init();
  if (!validConfig)
  {
    mqttServerValue[0] = '\0';
    mqttUserNameValue[0] = '\0';
    mqttUserPasswordValue[0] = '\0';
    mqttTopicValue[0] = '\0';
    delayValueC[0] = '\0';
  }

  delayValue = atoi(delayValueC);
  WiFi.hostname(iotWebConf.getThingName());

  server.on("/", handleRoot);
  server.on("/config", [] { iotWebConf.handleConfig(); });
  server.onNotFound([]() { iotWebConf.handleNotFound(); });

  mqttClient.begin(mqttServerValue, net);
  mqttClient.onMessage(mqttMessageReceived);

  pinMode(STATUS_PIN_LED_RED, OUTPUT);
  digitalWrite(STATUS_PIN_LED_RED, HIGH);

  log("Ready.");
}

void loop()
{
  iotWebConf.doLoop();
  mqttClient.loop();

  if (needMqttConnect)
  {
    if (connectMqtt())
    {
      needMqttConnect = false;
    }
  }
  else if ((iotWebConf.getState() == IOTWEBCONF_STATE_ONLINE) && (!mqttClient.connected()))
  {
    log("MQTT reconnect");
    connectMqtt();
  }

  if (needReset)
  {
    log("Rebooting after 1 second.");
    iotWebConf.delay(1000);
    ESP.restart();
  }

  unsigned long now = millis();
  if (60000 < now - lastReport)
  {
    lastReport = now;
    String topStat = String(mqttTopicValue) + topStatus;
    mqttClient.publish(topStat, String(BOOTTIME));
  }

  if ((micros() - lastRunColors) > delayValue)
  {
    lastRunColors = micros();

    if (processColor(targetRed, &currentRed))
    {
      analogWrite(PIN_RGB_RED, pgm_read_word(&gamma16[currentRed]));
    }

    if (processColor(targetGreen, &currentGreen))
    {
      analogWrite(PIN_RGB_GREEN, pgm_read_word(&gamma16[currentGreen]));
    }

    if (processColor(targetBlue, &currentBlue))
    {
      analogWrite(PIN_RGB_BLUE, pgm_read_word(&gamma16[currentBlue]));
    }

    if (processColor(targetWhite1, &currentWhite1))
    {
      analogWrite(PIN_WHITE1, pgm_read_word(&gamma16[currentWhite1]));
    }

    if (processColor(targetWhite2, &currentWhite2))
    {
      analogWrite(PIN_WHITE2, pgm_read_word(&gamma16[currentWhite2]));
    }
  }

  if ((millis() - redLEDMarker) < 100)
  {
    digitalWrite(STATUS_PIN_LED_RED, LOW);
  }
  else
  {
    digitalWrite(STATUS_PIN_LED_RED, HIGH);
  }
}

void handleRoot()
{
  if (iotWebConf.handleCaptivePortal())
  {
    return;
  }

  String s = "<!DOCTYPE html><html lang=\"en\"><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1, user-scalable=no\"/>";
  s += "<title>H801 ";
  s += iotWebConf.getThingName();
  s += "</title></head><body><h1>H801 ";
  s += iotWebConf.getThingName();
  s += "</h1>";
  s += "<ul>";
  s += "<li>Version: ";
  s += VERSION;
  s += "<li>MQTT server: ";
  s += mqttServerValue;
  s += "<li>MQTT topic: ";
  s += mqttTopicValue;
  s += "<li>Delay: ";
  s += delayValueC;
  s += "</ul>";
  s += "<a href='config'>config</a>";
  s += "</body></html>\n";
  server.send(200, "text/html", s);
}

void wifiConnected()
{
  needMqttConnect = true;
}

void configSaved()
{
  log("Configuration was updated.");
  needReset = true;
}

bool formValidator(iotwebconf::WebRequestWrapper *webRequestWrapper)
{
  log("Validating form.");
  bool valid = true;

  int l = webRequestWrapper->arg(mqttServerParam.getId()).length();
  if (l < 3)
  {
    mqttServerParam.errorMessage = "Please provide at least 3 characters!";
    valid = false;
  }

  return valid;
}

bool connectMqtt()
{
  unsigned long now = millis();
  if (5000 > now - lastMqttConnectionAttempt)
  {
    return false;
  }
  log("Connecting to MQTT server...");
  if (!connectMqttOptions())
  {
    lastMqttConnectionAttempt = now;
    return false;
  }
  log("Connected!");

  String topW1 = String(mqttTopicValue) + topWhite1;
  String topW2 = String(mqttTopicValue) + topWhite2;
  String topHSB = String(mqttTopicValue) + topHsb;

  mqttClient.subscribe(topW1);
  mqttClient.subscribe(topW2);
  mqttClient.subscribe(topHSB);
  return true;
}

bool connectMqttOptions()
{
  bool result;
  if (mqttUserPasswordValue[0] != '\0')
  {
    result = mqttClient.connect(iotWebConf.getThingName(), mqttUserNameValue, mqttUserPasswordValue);
  }
  else if (mqttUserNameValue[0] != '\0')
  {
    result = mqttClient.connect(iotWebConf.getThingName(), mqttUserNameValue);
  }
  else
  {
    result = mqttClient.connect(iotWebConf.getThingName());
  }
  return result;
}

String split(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++)
  {
    if (data.charAt(i) == separator || i == maxIndex)
    {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }

  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void mqttMessageReceived(String &topicRaw, String &payload)
{
  log("Incoming: " + topicRaw + " - " + payload);
  redLEDMarker = millis();

  String topW1 = String(mqttTopicValue) + topWhite1;
  String topW2 = String(mqttTopicValue) + topWhite2;
  String topHSB = String(mqttTopicValue) + topHsb;

  if (topicRaw.equals(topW1))
  {
    int i = payload.toInt();
    targetWhite1 = constrain(i * 10.23, 0, 1023);
  }
  if (topicRaw.equals(topW2))
  {
    int i = payload.toInt();
    targetWhite2 = constrain(i * 10.23, 0, 1023);
  }
  if (topicRaw.equals(topHSB))
  {
    String part01 = split(payload, ',', 0);
    String part02 = split(payload, ',', 1);
    String part03 = split(payload, ',', 2);

    log("Got HSB command:" + part01 + "," + part02 + "," + part03);
    unsigned int hue = part01.toInt();
    unsigned int saturation = part02.toInt();
    unsigned int brightness = part03.toInt();

    hsb.setHue(hue);
    hsb.setSaturation(saturation);
    hsb.setBrightness(brightness);
    unsigned int _red = 0;
    unsigned int _green = 0;
    unsigned int _blue = 0;
    if (hsb.toRgb(&_red, &_green, &_blue, 1023))
    {
      setColor(_red, _green, _blue);
    }
  }
}