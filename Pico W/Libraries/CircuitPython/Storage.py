import gc
import storage


class Storage:
    """Class to control the storage on a Raspberry Pi Pico device."""

    def __init__(self):
        pass

    def execute_script(self, filepath: str = "/") -> None:
        """Run a Python file from the storage."""
        with open(filepath, "r") as f:
            code = compile(f.read(), filepath, "exec")
            exec(code, globals())

    def heap_free(self) -> int:
        """Return the amount of free heap memory."""
        return gc.mem_free()

    def heap_used(self) -> int:
        """Return the total heap memory used."""
        return gc.mem_alloc()
