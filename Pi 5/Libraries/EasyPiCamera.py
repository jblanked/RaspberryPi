# Raspberry Pi 5 Library for working with the PiCamera
from picamera2 import Picamera2, Preview
from time import sleep
from libcamera import Transform


class EasyPiCamera:
    def __init__(self) -> None:
        self.camera = Picamera2()

    def preview(self, duration: int, vflip: bool = False, hflip: bool = False) -> None:
        self.camera.create_preview_configuration()
        self.camera.start_preview(
            Preview.QTGL, transform=Transform(vflip=vflip, hflip=hflip)
        )
        self.camera.start()
        sleep(duration)
        self.camera.close()

    def picture(self, file_path: str) -> None:
        self.camera.create_still_configuration()
        self.camera.start_and_capture_file(name=file_path)
        self.camera.close()

    def video(self, file_path: str, duration: int, show_preview: bool = True):
        self.camera.create_video_configuration(controls={"FrameRate": 30.0})
        self.camera.start_and_record_video(
            output=file_path, duration=duration, show_preview=show_preview
        )
        self.camera.close()
