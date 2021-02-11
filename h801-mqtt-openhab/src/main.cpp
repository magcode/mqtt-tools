#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <DNSServer.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <Secrets.h>
#include "gamma.h"
#include "hsb.h"

const int CHIP_ID = ESP.getChipId();
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

#define concat(first, second) first second
#define white1 "/white1"
#define white2 "/white2"
#define thsb "/hsb"
#define speed "/speed"

const char *topicWhite1 = concat(mqttTopic, white1);
const char *topicWhite2 = concat(mqttTopic, white2);
const char *topicHsb = concat(mqttTopic, thsb);
const char *topicSpeed = concat(mqttTopic, speed);

unsigned long lastRunColors = 0L;
// speed = 0 - 100: 0 -> 50000µs delay, 100 -> 100µs delay
unsigned long delayValue = 600;

// pin configurations
const unsigned int PIN_RGB_RED = 15;
const unsigned int PIN_RGB_GREEN = 13;
const unsigned int PIN_RGB_BLUE = 12;
const unsigned int PIN_WHITE1 = 14;
const unsigned int PIN_WHITE2 = 4;

const unsigned int PIN_LED_GREEN = 1;
const unsigned int PIN_LED_RED = 5;

Hsb hsb;
unsigned int currentRed = 1023;
unsigned int currentGreen = 1023;
unsigned int currentBlue = 1023;
unsigned int currentWhite1 = 1023;
unsigned int currentWhite2 = 1023;

unsigned int targetRed = 1023;
unsigned int targetGreen = 1023;
unsigned int targetBlue = 1023;
unsigned int targetWhite1 = 1023;
unsigned int targetWhite2 = 1023;

void setColor(unsigned int r, unsigned int g, unsigned int b)
{
	//Serial.printf("setting color to %d %d %d\n", r, g, b);
	targetRed = constrain(r, 0, 1023);
	targetGreen = constrain(g, 0, 1023);
	targetBlue = constrain(b, 0, 1023);
}

String split(String s, char delimiter, int index)
{
	int count = 0;
	int fromIndex = 0;
	int toIndex = -1;
	while (true)
	{
		fromIndex = toIndex + 1;
		toIndex = s.indexOf(delimiter, fromIndex);
		if (count == index)
		{
			if (toIndex == -1)
			{
				toIndex = s.length();
			}
			return s.substring(fromIndex, toIndex);
		}
		if (toIndex == -1)
		{
			break;
		}
		else
		{
			count++;
		}
	}
	return "";
}

