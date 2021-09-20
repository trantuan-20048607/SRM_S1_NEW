# -*- coding: utf-8 -*-
from app.core.msg import *
import cv2 as cv
import numpy as np

__all__ = ["Msg2Window"]


class Msg2Window(Msg):
    def __init__(self, img: np.array = cv.transpose(cv.imread("assets/BACK.jpg")),
                 hp: int = 0, heat: int = 0, bat: int = 0, auto_aim: bool = False,
                 terminate: bool = False, err: bool = False):
        super(Msg, self).__init__()
        self.img = img
        self.hp = hp
        self.heat = heat
        self.bat = bat
        self.auto_aim = auto_aim
        self.terminate = terminate
        self.err = err
