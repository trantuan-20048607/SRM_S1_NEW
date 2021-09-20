# -*- coding: utf-8 -*-
import numpy as np
import cv2 as cv
import math

__all__ = ["armor"]
__last_target = [640, 480]


def armor(img: np.array, debug: bool, color: str):
    global __last_target
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img_color = cv.bitwise_and(
        img, img, mask=cv.inRange(
            img_hsv, np.array([90, 132, 144]), np.array([100, 255, 255])))
    _, binary = cv.threshold(cv.cvtColor(img_color, cv.COLOR_BGR2GRAY), 128, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    center, weight = [0, 0], 0.0
    if contours:
        for i, contour in enumerate(contours):
            x, y, w, h = cv.boundingRect(contour)
            sq_a = math.sqrt(w * h)
            weight += sq_a
            center[0] += x * sq_a
            center[1] += y * sq_a
    if weight > 24:
        center[0] = int(center[0] / weight)
        center[1] = int(center[1] / weight)
        d = math.sqrt((__last_target[0] - center[0]) * (__last_target[0] - center[0]) +
                      (__last_target[1] - center[1]) * (__last_target[1] - center[1]))
        if d < 8:
            center = [int((center[0] + __last_target[0]) / 2), int((center[1] + __last_target[1]) / 2)]
        __last_target = center
        return center[0], center[1]
    else:
        return __last_target
