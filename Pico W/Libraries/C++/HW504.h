#pragma once
#include "Arduino.h"
#include "vector.h"
/*
# Wiring (HW504 -> Pico):
# SW -> GP17 (Pin 22 - TX)
# VRx -> GP27 (Pin 32 - ADC1)
# VRy -> GP26 (Pin 31 - ADC0)
# GND -> GND
# 5V -> VSYS (Pin 39)
*/

#define HW_LEFT_BUTTON 0
#define HW_RIGHT_BUTTON 1
#define HW_UP_BUTTON 2
#define HW_DOWN_BUTTON 3
#define HW_CENTER_BUTTON 4

#define HW_ORIENTATION_NORMAL 0
#define HW_ORIENTATION_90 1
#define HW_ORIENTATION_180 2
#define HW_ORIENTATION_270 3

class HW504
{
public:
    int x_axis;
    int y_axis;
    int orientation;
    int button;

    HW504(int x_pin = 26, int y_pin = 27, int button_pin = 17, int orientation = HW_ORIENTATION_NORMAL);
    Vector axes();                             // Read the raw ADC values from both axes and transform them based on the current orientation.
    bool value(int button = HW_CENTER_BUTTON); // Return the state of a button based on the transformed x,y axis values.

private:
    int _button(); // Read the button value from the joystick
    int _x_axis(); // Return the transformed x-axis value
    int _y_axis(); // Return the transformed y-axis value
};