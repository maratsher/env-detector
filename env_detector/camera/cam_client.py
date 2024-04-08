import ctypes
import select
import signal
import socket
import time
import os
from contextlib import ContextDecorator
import multiprocessing as mp
from multiprocessing.connection import Connection

import numpy as np

from env_detector.utils.camera_utils import ImageFrame, FrameMetadata, IMAGE_FORMAT
from env_detector.camera.base import BaseCamera
from env_detector.config.settings import CAM_SETTINGS
from env_detector.config import logger


WIDTH = CAM_SETTINGS.WIDTH
HEIGHT = CAM_SETTINGS.HEIGHT
TIMESTAMP_SIZE = 6
PIXEL_FORMAT_SIZE = 1
FRAME_OFFSET = TIMESTAMP_SIZE + PIXEL_FORMAT_SIZE

BODY_PAYLOAD = PIXEL_FORMAT_SIZE + TIMESTAMP_SIZE + WIDTH * HEIGHT

INTP = ctypes.POINTER(ctypes.c_uint8)

START_STREAM = b'start_stream'
GET_FRAME_MSG = b'get_frame'
CLOSE_STREAM = b'stop_stream'


class ProcessWatchDog:
    def __init__(self, is_stop):
        self.is_stop = is_stop
        self._process_alive = True
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, *args, **kwargs):
        self._process_alive = False

    @property
    def alive(self):
        return self._process_alive and (not bool(self.is_stop.value))


MAX_POLL_TIMEOUT = 5


def record_frames(ts_queue: Connection, lock_array: mp.Array, buffer_array: np.array, is_stop):

    def make_request_and_response(cmd, payload_size):
        sock.send(cmd)
        infds, outfds, errfds = select.select([sock], [], [], MAX_POLL_TIMEOUT)
        if infds:
            buf = sock.recv(payload_size, socket.MSG_WAITALL)
            return buf, True
        return None, False

    sock = socket.socket(*CAM_SETTINGS.protocol)
    sock.connect(CAM_SETTINGS.addres)
    logger.info('Connected to camera.')
    start_msg, flag = make_request_and_response(START_STREAM, 14)
    if not flag:
        logger.info(f'The camera does not respond.')
        sock.close()
        return
    # log.info(f'Start status "{start_msg.decode("utf-8")}"')
    # time.sleep(1)

    status = ProcessWatchDog(is_stop)

    while True:
        body, flag = make_request_and_response(GET_FRAME_MSG, BODY_PAYLOAD)
        if not flag:
            break
        logger.debug(f'Received frame with len {len(body)}')
        pixel_format = int.from_bytes(
            body[:PIXEL_FORMAT_SIZE], byteorder='big')
        timestamp = int.from_bytes(
            body[PIXEL_FORMAT_SIZE:FRAME_OFFSET], byteorder='big')
        img_bytes = body[FRAME_OFFSET:]
        ptr = ctypes.cast(img_bytes, INTP)
        np_img = np.ctypeslib.as_array(ptr, (HEIGHT, WIDTH))
        if not status.alive:
            break
        lock_array.acquire()
        buffer_array[:] = np_img
        ts_queue.send((timestamp, pixel_format))

    logger.info('Stop grabbing frames.')
    stop_msg, flag = make_request_and_response(CLOSE_STREAM, 14)
    sock.close()
    # time.sleep(1)
    # sys.exit(0)


class TcpCamera(ContextDecorator, BaseCamera):
    def __init__(self, is_stop, **kw):
        super().__init__()
        self.is_stop = is_stop
        self._pipe = mp.Pipe(duplex=False)
        self._mp_array = mp.Array(
            'I', int(np.prod((2048, 2448))), lock=mp.Lock())
        self._np_array = np.frombuffer(
            self._mp_array.get_obj(), dtype='I').reshape((2048, 2448))
        self._record_frames_p = mp.Process(target=record_frames,
                                           args=(self._pipe[1], self._mp_array, self._np_array, self.is_stop), daemon=True)

    def _init(self):
        logger.info(f"Start cam from {self.__class__.__name__} source")
        self._record_frames_p.start()

    @property
    def shape(self):
        return (WIDTH, HEIGHT)

    def _exit(self):
        self.is_stop.value = 1
        # self._record_frames_p.terminate()
        os.kill(self._record_frames_p.pid, signal.SIGKILL)
        # self._record_frames_p.join(timeout=10)

    def get_image(self) -> ImageFrame:
        if not self._pipe[0].poll(timeout=1):
            return None

        ts, pf = self._pipe[0].recv()

        frame = self._np_array.astype('uint8').copy()
        self._mp_array.release()
        t = FrameMetadata(ts / 1000, 0, 0)
        # if CAM_SETTINGS.frame_format > 0:
        #     frame = cv2.cvtColor(frame, CAM_SETTINGS.frame_format)
        return ImageFrame(frame, t, IMAGE_FORMAT(pf))

    def get_probe(self):
        return {
            'width': WIDTH,
            'height': HEIGHT,
            'frames_per_second': 20
        }
