# -*- coding: utf-8 -*-

from app.constants import *

__all__ = ["feed", "reset"]


def reset():
    # 此处填写重置 ROI、滤波器操作
    pass


def feed(img: np.ndarray, color: str, type_: str = AIM_METHOD_SELECT_LIST[DEFAULT_AIM_METHOD]) -> (int, int):
    # 此处填写主处理部分
    pass
