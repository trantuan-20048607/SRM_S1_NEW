# -*- coding: utf-8 -*-
import itertools
import logging
import math

import cv2 as cv

from app.constants import *

__all__ = ["feed", "reset", "modify_hsv_range"]

_kalman = cv.KalmanFilter(4, 2)
_last_pre = _current_pre = _last_mes = _current_mes = np.array([[SCREEN_SIZE[0] * 0.5],
                                                                [SCREEN_SIZE[1] * 0.5]], np.float32)

_d_t = _d2_t = (SCREEN_SIZE[0] * 0.5, SCREEN_SIZE[1] * 0.5)

_direct_target_data = _direct_data_cache = (SCREEN_SIZE[0] * 0.5, SCREEN_SIZE[1] * 0.5)
_target_weight = 0.0

_roi_enabled = False
_current_type = DEFAULT_AIM_METHOD


def modify_hsv_range(color: str, i: int, j: int, k: int, x: int):
    if HSV_RANGE[color][i][j][k] != x:
        HSV_RANGE[color][i][j][k] = x
        logging.debug(f"HSV {i} {j} {k} {x}")


def _kalman_reset():
    global _kalman, _last_pre, _last_mes, _current_pre, _current_mes

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
    _current_mes = _current_pre = _last_mes = _last_pre = np.array([[SCREEN_SIZE[0] * 0.5],
                                                                    [SCREEN_SIZE[1] * 0.5]], np.float32)


def _tri_reset():
    global _d_t, _d2_t

    _d_t = _d2_t = (SCREEN_SIZE[0] * 0.5, SCREEN_SIZE[1] * 0.5)


def reset():
    global _roi_enabled

    _roi_enabled = False
    _kalman_reset()
    _tri_reset()
    logging.debug("AUTO AIM RESET")


def _roi_cut_img(img, center, size):
    logging.debug(f"ROI {size[0]}x{size[1]}")
    return img[max(int(center[1] - size[1] * 0.5), 0):min(int(center[1] + size[1] * 0.5), SCREEN_SIZE[1]),
           max(int(center[0] - size[0] * 0.5), 0):min(int(center[0] + size[0] * 0.5), SCREEN_SIZE[0])]


