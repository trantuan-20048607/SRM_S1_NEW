# -*- coding: utf-8 -*-

import logging
import multiprocessing as mp
import time

import pygame

from app.config import *
from app.ui.main import *
from app.ui.msg import *


def start(color: str, debug: bool, in_queue: mp.Queue, out_queue: mp.Queue, record: bool):
    assert color in COLOR_LIST

    logging.basicConfig(level={True: logging.DEBUG, False: logging.INFO}[debug], filename="logs/ui.log", filemode="w",
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    window, real_fps, max_fps, msg = Window(debug, record), 0.0, 0.0, Msg2Window()
    while True:
        time_start = time.time()
        logging.debug(f"I {in_queue.qsize()} O {out_queue.qsize()}")
        if not in_queue.empty():
            msg = in_queue.get()
            if msg.terminate:
                break
        window.update(msg, in_queue.qsize(), out_queue.qsize(), (real_fps, max_fps))
        if msg.err:
            break
        window.feedback(out_queue)
        max_fps = 1.0 / max((time.time() - time_start), 1e-4)
        time.sleep(max((1.0 / UI_FPS_LIMIT) - (time.time() - time_start), 0))
        real_fps = 1.0 / max((time.time() - time_start), 1e-4)
        logging.info("FPS %.2f %.2f" % (real_fps, max_fps))
    pygame.quit()
