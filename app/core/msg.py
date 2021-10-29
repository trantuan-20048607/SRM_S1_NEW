# -*- coding: utf-8 -*-

import time

__all__ = ["Msg"]


class Msg(object):
    total_count = 0

    def __init__(self):
        self.time = time.time()
        Msg.total_count += 1
        self.id = Msg.total_count
