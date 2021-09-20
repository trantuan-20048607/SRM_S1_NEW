# -*- coding: utf-8 -*-
import logging
import time
import threading
import multiprocessing as mp
import cv2 as cv
import pygame
import numpy as np
from PIL import Image
from app.ui.msg import *
from app.ui.main import *


def start(color: str, debug: bool, in_queue: mp.Queue, out_queue: mp.Queue, record: bool):
    logging.basicConfig(level={True: logging.DEBUG, False: logging.INFO}[debug], filename="logs/ui.log", filemode='w',
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    if record:
        write_video = cv.VideoWriter(f"tmp/record_{color}.mp4",
                                     cv.VideoWriter_fourcc(*'avc1'), 30,
                                     Window.SCREEN_SIZE, True)
    window = Window(debug)
    msg_cache = Msg2Window()

    while True:
        time_start = time.time()
        using_cache = in_queue.empty()
        if not using_cache:
            msg: Msg2Window = in_queue.get()
            if msg.terminate:
                break
            if not debug:
                msg.img = cv.transpose(msg.img)
            msg_cache = msg
        else:
            msg = msg_cache
        window.update(msg, in_queue.qsize(), out_queue.qsize())
        if record:
            write_video.write(cv.cvtColor(np.asarray(Image.frombytes("RGB", Window.SCREEN_SIZE, pygame.image.tostring(
                window.screen.subsurface(0, 0, Window.SCREEN_SIZE[0], Window.SCREEN_SIZE[1]), "RGB"))),
                                          cv.COLOR_RGB2BGR))
        if not window.ctr_error:
            time.sleep(5)
            break
        window.feedback(out_queue)
        if not using_cache:
            logging.debug(f"FPS {1 / (time.time() - time_start)}")
            logging.debug(f"I/O QUE SZ: {in_queue.qsize()}, {out_queue.qsize()}")
    if record:
        write_video.release()
    pygame.quit()
