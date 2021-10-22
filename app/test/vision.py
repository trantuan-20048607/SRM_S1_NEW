# -*- coding: utf-8 -*-

import time

import cv2 as cv

import app.core.vision as vision
from app.config import *


def start(color: str):
    read_video, play_video = cv.VideoCapture(f"assets/s1{color}.avi"), True
    ret, img = read_video.read()

    # 初始化数值
    max_fps, real_fps, cost = 0.0, 0.0, 0.0

    def blank(x: int):
        pass

    for i in range(len(HSV_RANGE[color])):
        cv.namedWindow(f"HSV {i}", cv.WINDOW_NORMAL)
        for j in range(3):
            c = ["H", "S", "V"][j]
            cv.createTrackbar(f"MIN {c}", f"HSV {i}", HSV_RANGE[color][i][0][j],
                              180 if j == 0 else 255, blank)
            cv.createTrackbar(f"MAX {c}", f"HSV {i}", HSV_RANGE[color][i][1][j],
                              180 if j == 0 else 255, blank)

    while ret:
        time_start = time.time()

        # 目标位置
        if play_video:
            _ = vision.feed(img, color)

            # 显示 FPS
            cv.putText(img, "FPS %d/%d" % (int(real_fps), int(max_fps)) if
            max_fps < 1e4 else "FPS %d/INF" % int(real_fps),
                       (0, 24), cv.FONT_HERSHEY_SIMPLEX,
                       0.85, (0, 192, 0), 2)

            # 显示时间开销
            cv.putText(img, "COST %.5f" % cost,
                       (0, 48), cv.FONT_HERSHEY_SIMPLEX,
                       0.85, (0, 192, 0), 2)

        # 窗口生成
        cv.imshow("VISION MODULE TEST", img)

        for i in range(len(HSV_RANGE[color])):
            for j in range(3):
                c = ["H", "S", "V"][j]
                vision.modify_hsv_range(color, i, 0, j, cv.getTrackbarPos(f"MIN {c}", f"HSV {i}"))
                vision.modify_hsv_range(color, i, 1, j, cv.getTrackbarPos(f"MAX {c}", f"HSV {i}"))

        cost = time.time() - time_start
        max_fps = 1.0 / max((time.time() - time_start), 1e-4)
        k = cv.waitKey(max(int(1000.0 / CTR_FPS_LIMIT) - int(1000 * (time.time() - time_start)), 1)) & 0xFF
        real_fps = 1.0 / max((time.time() - time_start), 1e-4)
        if k == ord('q'):
            break
        elif k == ord('r'):
            vision.reset()
        elif k == ord('p'):
            play_video = not play_video

        if play_video:
            ret, img = read_video.read()
    cv.destroyAllWindows()
