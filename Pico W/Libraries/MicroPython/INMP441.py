# originally from https://github.com/miketeachman/micropython-i2s-examples/blob/master/examples/record_mic_to_sdcard_blocking.py
# modified to work with INMP441 microphone and Pico W
from EasySD import EasySD
from machine import SPI, Pin, I2S
import os
import gc


class INMP441:
    def __init__(self, miso_gpio=12, cs_gpio=13, sck_gpio=14, mosi_gpio=15):
        # SPI Configuration for SD Card
        self.cs = Pin(cs_gpio, Pin.OUT)
        self.spi = SPI(
            1,
            baudrate=1_000_000,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=SPI.MSB,
            sck=Pin(sck_gpio),
            mosi=Pin(mosi_gpio),
            miso=Pin(miso_gpio),
        )
        self.sd = None
        try:
            self.sd = EasySD(miso_gpio, cs_gpio, sck_gpio, mosi_gpio)
            if self.sd is not None and self.sd.sd:
                self.sd.sd.init_spi(25_000_000)
                if not self.sd.mount():
                    raise RuntimeError("Failed to mount SD card")
        except Exception as e:
            print(e)
            return None

        # I2S Configuration
        self.SCK_PIN = 16
        self.WS_PIN = 17
        self.SD_PIN = 18
        self.I2S_ID = 0
        self.BUFFER_LENGTH_IN_BYTES = 60000

        # Audio Configuration
        self.wav_file = None
        self.WAV_SAMPLE_SIZE_IN_BITS = 16
        self.FORMAT = I2S.MONO
        self.SAMPLE_RATE_IN_HZ = 22_050

        self.audio_in = None
        self.mic_samples = bytearray(10000)
        self.mic_samples_mv = memoryview(self.mic_samples)

    def _create_wav_header(
        self, sample_rate, bits_per_sample, num_channels, num_samples
    ):
        datasize = num_samples * num_channels * bits_per_sample // 8
        header = bytes("RIFF", "ascii")
        header += (datasize + 36).to_bytes(4, "little")
        header += bytes("WAVE", "ascii")
        header += bytes("fmt ", "ascii")
        header += (16).to_bytes(4, "little")
        header += (1).to_bytes(2, "little")
        header += (num_channels).to_bytes(2, "little")
        header += (sample_rate).to_bytes(4, "little")
        header += (sample_rate * num_channels * bits_per_sample // 8).to_bytes(
            4, "little"
        )
        header += (num_channels * bits_per_sample // 8).to_bytes(2, "little")
        header += (bits_per_sample).to_bytes(2, "little")
        header += bytes("data", "ascii")
        header += (datasize).to_bytes(4, "little")
        return header

    def init_audio(self, file_name="inmp441.wav", duration: int = 10):
        num_channels = 1 if self.FORMAT == I2S.MONO else 2
        self.WAV_SAMPLE_SIZE_IN_BYTES = self.WAV_SAMPLE_SIZE_IN_BITS // 8
        self.RECORDING_SIZE_IN_BYTES = (
            duration
            * self.SAMPLE_RATE_IN_HZ
            * self.WAV_SAMPLE_SIZE_IN_BYTES
            * num_channels
        )

        self.wav_file = self.sd.with_open(file_name, "wb")
        wav_header = self._create_wav_header(
            self.SAMPLE_RATE_IN_HZ,
            self.WAV_SAMPLE_SIZE_IN_BITS,
            num_channels,
            self.SAMPLE_RATE_IN_HZ * duration,
        )
        self.wav_file.write(wav_header)

        self.audio_in = I2S(
            self.I2S_ID,
            sck=Pin(self.SCK_PIN),
            ws=Pin(self.WS_PIN),
            sd=Pin(self.SD_PIN),
            mode=I2S.RX,
            bits=self.WAV_SAMPLE_SIZE_IN_BITS,
            format=self.FORMAT,
            rate=self.SAMPLE_RATE_IN_HZ,
            ibuf=self.BUFFER_LENGTH_IN_BYTES,
        )

    def record(self, file_name="inmp441.wav", duration: int = 10, unmount: bool = True):
        if not self.sd:
            raise RuntimeError("SD not initialized..")
        self.init_audio(file_name,duration)
        if not self.audio_in:
            raise RuntimeError("Audio input not initialized. Call init_audio() first.")

        num_sample_bytes_written_to_wav = 0
        print("==========  START RECORDING ==========")

        try:
            while num_sample_bytes_written_to_wav < self.RECORDING_SIZE_IN_BYTES:
                num_bytes_read_from_mic = self.audio_in.readinto(self.mic_samples_mv)
                if num_bytes_read_from_mic > 0:
                    num_bytes_to_write = min(
                        num_bytes_read_from_mic,
                        self.RECORDING_SIZE_IN_BYTES - num_sample_bytes_written_to_wav,
                    )
                    num_bytes_written = self.wav_file.write(
                        self.mic_samples_mv[:num_bytes_to_write]
                    )
                    num_sample_bytes_written_to_wav += num_bytes_written

            print("==========  DONE RECORDING ==========")
        except (KeyboardInterrupt, Exception) as e:
            print("Caught exception: {} {}".format(type(e).__name__, e))
        finally:
            self._cleanup(unmount)

    def _cleanup(self, unmount: bool = True):
        if self.wav_file:
            self.wav_file.close()
        if self.audio_in:
            self.audio_in.deinit()
        if unmount:
            self.sd.unmount()
            self.spi.deinit()
        
    def read_wav_file(self, file_name):
        try:            
            wav_file = self.sd.with_open(file_name, "rb")
            wav_file.seek(44)  # Skip WAV header
            audio_data = wav_file.read()
            return audio_data
        except OSError as e:
            print(f"Error reading file: {e}")
            return None


