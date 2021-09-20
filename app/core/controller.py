# -*- coding: utf-8 -*-
__all__ = ["Controller"]


class Controller:
    def __init__(self):
        self.auto_aim = False
        self.action_state = True
        self.gimbal_action = ''
        self.hp = 0
        self.heat = 0
        self.bat = 0
