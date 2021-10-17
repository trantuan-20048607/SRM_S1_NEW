# -*- coding: utf-8 -*-

import cv2 as cv

import app.core.vision as vision
from app.constants import *


def start(color: str):
    read_video, play_video = cv.VideoCapture(f"assets/s1{color}.avi"), True

    # 此处填写测试环境预处理代码

    while True:
        if play_video:
            ret, img = read_video.read()
            if ret:
                # 目标位置
                tgt = vision.feed(img, color)

                # 窗口
                cv.imshow("VISION MODULE TEST", img)

        # 此处填写对每一帧执行的测试代码

        k = cv.waitKey(int(1000.0 / CTR_FPS_LIMIT)) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('r'):
            vision.reset()
        elif k == ord('p'):
            play_video = not play_video
    cv.destroyAllWindows()