void mqttCallback(char *topicRaw, byte *payloadRaw, unsigned int length)
{
	if (strcmp(topicRaw, topicWhite1) == 0)
	{
		payloadRaw[length] = '\0';
		char *cstring = (char *)payloadRaw;
		int i = atoi(cstring);
		targetWhite1 = constrain(i * 10.23, 0, 1023);
	}
	if (strcmp(topicRaw, topicWhite2) == 0)
	{
		payloadRaw[length] = '\0';
		char *cstring = (char *)payloadRaw;
		int i = atoi(cstring);
		targetWhite2 = constrain(i * 10.23, 0, 1023);
	}
	if (strcmp(topicRaw, topicHsb) == 0)
	{
		char payload[length + 1];
		memset(payload, '\0', length + 1);
		memcpy(payload, payloadRaw, length);
		String payloadString(payload);
		payloadString.trim();

		unsigned int hue = split(payloadString, ',', 0).toInt();
		unsigned int saturation = split(payloadString, ',', 1).toInt();
		unsigned int brightness = split(payloadString, ',', 2).toInt();
		//Serial.printf("hsb: %d %d %d\n", hue, saturation, brightness);
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

void subscribeTopic(String topic)
{
	//Serial.printf("subscribing to topic: %s\n", topic.c_str());
	mqttClient.subscribe(topic.c_str());
}

void startMqtt()
{
	while (!mqttClient.connected())
	{
		String clientId = "h801-";
		clientId += host;
		clientId += String(random(0xffff), HEX);
		//Serial.println("MQTT connecting ...");
		delay(1000);
		if (mqttClient.connect(clientId.c_str()))
		{
			//Serial.println("MQTT connected");
			delay(1000);
			subscribeTopic(topicWhite1);
			subscribeTopic(topicWhite2);
			subscribeTopic(topicHsb);
			subscribeTopic(topicSpeed);
			//Serial.println("MQTT subscribed");
		}
		else
		{
			//Serial.println("MQTT failed, retrying...");
			delay(5000);
		}
	}
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

void startWifi(void)
{
	WiFi.begin(wifiAP, wifiPassword);
	//Serial.println("Wifi connecting ...");
	while (WiFi.status() != WL_CONNECTED)
	{
		delay(500);
		//Serial.print(".");
	}
	//Serial.println("Wifi connected");
}

void setup(void)
{
	//Serial.begin(57600);
	//Serial.set_tx(2);
	WiFi.hostname(host);
	//Serial.println(CHIP_ID + " starting");

	mqttClient.setServer(mqtt_server, mqtt_port);
	mqttClient.setCallback(mqttCallback);

	startWifi();
	delay(1000);

	//Serial.println(F("setting up ports"));
	pinMode(PIN_RGB_RED, OUTPUT);
	pinMode(PIN_RGB_GREEN, OUTPUT);
	pinMode(PIN_RGB_BLUE, OUTPUT);
	pinMode(PIN_WHITE1, OUTPUT);
	pinMode(PIN_WHITE2, OUTPUT);

	//pinMode(PIN_LED_RED, OUTPUT);
	//digitalWrite(PIN_LED_RED, HIGH);

	analogWrite(PIN_RGB_RED, 0);
	analogWrite(PIN_RGB_GREEN, 0);
	analogWrite(PIN_RGB_BLUE, 0);
	analogWrite(PIN_WHITE1, 0);
	analogWrite(PIN_WHITE2, 0);

	analogWrite(PIN_RGB_RED, 1023);
	delay(100);
	analogWrite(PIN_RGB_RED, 0);
	analogWrite(PIN_RGB_GREEN, 1023);
	delay(100);
	analogWrite(PIN_RGB_GREEN, 0);
	analogWrite(PIN_RGB_BLUE, 1023);
	delay(100);
	analogWrite(PIN_RGB_BLUE, 0);
	analogWrite(PIN_WHITE1, 1023);
	delay(100);
	analogWrite(PIN_WHITE1, 0);
	analogWrite(PIN_WHITE2, 1023);

	analogWrite(PIN_WHITE1, 1023);
	analogWrite(PIN_RGB_RED, 1023);
	analogWrite(PIN_RGB_GREEN, 1023);
	analogWrite(PIN_RGB_BLUE, 1023);

	setColor(0, 0, 0);
	targetWhite1 = 0;
	targetWhite2 = 0;	
}

void loop(void)
{
	if (!mqttClient.connected())
	{
		startMqtt();
	}
	mqttClient.loop();

	if ((micros() - lastRunColors) > delayValue)
	{
		lastRunColors = micros();

		if (processColor(targetRed, &currentRed))
		{
			//Serial.printf("updating red %d\n", currentRed);
			analogWrite(PIN_RGB_RED, pgm_read_word(&gamma16[currentRed]));
		}

		if (processColor(targetGreen, &currentGreen))
		{
			//Serial.printf("updating green %d\n", currentGreen);
			analogWrite(PIN_RGB_GREEN, pgm_read_word(&gamma16[currentGreen]));
		}

		if (processColor(targetBlue, &currentBlue))
		{
			//Serial.printf("updating blue %d\n", currentBlue);
			analogWrite(PIN_RGB_BLUE, pgm_read_word(&gamma16[currentBlue]));
		}

		if (processColor(targetWhite1, &currentWhite1))
		{
			//Serial.printf("updating white1 %d\n", currentWhite1);
			analogWrite(PIN_WHITE1, pgm_read_word(&gamma16[currentWhite1]));
		}

		if (processColor(targetWhite2, &currentWhite2))
		{
			//Serial.printf("updating white2 %d\n", currentWhite2);
			analogWrite(PIN_WHITE2, pgm_read_word(&gamma16[currentWhite2]));
		}
	}
}