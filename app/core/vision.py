# -*- coding: utf-8 -*-
import numpy as np
import cv2 as cv
import itertools
import math
from app.constants import *

__all__ = ["feed"]

ROI_SIZE = (324, 324)

# CONTROL VALUES FOR KARLAN FILTER, SMALLER IS BEST
KALMAN_SHAKE_CONTROL = 1e-3
KALMAN_DELAY_CONTROL = 1e-1

# WEIGHTS FOR TRIANGULAR FEEDBACK
TRIANGULAR_DIFFERENCE_WEIGHT = (1, 3, 2)

# ANGLE THRESHOLD FOR TRIANGULAR FEEDBACK
TRIANGULAR_MIN_ANGLE = 0

# SIDE LEN THRESHOLD FOR TRIANGULAR FEEDBACK
TRIANGULAR_MAX_SIDE_LEN = 32

# DATA FOR KALMAN FILTER
_kalman = cv.KalmanFilter(4, 2)
_kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                      [0, 1, 0, 0]], np.float32)
_kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                     [0, 1, 0, 1],
                                     [0, 0, 1, 0],
                                     [0, 0, 0, 1]], np.float32)
_kalman.processNoiseCov = np.array([[1, 0, 0, 0],
                                    [0, 1, 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]], np.float32) * KALMAN_SHAKE_CONTROL
_kalman.measurementNoiseCov = np.array([[1, 0],
                                        [0, 1]], np.float32) * KALMAN_DELAY_CONTROL
_last_pre = _current_pre = np.array([[SCREEN_SIZE[0] * 0.5],
                                     [SCREEN_SIZE[1] * 0.5]], np.float32)
_last_mes = _current_mes = np.array([[SCREEN_SIZE[0] * 0.5],
                                     [SCREEN_SIZE[1] * 0.5]], np.float32)

# DATA FOR TRIANGULAR FEEDBACK
_d_t = (SCREEN_SIZE[0] * 0.5, SCREEN_SIZE[1] * 0.5)
_d2_t = (SCREEN_SIZE[0] * 0.5, SCREEN_SIZE[1] * 0.5)

_roi_enabled = False


def _roi_cut_img(img: np.array, center: tuple, size: tuple):
    return img[max(int(center[1] - size[1] / 2), 0):min(int(center[1] + size[1] / 2), SCREEN_SIZE[1]),
           max(int(center[0] - size[0] / 2), 0):min(int(center[0] + size[0] / 2), SCREEN_SIZE[0])]


def _ident_tgt(img: np.array, debug: bool, color: str) -> tuple or None:
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    if color == "red":
        img_color = cv.bitwise_and(
            img, img, mask=cv.inRange(
                img_hsv, np.array([90, 112, 102]), np.array([100, 255, 255])))
    elif color == "blue":
        img_color = cv.add(
            cv.bitwise_and(
                img, img, mask=cv.inRange(
                    img_hsv, np.array([176, 112, 102]), np.array([180, 255, 255]))),
            cv.bitwise_and(
                img, img, mask=cv.inRange(
                    img_hsv, np.array([0, 112, 102]), np.array([8, 255, 255]))))
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

    if weight > 18:
        return center[0] / weight, center[1] / weight
    else:
        return None


def _smooth(data: tuple, debug: bool):
    _update_triangular_feedback(data, debug)
    _update_kalman(data, debug)


def _get_target_position(tag: str, debug: bool):
    if tag == "kalman":
        return int(_current_pre[0][0]), int(_current_pre[1][0])
    elif tag == "tri":
        return int(_d_t[0]), int(_d_t[1])


def _update_triangular_feedback(data: tuple, debug: bool):
    global _d_t, _d2_t
    points = (np.array(data), np.array(_d_t), np.array(_d2_t))
    sides = tuple(x - y for x, y in itertools.combinations(points, 2))
    if abs(np.cross(sides[0], sides[1])) < 1e-2 \
            or abs(np.cross(sides[2], sides[1])) < 1e-2 \
            or abs(np.cross(sides[0], sides[2])) < 1e-2:
        _d2_t = _d_t
        _d_t = data
        return
    side_len = tuple(np.linalg.norm(s) for s in sides)
    if abs(side_len[0]) < 1e-2 or abs(side_len[1]) < 1e-2 or abs(side_len[2]) < 1e-2 \
            or max(side_len) > TRIANGULAR_MAX_SIDE_LEN:
        _d2_t = _d_t
        _d_t = data
        return
    angles = (math.acos((side_len[0] * side_len[0] + side_len[1] * side_len[1] -
                         side_len[2] * side_len[2]) / (2 * side_len[0] * side_len[1])),
              math.acos((side_len[0] * side_len[0] + side_len[2] * side_len[2] -
                         side_len[1] * side_len[1]) / (2 * side_len[0] * side_len[2])),
              math.acos((side_len[2] * side_len[2] + side_len[1] * side_len[1] -
                         side_len[0] * side_len[0]) / (2 * side_len[2] * side_len[1]))
              )
    if min(angles) * 180 / math.pi < TRIANGULAR_MIN_ANGLE:
        _d2_t = _d_t
        _d_t = data
    else:
        g_center = TRIANGULAR_DIFFERENCE_WEIGHT[0] * points[0] + \
                   TRIANGULAR_DIFFERENCE_WEIGHT[1] * points[1] + \
                   TRIANGULAR_DIFFERENCE_WEIGHT[2] * points[2]

        weight = TRIANGULAR_DIFFERENCE_WEIGHT[0] + TRIANGULAR_DIFFERENCE_WEIGHT[1] + TRIANGULAR_DIFFERENCE_WEIGHT[2]
        _d2_t = _d_t
        _d_t = (g_center[0] / weight, g_center[1] / weight)


def _update_kalman(data: tuple, debug: bool):
    global _last_pre, _current_pre, _last_mes, _current_mes
    _last_pre = _current_pre
    _last_mes = _current_mes
    _current_mes = np.array([[data[0]], [data[1]]], np.float32)
    _kalman.correct(_current_mes)
    _current_pre = _kalman.predict()


def feed(img: np.array, debug: bool, color: str, tag=AIM_METHOD_LIST[DEFAULT_AIM_METHOD]):
    assert tag in ("kalman", "tri")
    global _roi_enabled, _last_pre, _last_mes, _current_pre, _current_mes
    if not _roi_enabled:
        tgt = _ident_tgt(img, debug, color)
        if tgt:
            _roi_enabled = True
            _smooth(tgt, debug)
            return _get_target_position(tag, debug)
        else:
            return _get_target_position(tag, debug)
    else:
        tgt = _ident_tgt(_roi_cut_img(img, (_last_pre[0][0], _last_pre[1][0]), ROI_SIZE), debug, color)
        if tgt:
            tgt = (tgt[0] - ROI_SIZE[0] * 0.5 + _last_pre[0][0],
                   tgt[1] - ROI_SIZE[1] * 0.5 + _last_pre[1][0])
            _smooth(tgt, debug)
            return _get_target_position(tag, debug)
        else:
            _roi_enabled = False
            return _get_target_position(tag, debug)
