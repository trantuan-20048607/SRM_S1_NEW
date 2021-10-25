# -*- coding: utf-8 -*-

from app.config import *
from app.core.msg import *

__all__ = ["Msg2Controller"]


class Msg2Controller(Msg):
    def __init__(self, speed: tuple = (0, 0),
                 cur_delta: tuple = (0, 0),
                 aim_method: str = DEFAULT_AIM_METHOD,
                 fire: bool = False,
                 reset_auto_aim: bool = False,
                 terminate: bool = False):
        super(Msg2Controller, self).__init__()

        assert aim_method in AIM_METHOD_SELECT_LIST

        self.speed = speed
        self.cur_delta = cur_delta
        self.aim_method = aim_method
        self.fire = fire
        self.reset_auto_aim = reset_auto_aim
        self.terminate = terminate
