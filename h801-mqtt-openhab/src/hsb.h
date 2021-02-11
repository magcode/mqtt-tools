#pragma once

#include <Arduino.h>

class Hsb {
public:
    Hsb() : _hue(0), _saturation(0), _brightness(0) {}
    Hsb(unsigned int hue, unsigned int saturation, unsigned int brightness) : _hue(hue), _saturation(saturation), _brightness(brightness) {
        if (this->_hue > 360) {
            this->_hue = 360;
        }
        if (this->_saturation > 100) {
            this->_saturation = 100;
        }
        if (this->_brightness > 100) {
            this->_brightness = 100;
        }
    }

    String toString() {
        String ret = "";
        ret += this->getHue();
        ret += ",";
        ret += this->getSaturation();
        ret += ",";
        ret += this->getBrightness();
        return ret;
    }

    unsigned int getHue() {
        return this->_hue;
    }

    unsigned int getSaturation() {
        return this->_saturation;
    }

    unsigned int getBrightness() {
        return this->_brightness;
    }

    void setHue(unsigned int hue) {
        this->_hue = constrain(hue, 0, 360);
    }

    void setSaturation(unsigned int saturation) {
        this->_saturation = constrain(saturation, 0, 100);
    }

    void setBrightness(unsigned int brightness) {
        this->_brightness = constrain(brightness, 0, 100);
    }

    bool toRgb(unsigned int *red, unsigned int *green, unsigned int *blue, unsigned int scale) {
        // https://de.wikipedia.org/wiki/HSV-Farbraum#Umrechnung_HSV_in_RGB
        if (this->_brightness == 0) {
            // brightness = 0 -> black
            *red = 0;
            *green = 0;
            *blue = 0;
        } else if (this->_saturation == 0) {
            // saturatino = 0 -> grey, r, g and b are all equal
            *red = ((double)this->_brightness / 100.0) * scale;
            *green = *red;
            *blue = *red;
        } else {
            double saturationDouble = this->_saturation / 100.0;
            double brightnessDouble = this->_brightness / 100.0;

            double hi = this->_hue / 60.0;
            int hiInt = (int)hi;
            // f is the remainder from hue / 60
            double f = hi - hiInt;
            
            // Serial.printf("hi %f hiInt %d f %f\n", hi, hiInt, f);
            
            // the _ values are between 0 and 1
            double _red = 0;
            double _green = 0;
            double _blue = 0;
            
            double p = brightnessDouble * (1 - saturationDouble);
            double q = brightnessDouble * (1 - saturationDouble * f);
            double t = brightnessDouble * (1 - saturationDouble * (1 - f));
            
            // Serial.printf("p %f q %f t %f\n", p, q, t);
            
            switch (hiInt) {
                case 0:
                case 6:
                    _red = brightnessDouble;
                    _green = t;
                    _blue = p;
                    break;
                case 1:
                    _red = q;
                    _green = brightnessDouble;
                    _blue = p;
                    break;
                case 2:
                    _red = p;
                    _green = brightnessDouble;
                    _blue = t;
                    break;
                case 3:
                    _red = p;
                    _green = q;
                    _blue = brightnessDouble;
                    break;
                case 4:
                    _red = t;
                    _green = p;
                    _blue = brightnessDouble;
                    break;
                case 5:
                    _red = brightnessDouble;
                    _green = p;
                    _blue = q;
                    break;
                default:
                    return false;
            }
            
            _red *= scale;
            _green *= scale;
            _blue *= scale;
            
            *red = _red;
            *green = _green;
            *blue = _blue;
        }
        // Serial.printf("%f %f %f\n", _red, _green, _blue);
        return true;
    }

    void fromRgb(unsigned int r, unsigned int g, unsigned int b, double scale) {
        // taken from Eclipse Smarthome Project: https://github.com/eclipse/smarthome/blob/a8b63edd3a624331fb3bb6774b6cc46b5d2f213b/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/library/types/HSBType.java
        double tmpHue = 0.0;
        double tmpSaturation = 0.0;
        double tmpBrightness = 0.0;
        int max = (r > g) ? r : g;
        if (b > max) {
            max = b;
        }
        int min = (r < g) ? r : g;
        if (b < min) {
            min = b;
        }
        tmpBrightness = max / scale;
        tmpSaturation = (max != 0 ? ((float) (max - min)) / ((float) max) : 0) * 100;
        if (tmpSaturation == 0) {
            tmpHue = 0;
        } else {
            double red = ((float) (max - r)) / ((float) (max - min));
            double green = ((float) (max - g)) / ((float) (max - min));
            double blue = ((float) (max - b)) / ((float) (max - min));
            if (r == max) {
                tmpHue = blue - green;
            } else if (g == max) {
                tmpHue = 2.0 + red - blue;
            } else {
                tmpHue = 4.0 + green - red;
            }
            tmpHue = tmpHue / 6.0 * 360;
            if (tmpHue < 0) {
                tmpHue = tmpHue + 360.0;
            }
        }

        this->_hue = tmpHue;
        this->_saturation = tmpSaturation;
        this->_brightness = tmpBrightness;
    }

private:
    unsigned int _hue;
    unsigned int _saturation;
    unsigned int _brightness;

};