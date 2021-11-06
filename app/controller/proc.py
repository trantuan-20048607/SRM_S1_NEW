# -*- coding: utf-8 -*-

import logging
import multiprocessing as mp
import time

import cv2 as cv

from app.config import *
from app.controller.config import S1Robot
from app.controller.main import *
from app.ui.msg import *


def start(color: str, debug: bool, in_queue: mp.Queue, out_queue: mp.Queue, record: bool):
    assert color in COLOR_LIST

    logging.basicConfig(level={True: logging.DEBUG, False: logging.INFO}[debug],
                        filename="logs/controller.log", filemode="w",
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    if debug:
        read_video = cv.VideoCapture("assets/s1%s.avi" % ENEMY_COLOR[color])
    if record:
        write_video = cv.VideoWriter(f'tmp/{time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())}_s1{color}.avi',
                                     cv.VideoWriter_fourcc(*'XVID'), CTR_FPS_LIMIT, SCREEN_SIZE, True)
    real_fps, max_fps, s1, current_msg_id = 0.0, 0.0, S1Controller("S1", color, debug), 0

    def terminate_window():
        while not out_queue.empty():
            _ = out_queue.get()
        out_queue.put(Msg2Window(terminate=True))

    def report_error():
        while not out_queue.empty():
            _ = out_queue.get()
        out_queue.put(Msg2Window(
            img=cv.transpose(cv.imread("assets/ERR.jpg")), err=True))

    try:
        while s1.hp > 0:
            time_start = time.time()
            if debug:
                ret, img = read_video.read()
                if not ret:
                    s1.die()
            else:
                img = s1.img()
            if img is None:
                continue
            logging.debug(f"I {in_queue.qsize()} O {out_queue.qsize()}")
            if not in_queue.empty():
                msg = in_queue.get()
                current_msg_id = msg.id
                s1.act(img, msg)
            if not out_queue.full():
                out_queue.put(
                    Msg2Window(corresponding_id=current_msg_id,
                               img=cv.transpose(img), hp=s1.hp, heat=s1.heat, bat=s1.bat,
                               speed=s1.speed, aim_method=s1.aim_method, aim_target=s1.aim_target,
                               fps=(real_fps, max_fps)))
            if record:
                cv.putText(img, "FPS %.0f/%d" % (real_fps, CTR_FPS_LIMIT),
                           (0, 24), cv.FONT_HERSHEY_SIMPLEX,
                           0.85, (0, 192, 0), 2)
                cv.putText(img, "HP %d/%d" % (s1.hp, S1Robot.INITIAL_HP),
                           (0, 48), cv.FONT_HERSHEY_SIMPLEX,
                           0.85, (0, 192, 0) if s1.hp * 2 > S1Robot.INITIAL_HP else (10, 20, 160), 2)
                cv.putText(img, "HEAT %d/%d" % (s1.heat, S1Robot.MAX_HEAT),
                           (0, 72), cv.FONT_HERSHEY_SIMPLEX,
                           0.85, (0, 192, 0) if s1.heat * 1.2 < S1Robot.MAX_HEAT else (10, 20, 160), 2)
                if s1.speed != (0, 0):
                    cv.putText(img, "MOVING",
                               (0, 120), cv.FONT_HERSHEY_SIMPLEX,
                               0.85, (50, 150, 250), 2)
                if s1.aim_method != "manual":
                    cv.putText(img, f"AUTO AIM: {AUTO_AIM_METHOD_LIST[s1.aim_method]}",
                               (0, 96), cv.FONT_HERSHEY_SIMPLEX,
                               0.85, (0, 192, 0), 2)
                    cv.putText(img, f"{s1.aim_target[0]}, {s1.aim_target[1]}",
                               (s1.aim_target[0] - 76, s1.aim_target[1] - 60), cv.FONT_HERSHEY_SIMPLEX,
                               0.75, (0, 192, 0), 2)
                    cv.rectangle(img, (s1.aim_target[0] - 80, s1.aim_target[1] - 80),
                                 (s1.aim_target[0] + 80, s1.aim_target[1] + 80), (0, 192, 0), 2)
                else:
                    cv.putText(img, "MANUAL AIM",
                               (0, 96), cv.FONT_HERSHEY_SIMPLEX,
                               0.85, (50, 150, 250), 2)
                write_video.write(img)
            max_fps = 1.0 / max((time.time() - time_start), 1e-4)
            time.sleep(max((1.0 / CTR_FPS_LIMIT) - (time.time() - time_start), 0))
            real_fps = 1.0 / max((time.time() - time_start), 1e-4)
            logging.info("FPS %.2f %.2f" % (real_fps, max_fps))
        terminate_window()
    except Exception as e:
        logging.error(e)
        s1.die()
        report_error()
    if debug:
        read_video.release()
    if record:
        write_video.release()
