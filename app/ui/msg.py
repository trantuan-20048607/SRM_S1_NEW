# -*- coding: utf-8 -*-

import cv2 as cv
import numpy as np

from app.config import *
from app.core.msg import *

__all__ = ["Msg2Window"]
_default_img = cv.transpose(cv.imread("assets/BACK.jpg"))


class Msg2Window(Msg):
    def __init__(self,
                 corresponding_id: int = 0,
                 img: np.ndarray = _default_img,
                 hp: int = 0,
                 heat: int = 0,
                 bat: int = 0,
                 speed: tuple = (0, 0),
                 aim_method: str = DEFAULT_AIM_METHOD,
                 aim_target: tuple = (int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2)),
                 fps: tuple = (0.0, 0.0),
                 terminate: bool = False,
                 err: bool = False):
        super(Msg2Window, self).__init__()

        self.corresponding_id = corresponding_id
        self.img = img
        self.hp = hp
        self.heat = heat
        self.bat = bat
        self.speed = speed
        self.aim_method = aim_method
        self.aim_target = aim_target
        self.fps = fps
        self.terminate = terminate
        self.err = err
