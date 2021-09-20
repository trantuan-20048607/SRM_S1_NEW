# -*- coding: utf-8 -*-
import numpy as np
import cv2 as cv
import math
from app.constants import *

__all__ = ["find_target"]
ROI_SIZE = (324, 324)
__last_target = (int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2))
__roi_enabled = False


def roi_img(img: np.array, size: tuple):
    global __last_target
    return img[max(int(__last_target[1] - size[1] / 2), 0):min(int(__last_target[1] + size[1] / 2), SCREEN_SIZE[1]),
           max(int(__last_target[0] - size[0] / 2), 0):min(int(__last_target[0] + size[0] / 2), SCREEN_SIZE[0])]


def find_target(img: np.array, debug: bool, color: str):
    global __roi_enabled, __last_target
    if not __roi_enabled:
        pos = armor(img, debug, color)
        if pos is None:
            return __last_target
        else:
            __last_target = pos
            __roi_enabled = True
            return pos
    else:
        pos = armor(roi_img(img, ROI_SIZE), debug, color)
        if pos is None:
            __roi_enabled = False
            return __last_target
        else:
            pos = (pos[0] - int(ROI_SIZE[0] / 2) + __last_target[0],
                   pos[1] - int(ROI_SIZE[1] / 2) + __last_target[1])
            d = math.sqrt((__last_target[0] - pos[0]) * (__last_target[0] - pos[0]) +
                          (__last_target[1] - pos[1]) * (__last_target[1] - pos[1]))
            if d < 24:
                pos = (
                    int((d * pos[0] + (24 - d) * __last_target[0]) / 24),
                    int((d * pos[1] + (24 - d) * __last_target[1]) / 24))
            __last_target = pos
            return pos


def armor(img: np.array, debug: bool, color: str):
    global __last_target, __roi_enabled
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    if color == "red":
        img_color = cv.bitwise_and(
            img, img, mask=cv.inRange(img_hsv, np.array([90, 112, 102]), np.array([100, 255, 255])))
    elif color == "blue":
        img_color = cv.add(
            cv.bitwise_and(
                img, img, mask=cv.inRange(img_hsv,
                                          np.array([176, 112, 102]),
                                          np.array([180, 255, 255]))),
            cv.bitwise_and(
                img, img, mask=cv.inRange(img_hsv,
                                          np.array([0, 112, 102]),
                                          np.array([8, 255, 255])))
        )
    cv.medianBlur(img_color, 3, img_color)
    _, binary = cv.threshold(cv.cvtColor(img_color, cv.COLOR_BGR2GRAY), 16, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    center, weight = [0, 0], 0.0
    if contours:
        for i, contour in enumerate(contours):
            x, y, w, h = cv.boundingRect(contour)
            a = w * h
            if a > 16:
                weight += a
                center[0] += x * a
                center[1] += y * a
                cv.rectangle(img_color, (x, y), (x + w, y + h), (182, 89, 155), 2)

    if debug:
        cv.imshow("DEBUG", img_color)
        cv.waitKey(2)
    if weight > 18:
        return int(center[0] / weight), int(center[1] / weight)
    else:
        return None
