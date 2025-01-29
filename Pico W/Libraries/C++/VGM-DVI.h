#pragma once
#include "Arduino.h"
#include <PicoDVI.h>                  // Core display & graphics library
#include <Fonts/FreeSansBold18pt7b.h> // A custom font
#include <vector.h>

class VGM_DVI
{
public:
    VGM_DVI();
    ~VGM_DVI();
    bool begin();
    void background(uint16_t color);
    void clear(Vector position, Vector size, uint16_t color);
    void color(uint16_t color);
    void text(Vector position, const char *text);
    void text(Vector position, const char *text, const GFXfont *font);
    void text(Vector position, const char *text, const GFXfont *font, uint16_t color);
    DVIGFX16 *display;
    Vector size;
};