# -*- coding: utf-8 -*-
import logging
import multiprocessing as mp
import time

import pygame

from app.constants import *
from app.ui.main import *
from app.ui.msg import *


def start(color: str, debug: bool, in_queue: mp.Queue, out_queue: mp.Queue):
    assert color in COLOR_LIST

    logging.basicConfig(level={True: logging.DEBUG, False: logging.INFO}[debug], filename="logs/ui.log", filemode="w",
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    window = Window(debug)
    real_fps, max_fps = 0.0, 0.0
    msg = Msg2Window()
    while True:
        time_start = time.time()
        if not in_queue.empty():
            msg = in_queue.get()
            if msg.terminate:
                break
        window.update(msg, in_queue.qsize(), out_queue.qsize(), (real_fps, max_fps))
        if msg.err:
            time.sleep(5)
            break
        window.feedback(out_queue)
        max_fps = 1.0 / (time.time() - time_start)
        time.sleep(max((1.0 / UI_FPS_LIMIT) - (time.time() - time_start), 0))
        real_fps = 1.0 / (time.time() - time_start)
        logging.debug(f"I/O QUE SZ: {in_queue.qsize()}, {out_queue.qsize()}")
        logging.info("FPS %.2f %.2f" % (real_fps, max_fps))
    pygame.quit()
