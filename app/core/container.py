# -*- coding: utf-8 -*-
import multiprocessing as mp

import app.controller.proc as controller
import app.ui.proc as ui
from app.constants import *

__all__ = ["Container"]


class Container(object):
    def __init__(self, color: str, debug: bool):
        assert color in COLOR_LIST

        self.color = color
        self.debug = debug

    def start(self):
        msg_ui_2_ctr_queue = mp.Queue()
        msg_ctr_2_ui_queue = mp.Queue()
        ui_proc = mp.Process(target=ui.start,
                             args=(self.color, self.debug, msg_ctr_2_ui_queue,
                                   msg_ui_2_ctr_queue),
                             name="ui")
        ctr_proc = mp.Process(target=controller.start,
                              args=(self.color, self.debug, msg_ui_2_ctr_queue,
                                    msg_ctr_2_ui_queue),
                              name="controller")
        ui_proc.start()
        ctr_proc.start()
        ctr_proc.join()
        ui_proc.join()
        msg_ctr_2_ui_queue.close()
        msg_ui_2_ctr_queue.close()
