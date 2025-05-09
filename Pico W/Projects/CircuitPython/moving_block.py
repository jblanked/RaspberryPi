import displayio
import gc
import time

displayio.release_displays()

gc.collect()
print(gc.mem_free())

from Board import (
    Board,
    BOARD_TYPE_VGM,
    VGM_BOARD_CONFIG,
)  # https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/CircuitPython/Board.py - add to the /lib folder

from Draw import (
    Draw,
    TFT_WHITE,
    TFT_BLACK,
)  # https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/CircuitPython/Draw.py - add to the /lib folder

from Vector import (
    Vector,
)  # https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/CircuitPython/Vector.py - add to the /lib folder

gc.collect()
print(gc.mem_free())

# Initialize the display
display = Draw(VGM_BOARD_CONFIG)

gc.collect()
print(gc.mem_free())

# First, set up the palette correctly
display.set_palette(0, TFT_BLACK)  # Ensure index 0 is black
display.set_palette(1, TFT_WHITE)  # Ensure index 1 is white

# Ball properties
ball_pos = Vector(50, 50)
ball_vel = Vector(2, 3)
ball_radius = 10

# Main animation loop
try:
    while True:
        # draw the ball on a fresh (blank) back buffer
        display.rect_fill(
            Vector(ball_pos.x - ball_radius, ball_pos.y - ball_radius),
            Vector(ball_radius * 2, ball_radius * 2),
            TFT_BLACK,
        )

        # show it (and implicitly get another blank buffer for next frame)
        display.swap()

        ball_pos.x += 1

        # Small delay to control animation speed
        time.sleep(0.033)  # Approximately 30 FPS for better visibility

except KeyboardInterrupt:
    # Clean up on exit
    display.deinit()
    print("Animation stopped")
