# -*- coding: utf-8 -*-
import multiprocessing as mp
import cv2 as cv
import pygame
import logging
from pygame.locals import *
from app.controller.main import *
from app.ui.msg import *
from app.controller.msg import *

__all__ = ["Window"]


class Window(object):
    SPEED_MAP = {
        K_a: (0, -1), K_d: (0, 1), K_w: (1, 0), K_s: (-1, 0)
    }
    SCREEN_SIZE = (1280, 720)

    def __init__(self, debug: bool):
        pygame.init()
        pygame.event.set_allowed([MOUSEBUTTONDOWN, KEYUP, KEYDOWN])
        pygame.display.set_caption("SRM 校内赛")
        pygame.mouse.set_visible(debug)
        pygame.event.set_grab(True)

        self.debug = debug
        self.screen = pygame.display.set_mode(Window.SCREEN_SIZE, flags=pygame.DOUBLEBUF)
        self.limit = True
        self.speed = (0, 0)
        self.fire_show_delay = 0
        self.ctr_error = True

        logging.debug(self)

    def update(self, msg: Msg2Window, ui_queue_size: int, ctr_queue_size: int):
        pygame.surfarray.blit_array(self.screen, cv.cvtColor(msg.img, cv.COLOR_BGR2RGB))
        if msg.err:
            self.screen.blit(pygame.font.Font(
                "assets/DX_BOLD.ttf", 70).render("控制器出错", True, (160, 20, 10)), (465, 290))
            self.screen.blit(pygame.font.Font(
                "assets/DX_BOLD.ttf", 50).render("程序将自动退出", True, (160, 20, 10)), (465, 360))
            self.ctr_error = False
        else:
            ft = pygame.font.Font("assets/DX_BOLD.ttf", 30)
            if msg.hp * 3 > S1Controller.INITIAL_HP:
                self.screen.blit(ft.render(f"HP: {msg.hp} / {S1Controller.INITIAL_HP}",
                                           True, (10, 180, 10)), (100, 50))
            else:
                self.screen.blit(ft.render(f"HP: {msg.hp} / {S1Controller.INITIAL_HP}",
                                           True, (160, 20, 10)), (100, 50))
            if msg.heat > S1Controller.MAX_HEAT:
                self.screen.blit(ft.render("热量超限", True, (160, 20, 10)), (100, 100))
            elif msg.heat > S1Controller.MAX_HEAT * 0.8:
                self.screen.blit(ft.render(f"CAL: {msg.heat} / {S1Controller.MAX_HEAT}",
                                           True, (160, 20, 10)), (100, 100))
            elif msg.heat > S1Controller.MAX_HEAT * 0.6:
                self.screen.blit(ft.render(f"CAL: {msg.heat} / {S1Controller.MAX_HEAT}",
                                           True, (250, 150, 50)), (100, 100))
            else:
                self.screen.blit(ft.render(f"CAL: {msg.heat} / {S1Controller.MAX_HEAT}",
                                           True, (10, 180, 10)), (100, 100))

            if msg.auto_aim:
                self.screen.blit(ft.render("自动瞄准", True, (10, 180, 10)), (100, 250))
            else:
                self.screen.blit(ft.render("手动瞄准", True, (250, 150, 50)), (100, 250))
            if ui_queue_size > 2:
                self.screen.blit(ft.render("显示延迟", True, (160, 20, 10)), (100, 150))
            if ctr_queue_size > 2:
                self.screen.blit(ft.render("操作延迟", True, (160, 20, 10)), (100, 200))
            if pygame.mouse.get_pos() != (640, 360):
                self.screen.blit(ft.render("瞄准", True, (160, 20, 10)), (160, 300))
            if self.fire_show_delay > 0:
                self.screen.blit(ft.render("开火", True, (160, 20, 10)), (220, 300))
                self.fire_show_delay -= 1
            if not self.debug:
                self.screen.blit(ft.render(f"BAT: {msg.bat}", True, (10, 255, 10)), (800, 80))
            if self.speed[0] or self.speed[1]:
                self.screen.blit(ft.render("移动", True, (160, 20, 10)), (100, 300))
        pygame.display.flip()

    def feedback(self, out_queue: mp.Queue):
        for event in pygame.event.get():
            speed, auto_aim = self.speed, None
            term, cur_delta = event.type == QUIT, (0, 0)

            if event.type == KEYDOWN and event.key in Window.SPEED_MAP:
                speed = (speed[0] + Window.SPEED_MAP[event.key][0], speed[1] + Window.SPEED_MAP[event.key][1])
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    term = True
                if event.key in (K_q, K_e):
                    auto_aim = {K_q: True, K_e: False}[event.key]
            elif event.type == KEYUP and event.key in Window.SPEED_MAP:
                speed = (speed[0] - Window.SPEED_MAP[event.key][0], speed[1] - Window.SPEED_MAP[event.key][1])
            elif not self.limit:
                cur_current = pygame.mouse.get_pos()
                if cur_current != (640, 360):
                    cur_delta = (cur_current[0] - 640, cur_current[1] - 360)
                    pygame.mouse.set_pos(640, 360)

            if not out_queue.full():
                if not self.limit or event.type == MOUSEBUTTONDOWN or self.speed != speed or term:
                    if event.type == MOUSEBUTTONDOWN:
                        self.fire_show_delay = 10
                    out_queue.put(Msg2Controller(speed=speed, cur_delta=cur_delta, auto_aim=auto_aim,
                                                 fire=event.type == MOUSEBUTTONDOWN, terminate=term))
                    self.speed = speed
                self.limit = not self.limit
            else:
                logging.warning("CTR MSG QUEUE FULL")
