import microcontroller
import supervisor
import gc


class System:
    def __init__(self):
        pass

    def bootloader_mode(self):
        """Enter the bootloader mode."""
        microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
        microcontroller.reset()

    def free_heap(self):
        """Return the amount of free heap memory."""
        return gc.mem_free()

    def hard_reset(self):
        """Reboot the system."""
        microcontroller.reset()

    def safe_mode(self):
        """Enter the safe mode."""
        microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
        microcontroller.reset()

    def soft_reset(self):
        """Reboot the system without resetting the hardware."""
        supervisor.reload()

    def uf2_mode(self):
        """Enter the UF2 mode."""
        microcontroller.on_next_reset(microcontroller.RunMode.UF2)
        microcontroller.reset()

    def used_heap(self):
        """Return the total heap memory used."""
        return gc.mem_alloc()
