# -*- coding: utf-8 -*-
import logging
import multiprocessing as mp
import time

import cv2 as cv

from app.constants import *
from app.controller.main import *
from app.controller.msg import *
from app.ui.msg import *


def start(color: str, debug: bool, in_queue: mp.Queue, out_queue: mp.Queue):
    assert color in COLOR_LIST

    logging.basicConfig(level={True: logging.DEBUG, False: logging.INFO}[debug],
                        filename="logs/controller.log", filemode="w",
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    read_video = cv.VideoCapture("assets/s1%s.avi" % COLOR_ENEMY_LIST[color])
    real_fps, max_fps = 0.0, 0.0
    s1 = S1Controller("S1", color, debug)

    def terminate_window():
        if out_queue.full():
            _ = out_queue.get()
        out_queue.put(Msg2Window(terminate=True))

    def report_error():
        if out_queue.full():
            _ = out_queue.get()
        out_queue.put(Msg2Window(img=cv.imread("assets/ERR.jpg"), err=True))

    while True:
        try:
            time_start = time.time()
            if debug:
                ret, img = read_video.read()
                if not ret:
                    logging.debug("VIDEO ENDED")
                    s1.die()
                    terminate_window()
                    break
            else:
                img = s1.img()
            if not in_queue.empty():
                msg: Msg2Controller = in_queue.get()
                s1.act(img, msg)
                if s1.hp == 0:
                    terminate_window()
                    break
            if not out_queue.full():
                out_queue.put(
                    Msg2Window(img=img, hp=s1.hp, heat=s1.heat, bat=s1.bat,
                               aim_method=s1.aim_method, aim_target=s1.aim_target,
                               fps=(real_fps, max_fps)))
            else:
                logging.warning("UI MSG QUEUE FULL")
            max_fps = 1 / (time.time() - time_start)
            time.sleep(max((1.0 / CTR_FPS_LIMIT) - (time.time() - time_start), 0))
            real_fps = 1 / (time.time() - time_start)
            logging.info("FPS %.2f %.2f" % (real_fps, max_fps))
        except Exception as e:
            logging.error(e)
            s1.die()
            report_error()
            break
    read_video.release()
