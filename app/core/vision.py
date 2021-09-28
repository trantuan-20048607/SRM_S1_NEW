# -*- coding: utf-8 -*-
import itertools

import cv2 as cv

from app.constants import *

__all__ = ["feed"]

_kalman = cv.KalmanFilter(4, 2)
_last_pre = _current_pre = _last_mes = _current_mes = np.array([[SCREEN_SIZE[0] * 0.5],
                                                                [SCREEN_SIZE[1] * 0.5]], np.float32)

_d_t = _d2_t = (SCREEN_SIZE[0] * 0.5, SCREEN_SIZE[1] * 0.5)

_direct_target_data = _direct_data_cache = (SCREEN_SIZE[0] * 0.5, SCREEN_SIZE[1] * 0.5)

_roi_enabled = False
_current_tag = DEFAULT_AIM_METHOD


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


def _reset():
    global _roi_enabled
    _roi_enabled = False
    _kalman_reset()
    _tri_reset()


def _roi_cut_img(img: np.array, center: tuple, size: tuple):
    return img[max(int(center[1] - size[1] / 2), 0):min(int(center[1] + size[1] / 2), SCREEN_SIZE[1]),
           max(int(center[0] - size[0] / 2), 0):min(int(center[0] + size[0] / 2), SCREEN_SIZE[0])]


def _ident_tgt(img: np.array, color: str) -> tuple or None:
    assert color in COLOR_LIST

    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img_color = np.zeros(img.shape, dtype=np.uint8)

    if color in HSV_RANGE and type(HSV_RANGE[color]) in (list, tuple):
        if type(HSV_RANGE[color]) == tuple:
            img_color = cv.bitwise_and(
                img, img, mask=cv.inRange(
                    img_hsv, HSV_RANGE[color][0], HSV_RANGE[color][1]))
        else:
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
                weight += a
                center_x += x * a
                center_y += y * a
    if weight > MIN_VALID_TOTAL_AREA:
        return center_x / weight, center_y / weight
    else:
        return None


def _smooth(data: tuple, tag: str):
    assert tag in AUTO_AIM_METHOD_LIST

    _update_kalman(data)
    _update_triangular_feedback(data)
    """
    if tag == "kalman":
        _update_kalman(data)
    elif tag == "tri":
        _update_triangular_feedback(data)
    """


def _get_target_position(tag: str):
    assert tag in AUTO_AIM_METHOD_LIST

    global _direct_data_cache
    if tag == "kalman":
        return int(_current_pre[0][0]), int(_current_pre[1][0])
    elif tag == "tri":
        return int(_d_t[0]), int(_d_t[1])
    elif tag == "direct":
        if _direct_target_data:
            _direct_data_cache = _direct_target_data
            return int(_direct_target_data[0]), int(_direct_target_data[1])
        else:
            return int(_direct_data_cache[0]), int(_direct_data_cache[1])


def _triangular_weight(max_len: int or float):
    for i in range(len(TRIANGULAR_SIDE_LEN_LEVEL)):
        if max_len < TRIANGULAR_SIDE_LEN_LEVEL[i]:
            return TRIANGULAR_DIFFERENCE_WEIGHT[i]
    return TRIANGULAR_DIFFERENCE_WEIGHT[-1]


def _update_triangular_feedback(data: tuple):
    global _d_t, _d2_t

    points = (np.array(data), np.array(_d_t), np.array(_d2_t))
    sides = tuple(x - y for x, y in itertools.combinations(points, 2))
    side_len = tuple(np.linalg.norm(s) for s in sides)
    weight = _triangular_weight(max(side_len))

    g_center_x, g_center_y = weight[0] * points[0] + weight[1] * points[1] + weight[2] * points[2]

    weight = weight[0] + weight[1] + weight[2]
    _d2_t = _d_t
    _d_t = (g_center_x / weight, g_center_y / weight)


def _update_kalman(data: tuple):
    global _last_pre, _current_pre, _last_mes, _current_mes
    _last_pre = _current_pre
    _last_mes = _current_mes

    _current_mes = np.array([[data[0]], [data[1]]], np.float32)

    _kalman.correct(_current_mes)
    _current_pre = _kalman.predict()


def feed(img: np.array, color: str, tag: str = AIM_METHOD_SELECT_LIST[DEFAULT_AIM_METHOD]):
    assert tag in AUTO_AIM_METHOD_LIST
    assert color in COLOR_LIST

    global _roi_enabled, _last_pre, _last_mes, _current_pre, _current_mes, _direct_target_data, _current_tag

    if tag != _current_tag:
        # _reset()
        _current_tag = tag

    if not _roi_enabled:
        _direct_target_data = _ident_tgt(img, color)

        if _direct_target_data:
            _roi_enabled = True

            _smooth(_direct_target_data, tag)

            return _get_target_position(tag)

        else:
            return _get_target_position(tag)
    else:
        last_x, last_y = _get_target_position(tag)

        _direct_target_data = _ident_tgt(_roi_cut_img(img, (last_x, last_y), ROI_SIZE), color)

        if _direct_target_data:
            _direct_target_data = (_direct_target_data[0] - ROI_SIZE[0] * 0.5 + last_x,
                                   _direct_target_data[1] - ROI_SIZE[1] * 0.5 + last_y)

            _smooth(_direct_target_data, tag)

            return _get_target_position(tag)

        else:
            _roi_enabled = False

            return _get_target_position(tag)
