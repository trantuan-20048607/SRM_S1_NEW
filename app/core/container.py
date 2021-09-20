# -*- coding: utf-8 -*-
import logging
import time
import app.ui.proc as ui
import app.controller.proc as controller
import multiprocessing as mp

__all__ = ["Container"]


class Container(object):
    COLORS = ["red", "blue"]

    def __init__(self, color: str, debug: bool, record: bool):
        assert color in Container.COLORS
        self.color = color
        self.debug = debug
        self.record = record
        logging.info(self)

    def start(self):
        msg_ui_2_ctr_queue = mp.Queue()
        msg_ctr_2_ui_queue = mp.Queue()
        ctr_proc = mp.Process(target=controller.start,
                              args=(self.color, self.debug, msg_ui_2_ctr_queue,
                                    msg_ctr_2_ui_queue, self.record),
                              name="controller")
        ctr_proc.start()
        logging.info(ctr_proc)
        ui_proc = mp.Process(target=ui.start,
                             args=(self.debug, msg_ctr_2_ui_queue,
                                   msg_ui_2_ctr_queue),
                             name="ui")
        ui_proc.start()
        logging.info(ui_proc)
        ctr_proc.join()
        ui_proc.join()
        msg_ctr_2_ui_queue.close()
        msg_ui_2_ctr_queue.close()
