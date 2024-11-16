# Raspberry Pi 2w Library for working with the PiCamera
from time import sleep
from picamera2 import Picamera2, Preview
from libcamera import Transform
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

# if you get: QStandardPaths: wrong permissions on runtime directory /run/user/1000, 0770 instead of 0700
# run: sudo chmod 0700 /run/user/1000


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
        """Headless picture capture"""
        self.camera.create_still_configuration()
        self.camera.start()
        self.camera.capture_file(file_path)
        self.camera.stop()

    def video(self, file_path: str, duration: int) -> None:
        """Headless video capture"""
        video_config = self.camera.create_video_configuration(
            controls={"FrameRate": 30.0}
        )
        self.camera.configure(video_config)
        self.camera.start()
        encoder = H264Encoder(10000000)
        output = FfmpegOutput(file_path)
        self.camera.start_recording(encoder, output)
        sleep(duration)
        self.camera.stop_recording()
        self.camera.stop()
