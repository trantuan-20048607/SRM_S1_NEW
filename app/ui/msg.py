# -*- coding: utf-8 -*-
import cv2 as cv

from app.constants import *
from app.core.msg import *

__all__ = ["Msg2Window"]


class Msg2Window(Msg):
    def __init__(self, img: np.array = cv.transpose(cv.imread("assets/BACK.jpg")),
                 hp: int = 0, heat: int = 0, bat: int = 0, aim_method: str = DEFAULT_AIM_METHOD,
                 target: tuple = (0, 0), terminate: bool = False, err: bool = False):
        super(Msg, self).__init__()

        self.img = img
        self.hp = hp
        self.heat = heat
        self.bat = bat
        self.aim_method = aim_method
        self.target = target
        self.terminate = terminate
        self.err = err
