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
    fps = 0
    msg = Msg2Window()
    while True:
        time_start = time.time()
        if not in_queue.empty():
            msg = in_queue.get()
            if msg.terminate:
                break
        window.update(msg, in_queue.qsize(), out_queue.qsize(), fps)
        if msg.err:
            time.sleep(5)
            break
        window.feedback(out_queue)
        while time.time() - time_start < 1.0 / UI_FPS_LIMIT:
            time.sleep(0.1 / UI_FPS_LIMIT)
        fps = 1.0 / (time.time() - time_start)
        logging.debug(f"I/O QUE SZ: {in_queue.qsize()}, {out_queue.qsize()}")
        logging.info("FPS %.2f" % fps)
    pygame.quit()
