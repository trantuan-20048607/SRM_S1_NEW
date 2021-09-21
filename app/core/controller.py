# -*- coding: utf-8 -*-
from app import constants

__all__ = ["Controller"]


class Controller:
    def __init__(self):
        self.aim_method = constants.DEFAULT_AIM_METHOD
        self.action_state = True
        self.gimbal_action = ''
        self.hp = 0
        self.heat = 0
        self.bat = 0
