# -*- coding: utf-8 -*-
from app.core.msg import *
import multiprocessing as mp

__all__ = ["Msg2Controller"]


class Msg2Controller(Msg):
    def __init__(self, speed: tuple = (0, 0), cur_delta: tuple = (0, 0),
                 auto_aim=None, fire: bool = False, terminate: bool = False):
        super(Msg2Controller, self).__init__()
        assert auto_aim in (True, False, None)
        self.speed = speed
        self.cur_delta = cur_delta
        self.auto_aim = auto_aim
        self.fire = fire
        self.terminate = terminate
