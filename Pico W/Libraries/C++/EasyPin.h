#define ON HIGH
#define OFF LOW
#define PICO_LED LED_BUILTIN
/*
- LED_BUILTIN is the built-in LED on the Raspberry Pi Pico.
- 21 is the GP21 pin on the Raspberry Pi Pico, which is the 27th pin and is where an external LED should be connected.
*/
class EasyPin
{
public:
    EasyPin(int pin = PICO_LED)
    {
        _pin = pin;
        pinMode(_pin, OUTPUT);
    }

    void on()
    {
        digitalWrite(_pin, ON);
    }

    void off()
    {
        digitalWrite(_pin, OFF);
    }

    void toggle()
    {
        digitalWrite(_pin, !digitalRead(_pin));
    }

    void blink(int duration)
    {
        on();
        delay(duration);
        off();
    }

    void blink(int duration, int times)
    {
        for (int i = 0; i < times; i++)
        {
            blink(duration);
            delay(duration);
        }
    }

private:
    int _pin;
};