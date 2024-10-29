#include <Wire.h>              // This library allows you to communicate with I2C devices
#include <LiquidCrystal_I2C.h> // https://github.com/fdebrabander/Arduino-LiquidCrystal-I2C-library
/* Raspberry Pi Pico Wiring
GND -> GRND
VCC —> 5v (VBUS)
SDA —> GP4 (6th pin - I2C0 SDA)
SCL —> GP5 (7th pin - I2C0 SCL)
*/
class EasyLCD
{
public:
    // Change the address to 0x3F is you can not see the message on the LCD
    EasyLCD(uint8_t lcd_addr = 0x27, uint8_t lcd_cols = 16, uint8_t lcd_rows = 2)
        : lcd(lcd_addr, lcd_cols, lcd_rows)
    {
        LiquidCrystal_I2C ini(lcd_addr, lcd_cols, lcd_rows); // Initialize LCD with provided dimensions
        this->lcd = ini;
        this->columns = lcd_cols;
    }

    void begin(bool backlight = true)
    {
        this->lcd.begin();
        if (backlight)
        {
            this->lcd.backlight();
        }
    }

    void write(String str, int row = 0, bool clear = false)
    {
        if (clear)
        {
            this->clear();
        }
        this->lcd.setCursor(0, row);

        if (row == 0 && str.length() > this->columns)
        {
            this->lcd.print(str.substring(0, this->columns));
            this->lcd.setCursor(0, 1);
            this->lcd.print(str.substring(this->columns));
        }
        else if (str.length() <= this->columns)
        {
            this->lcd.print(str);
        }
        else
        {
            this->lcd.print(str.substring(0, this->columns));
        }
    }

    void clear()
    {
        this->lcd.clear();
    }

private:
    LiquidCrystal_I2C lcd; // Declare without parameters here
    int columns;
};
