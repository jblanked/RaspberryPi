#include "VGM-DVI.h"

VGM_DVI::VGM_DVI()
{
    size = Vector(320, 240);
    display = new DVIGFX16(DVI_RES_320x240p60, picodvi_dvi_cfg);
}

VGM_DVI::~VGM_DVI()
{
    delete display;
}

bool VGM_DVI::begin()
{
    if (!display->begin())
        return false;

    display->fillScreen(0); // Start by clearing the screen; color 0 = black
    display->setFont();
    display->setTextSize(1);
    return true;
}

void VGM_DVI::background(uint16_t color)
{
    display->fillScreen(color);
}

void VGM_DVI::clear(Vector position, Vector size, uint16_t color)
{
    display->fillRect(position.x, position.y, size.x, size.y, color);
}

void VGM_DVI::color(uint16_t color)
{
    display->setTextColor(color);
}

void VGM_DVI::text(Vector position, const char *text)
{
    display->setCursor(position.x, position.y);
    display->print(text);
}

void VGM_DVI::text(Vector position, const char *text, const GFXfont *font)
{
    display->setFont(font);
    display->setCursor(position.x, position.y);
    display->print(text);
}

void VGM_DVI::text(Vector position, const char *text, const GFXfont *font, uint16_t color)
{
    display->setFont(font);
    display->setTextColor(color);
    display->setCursor(position.x, position.y);
    display->print(text);
}