# -*- coding: utf-8 -*-
from app.core.msg import *
from app import constants

__all__ = ["Msg2Controller"]


class Msg2Controller(Msg):
    def __init__(self, speed: tuple = (0, 0), cur_delta: tuple = (0, 0),
                 aim_method: str = constants.DEFAULT_AIM_METHOD, fire: bool = False, terminate: bool = False):
        super(Msg2Controller, self).__init__()

        assert aim_method in ("manual", "kalman", "tri")

        self.speed = speed
        self.cur_delta = cur_delta
        self.aim_method = aim_method
        self.fire = fire
        self.terminate = terminate
