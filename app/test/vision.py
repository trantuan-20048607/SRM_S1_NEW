# -*- coding: utf-8 -*-

import cv2 as cv

import app.core.vision as vision
from app.constants import *


def start(color: str):
    read_video, play_video = cv.VideoCapture(f"assets/s1{color}.avi"), True

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
    while True:
        if play_video:
            ret, img = read_video.read()
            if ret:
                _ = vision.feed(img, color)
                cv.imshow("VISION MODULE TEST", img)

        for i in range(len(HSV_RANGE[color])):
            for j in range(3):
                c = ["H", "S", "V"][j]
                vision.modify_hsv_range(color, i, 0, j, cv.getTrackbarPos(f"MIN {c}", f"HSV {i}"))
                vision.modify_hsv_range(color, i, 1, j, cv.getTrackbarPos(f"MAX {c}", f"HSV {i}"))

        k = cv.waitKey(int(1000.0 / CTR_FPS_LIMIT)) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('r'):
            vision.reset()
        elif k == ord('p'):
            play_video = not play_video
    cv.destroyAllWindows()
