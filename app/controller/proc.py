# -*- coding: utf-8 -*-
import logging
import multiprocessing as mp
import time

import cv2 as cv

from app.controller.main import *
from app.controller.msg import *
from app.ui.msg import *


def start(color: str, debug: bool, in_queue: mp.Queue, out_queue: mp.Queue, record: bool):
    logging.basicConfig(level={True: logging.DEBUG, False: logging.INFO}[debug],
                        filename="logs/controller.log", filemode='w',
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")

    if debug:
        video_src = "assets/s1%s.avi" % {"red": "blue", "blue": "red"}[color]
        read_video = cv.VideoCapture(video_src)
        video_fps = read_video.get(cv.CAP_PROP_FPS)

    s1 = S1Controller("S1", color, debug)
    limit = False

    def terminate_window(window_queue: mp.Queue):
        if window_queue.full():
            _ = window_queue.get()
        window_queue.put(Msg2Window(terminate=True))

    def report_error(window_queue: mp.Queue):
        if window_queue.full():
            _ = window_queue.get()
        window_queue.put(Msg2Window(img=cv.transpose(cv.imread("assets/ERR.jpg")), err=True))

    while True:
        time_start = time.time()

        if debug:
            ret, img = read_video.read()

            if not record:
                time.sleep(0.05 / video_fps)

            if not ret:
                logging.debug("VIDEO ENDED")
                terminate_window(out_queue)
                break

        else:
            img = s1.get_img()

        if not debug:
            s1.hit()

        if not in_queue.empty():
            msg: Msg2Controller = in_queue.get()

            try:
                s1.act(img, msg)
            except Exception as e:
                logging.error(e)

                report_error(out_queue)
                break

            if msg.terminate or s1.hp == 0:
                terminate_window(out_queue)
                break

        s1.cool()

        if not out_queue.full():

            if out_queue.empty() or not limit:
                if debug:
                    img = cv.transpose(img)

                    out_queue.put(
                        Msg2Window(img=img, hp=s1.hp, heat=s1.heat, bat=s1.bat,
                                   aim_method=s1.aim_method, target=s1.target))

        else:
            logging.warning("UI MSG QUEUE FULL")

        if not limit:
            logging.debug(f"FPS {1 / (time.time() - time_start)}")

        limit = out_queue.qsize() > 2
