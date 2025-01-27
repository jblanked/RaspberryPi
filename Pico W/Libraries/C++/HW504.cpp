#include "HW504.h"

HW504::HW504(int x_pin, int y_pin, int button_pin, int orientation)
{
    this->x_axis = x_pin;
    this->y_axis = y_pin;
    this->button = button_pin;
    this->orientation = orientation;
    pinMode(this->x_axis, INPUT);
    pinMode(this->y_axis, INPUT);
    pinMode(this->button, INPUT_PULLUP);
}

Vector HW504::axes()
{
    Vector v;
    v.x = analogRead(this->x_axis);
    v.y = analogRead(this->y_axis);

    switch (this->orientation)
    {
    case HW_ORIENTATION_NORMAL:
        break;
    case HW_ORIENTATION_90:
        v = Vector(v.y, 1023 - v.x);
        break;
    case HW_ORIENTATION_180:
        v = Vector(1023 - v.x, 1023 - v.y);
        break;
    case HW_ORIENTATION_270:
        v = Vector(1023 - v.y, v.x);
        break;
    default:
        break;
    }
    return v;
}

int HW504::_button()
{
    return digitalRead(this->button);
}

int HW504::_x_axis()
{
    Vector v = this->axes();
    return v.x;
}

int HW504::_y_axis()
{
    Vector v = this->axes();
    return v.y;
}

bool HW504::value(int button)
{
    switch (button)
    {
    case HW_LEFT_BUTTON:
        return this->_x_axis() < 100;
    case HW_RIGHT_BUTTON:
        return this->_x_axis() > 1000;
    case HW_UP_BUTTON:
        return this->_y_axis() < 100;
    case HW_DOWN_BUTTON:
        return this->_y_axis() > 1000;
    case HW_CENTER_BUTTON:
        return this->_button() == LOW;
    default:
        return false;
    }
}