def _ident_tgt(img, color):
    global _target_weight

    assert color in COLOR_LIST

    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img_color = np.zeros(img.shape, dtype=np.uint8)
    if color in HSV_RANGE:
        for lower, upper in HSV_RANGE[color]:
            img_color = cv.add(img_color, cv.bitwise_and(
                img, img, mask=cv.inRange(img_hsv, lower, upper)))
    else:
        img_color = img_hsv
    cv.medianBlur(img_color, 3, img_color)
    _, binary = cv.threshold(cv.cvtColor(img_color, cv.COLOR_BGR2GRAY), GRAY_THRESH, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    center_x, center_y, weight = 0.0, 0.0, 0.0
    if contours:
        for i, contour in enumerate(contours):
            x, y, w, h = cv.boundingRect(contour)
            a = w * h
            if a > MIN_RECT_AREA:
                cv.rectangle(img, (x, y), (x + w, y + h), UI_COLOR_NOTICE, 2)
                cv.putText(img, "%d" % a, (x, y), cv.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255))
                weight += a
                center_x += (x + w * 0.5) * a
                center_y += (y + h * 0.5) * a
    if weight > MIN_VALID_TOTAL_AREA:
        _target_weight = weight
        if img.shape[0] < SCREEN_SIZE[1] and img.shape[1] < SCREEN_SIZE[0]:
            cv.putText(img, "%d %.2f%%" % (weight, 100 * weight / (img.shape[0] * img.shape[1])),
                       (0, img.shape[0] - 2), cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
        return center_x / weight, center_y / weight
    else:
        return None


def _smooth(data, type_):
    assert type_ in AUTO_AIM_METHOD_LIST

    if type_ == "kalman":
        _update_kalman(data)
    elif type_ == "tri":
        _update_triangular_feedback(data)


def _get_target_position(type_):
    assert type_ in AUTO_AIM_METHOD_LIST

    global _direct_data_cache

    if type_ == "kalman":
        return int(_current_pre[0][0]), int(_current_pre[1][0])
    elif type_ == "tri":
        return int(_d_t[0]), int(_d_t[1])
    elif type_ == "direct":
        if _direct_target_data:
            _direct_data_cache = _direct_target_data
            return int(_direct_target_data[0]), int(_direct_target_data[1])
        else:
            return int(_direct_data_cache[0]), int(_direct_data_cache[1])


def _triangular_weight(len_):
    for i in range(len(TRIANGULAR_SIDE_LEN_LEVEL)):
        if len_ < TRIANGULAR_SIDE_LEN_LEVEL[i]:
            return TRIANGULAR_DIFFERENCE_WEIGHT[i]
    return TRIANGULAR_DIFFERENCE_WEIGHT[-1]


def _update_triangular_feedback(data):
    global _d_t, _d2_t

    points = (np.array(data), np.array(_d_t), np.array(_d2_t))
    sides = tuple(x - y for x, y in itertools.combinations(points, 2))
    side_len = tuple(np.linalg.norm(s) for s in sides)
    weight = _triangular_weight(max(side_len))
    g_center_x, g_center_y = weight[0] * points[0] + weight[1] * points[1] + weight[2] * points[2]
    weight = weight[0] + weight[1] + weight[2]
    _d2_t = _d_t
    _d_t = (g_center_x / weight, g_center_y / weight)


def _update_kalman(data):
    global _last_pre, _current_pre, _last_mes, _current_mes

    _last_pre = _current_pre
    _last_mes = _current_mes
    _current_mes = np.array([[data[0]], [data[1]]], np.float32)
    _kalman.correct(_current_mes)
    _current_pre = _kalman.predict()


def feed(img: np.ndarray, color: str, type_: str = AIM_METHOD_SELECT_LIST[DEFAULT_AIM_METHOD]) -> (int, int):
    assert type_ in AUTO_AIM_METHOD_LIST
    assert img.shape == (SCREEN_SIZE[1], SCREEN_SIZE[0], 3)
    assert color in COLOR_LIST

    global _roi_enabled, _last_pre, _last_mes, _current_pre, _current_mes, _direct_target_data, _current_type

    if type_ != _current_type:
        reset()
        _current_type = type_
    last_x, last_y = _get_target_position(type_)
    if last_x > SCREEN_SIZE[0] or last_y > SCREEN_SIZE[1] or \
            last_x < 0 or last_y < 0:
        reset()
    elif last_x > SCREEN_SIZE[0] - ROI_LIMIT or last_y > SCREEN_SIZE[1] - ROI_LIMIT or \
            last_x < ROI_LIMIT or last_y < ROI_LIMIT:
        _roi_enabled = False
        logging.debug("ROI DISABLED")

    if not _roi_enabled:
        _direct_target_data = _ident_tgt(img, color)
        if _direct_target_data:
            _roi_enabled = True
            logging.debug("ROI ENABLED")
            _smooth(_direct_target_data, type_)
            return _get_target_position(type_)
        else:
            return _get_target_position(type_)
    else:
        roi_size = math.sqrt(_target_weight * 32)
        logging.debug("ROI SIZE %.2fx%.2f" % (roi_size, roi_size))
        _direct_target_data = _ident_tgt(_roi_cut_img(img, (last_x, last_y), (int(roi_size), int(roi_size))), color)
        if _direct_target_data:
            _direct_target_data = (_direct_target_data[0] - roi_size * 0.5 + last_x,
                                   _direct_target_data[1] - roi_size * 0.5 + last_y)
            _smooth(_direct_target_data, type_)
            cv.rectangle(img, (int(last_x - roi_size * 0.5), int(last_y - roi_size * 0.5)),
                         (int(last_x + roi_size * 0.5), int(last_y + roi_size * 0.5)), UI_COLOR_NOTICE, 2)
            return _get_target_position(type_)
        else:
            _roi_enabled = False
            logging.debug("ROI DISABLED")
            return _get_target_position(type_)
