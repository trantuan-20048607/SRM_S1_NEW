# -*- coding: utf-8 -*-

import time

import cv2 as cv

import app.core.vision as vision
from app.config import *


def start(color: str):
    read_video, play_video = cv.VideoCapture(f"assets/s1{color}.avi"), True
    ret, img_ = read_video.read()

    # 初始化数值
    max_fps, real_fps, cost = 0.0, 0.0, 0.0

    # TODO 此处填写测试环境初始化代码

    while ret:
        time_start = time.time()

        img = img_.copy()

        # 目标位置
        tgt = vision.feed(img, color)

        # 显示 FPS
        cv.putText(img, "FPS %d/%d" % (int(real_fps), int(max_fps)) if
        max_fps < 1e4 else "FPS %d/INF" % int(real_fps),
                   (0, 24), cv.FONT_HERSHEY_SIMPLEX,
                   0.85, (0, 192, 0), 2)

        # 显示时间开销
        cv.putText(img, "COST %.5f" % cost,
                   (0, 48), cv.FONT_HERSHEY_SIMPLEX,
                   0.85, (0, 192, 0), 2)

        # TODO 此处更改窗口标题
        cv.imshow("VISION MODULE TEST", img)

        # TODO 此处填写对每一帧执行的测试代码

        cost = time.time() - time_start
        max_fps = 1.0 / max((time.time() - time_start), 1e-4)
        k = cv.waitKey(max(int(1000.0 / CTR_FPS_LIMIT) - int(1000 * (time.time() - time_start)), 0)) & 0xFF
        real_fps = 1.0 / max((time.time() - time_start), 1e-4)

        # TODO 此处可自定义按键操作
        if k == ord('q'):
            break
        elif k == ord('r'):
            vision.reset()
        elif k == ord('p'):
            play_video = not play_video

        if play_video:
            ret, img_ = read_video.read()
        else:
            vision.reset()
    cv.destroyAllWindows()
