# -*- coding: utf-8 -*-
from app.constants import *

__all__ = ["Controller"]


class Controller:
    def __init__(self):
        self.aim_method = DEFAULT_AIM_METHOD
        self.action_state = True
        self.gimbal_action = ''
        self.hp = 0
        self.heat = 0
        self.bat = 0
        self.hit_times, self.last_hit_times = 0, 0
