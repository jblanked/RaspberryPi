# Description: A simple library to make working with SD cards easier on the Raspberry Pi Pico W with MicroPython.
from machine import SPI, Pin
import sdcard, uos
import sys
import errno


class EasySD:
    def __init__(
        self,
        miso_pin: int = 12,
        cs_pin: int = 13,
        sck_pin: int = 14,
        mosi_pin: int = 15,
    ):
        try:
            self.spi = SPI(1, sck=Pin(sck_pin), mosi=Pin(mosi_pin), miso=Pin(miso_pin))
            self.cs = Pin(cs_pin)
            self.sd = sdcard.SDCard(self.spi, self.cs)
            self.mounted = False
        except Exception as e:
            print(f"Failed to initialize SPI or SD card: {e}")
            sys.exit()

    def mount(self, mount_point: str = "/sd"):
        """Mount the SD card to the specified mount point. Default is /sd."""
        try:
            uos.mount(self.sd, mount_point)
            self.mounted = True
            return True
        except OSError as e:
            if e.errno == errno.EIO:
                print("I/O Error: Possible SD card disconnection or corruption.")
                return False
            elif e.errno == errno.ENODEV:
                print("No SD card detected.")
                return False
            elif e.errno == errno.ENOENT:
                print("Mount point not found.")
                return False
            else:
                print(f"OS Error: {e}")
                return False
        except Exception as e:
            print(f"General Error: {e}")
            return False

    def unmount(self, mount_point: str = "/sd"):
        """Unmount the SD card from the specified mount point. Default is /sd."""
        try:
            uos.umount(mount_point)
            self.mounted = False
            return True
        except OSError as e:
            print(f"Error during unmounting: {e}")
            return False
        except Exception as e:
            print(f"General Error during unmounting: {e}")
            return False

    def write(self, file_path: str, data: str) -> bool:
        """Write data to a file. If the file does not exist, it will be created."""
        try:
            with open(f"/sd/{file_path}", "w") as f:
                f.write(data)
                return True
        except Exception as e:
            print(f"Error occurred while writing: {e}")
            return False

    def read(self, file_path: str) -> str:
        """Read data from a file."""
        try:
            with open(f"/sd/{file_path}", "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error occurred while reading: {e}")
            return ""

    def listdir(self, directory: str = "/sd") -> list:
        """List all files in a directory. Default is /sd."""
        try:
            return uos.listdir(directory)
        except Exception as e:
            print(f"Error occurred while listing files: {e}")
            return []

    def mkdir(self, directory: str) -> bool:
        """Create a directory."""
        try:
            uos.mkdir(f"/sd/{directory}")
            return True
        except Exception as e:
            print(f"Error occurred while making directory: {e}")
            return False

    def remove(self, file_path: str) -> bool:
        """Remove a file."""
        try:
            # Check if it's a file or directory
            stats = uos.stat(f"/sd/{file_path}")
            if stats[0] & 0x4000:  # Directory flag in mode
                print("Error: Path is a directory, use rmdir() instead.")
                return False
            uos.remove(f"/sd/{file_path}")
            return True
        except Exception as e:
            print(f"Error occurred while removing file: {e}")
            return False

    def rmdir(self, directory: str) -> bool:
        """Remove a directory."""
        try:
            uos.rmdir(f"/sd/{directory}")
            return True
        except Exception as e:
            print(f"Error occurred while removing directory: {e}")
            return False

    def rename(self, old_file_path: str, new_file_path: str) -> bool:
        """Rename a file or directory."""
        try:
            uos.rename(f"/sd/{old_file_path}", f"/sd/{new_file_path}")
            return True
        except Exception as e:
            print(f"Error occurred while renaming: {e}")
            return False

    def stat(self, file_path: str) -> dict:
        """Get file stats."""
        try:
            return uos.stat(f"/sd/{file_path}")
        except Exception as e:
            print(f"Error occurred while getting file stats: {e}")
            return {}

    def is_mounted(self) -> bool:
        """Check if the SD card is mounted."""
        return self.mounted
