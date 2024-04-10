from pydantic import BaseSettings
from enum import Enum
import ipaddress
from typing import Union
import socket
import cv2

class SRC(Enum):
    cam = "cam"
    img = "img"
    
class Extension(Enum):
    txt = ".txt"
    bin = ".bin"
    
class AppSettings(BaseSettings):
    LOGGING: bool = True
    DEBUG: bool = False
    SOURCE: str = SRC.cam.value
    PORT: int = 5051
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        
    

class ImageSettings(AppSettings):
    WIDTH: int = 2448
    HEIGHT: int = 2048
    FRAME_FORMAT: str = 'GRAY'

    @property
    def frame_format(self) -> int:
        if self.FRAME_FORMAT.upper() == 'GRAY':
            return -1
        elif self.FRAME_FORMAT.upper() == 'BAYER':
            # return cv2.COLOR_BayerRG2RGB # TO DO проверить цвета, если неправильно переделать в COLOR_BayerRG2BGR
            return cv2.COLOR_BayerRG2GRAY # TO DO проверить цвета, если неправильно переделать в COLOR_BayerRG2BGR
        else:
            raise ValueError("FRAME_FORMAT must be 'GRAY' or 'BAYER'")

class TcpCameraSettings(ImageSettings):
    CAM_HOST: Union[ipaddress.IPv4Address, str] = '/tmp/camera.sock'
    CAM_PORT: int = 8058

    @property
    def protocol(self) -> list:
        if isinstance(self.CAM_HOST, str):
            return (socket.AF_UNIX, socket.SOCK_STREAM)
        return (socket.AF_INET, socket.SOCK_STREAM)

    @property
    def addres(self) -> list:
        if isinstance(self.CAM_HOST, str):
            return self.CAM_HOST
        return (str(self.CAM_HOST), self.CAM_PORT)


class WriterSettings(ImageSettings):
    FRAMES_PER_SECOND: int = 20


CAM_SETTINGS = TcpCameraSettings()
WRITE_SETTINGS = WriterSettings()
APP_SETTINGS = AppSettings()
