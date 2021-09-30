# -*- coding: utf-8 -*-
import logging
import multiprocessing as mp

import cv2 as cv
import pygame
from pygame.locals import *

from app.constants import *
from app.controller.const import S1Robot
from app.controller.msg import *
from app.ui.msg import *

__all__ = ["Window"]


class Window(object):
    SPEED_MAP = {
        K_a: (0, -1), K_d: (0, 1), K_w: (1, 0), K_s: (-1, 0)
    }

    def __init__(self, debug: bool):

        pygame.init()
        pygame.event.set_allowed([MOUSEBUTTONDOWN, KEYUP, KEYDOWN])
        pygame.event.set_blocked(MOUSEMOTION)
        pygame.display.set_caption("SRM 校内赛")
        pygame.mouse.set_visible(debug)
        pygame.event.set_grab(True)

        self.debug = debug
        self.screen = pygame.display.set_mode(SCREEN_SIZE, flags=pygame.DOUBLEBUF)
        self.speed = (0, 0)
        self.fire_show_delay = 0
        self.aim_method = DEFAULT_AIM_METHOD

        logging.debug(self)

    def update(self, msg: Msg2Window, ui_queue_size: int, ctr_queue_size: int, record: bool):
        pygame.surfarray.blit_array(self.screen, cv.cvtColor(msg.img, cv.COLOR_BGR2RGB))

        if msg.err:
            self.screen.blit(pygame.font.Font(
                "assets/DX_BOLD.ttf", 70).render(
                "控制器出错", True, (160, 20, 10)),
                (int((SCREEN_SIZE[0] - 350) / 2), int(SCREEN_SIZE[1] / 2) - 70))
            self.screen.blit(pygame.font.Font(
                "assets/DX_BOLD.ttf", 50).render(
                "程序将自动退出", True, (160, 20, 10)),
                (int((SCREEN_SIZE[0] - 350) / 2), int(SCREEN_SIZE[1] / 2)))

        else:
            ft = pygame.font.Font("assets/DX_BOLD.ttf", 30)

            if msg.hp * 3 > S1Robot.INITIAL_HP:
                self.screen.blit(ft.render(f"HP: {msg.hp} / {S1Robot.INITIAL_HP}",
                                           True, (10, 180, 10)), (100, 50))
            else:
                self.screen.blit(ft.render(f"HP: {msg.hp} / {S1Robot.INITIAL_HP}",
                                           True, (160, 20, 10)), (100, 50))
            if msg.heat > S1Robot.MAX_HEAT:
                self.screen.blit(ft.render("热量超限", True, (160, 20, 10)), (100, 100))
            elif msg.heat > S1Robot.MAX_HEAT * 0.8:
                self.screen.blit(ft.render(f"CAL: {msg.heat} / {S1Robot.MAX_HEAT}",
                                           True, (160, 20, 10)), (100, 100))
            elif msg.heat > S1Robot.MAX_HEAT * 0.6:
                self.screen.blit(ft.render(f"CAL: {msg.heat} / {S1Robot.MAX_HEAT}",
                                           True, (250, 150, 50)), (100, 100))
            else:
                self.screen.blit(ft.render(f"CAL: {msg.heat} / {S1Robot.MAX_HEAT}",
                                           True, (10, 180, 10)), (100, 100))

            if record:
                self.screen.blit(pygame.font.Font(
                    "assets/DX_BOLD.ttf", 20).render(
                    "录像模式", True, (160, 20, 10)), (8, 8))

            if ui_queue_size > QUEUE_BLOCK_THRESH:
                self.screen.blit(ft.render("显示延迟", True, (160, 20, 10)), (100, 150))
            if ctr_queue_size > QUEUE_BLOCK_THRESH:
                self.screen.blit(ft.render("操作延迟", True, (160, 20, 10)), (100, 200))

            if pygame.mouse.get_pos() != (int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2)) \
                    and msg.aim_method == "manual":
                self.screen.blit(ft.render("瞄准", True, (160, 20, 10)), (160, 300))
            if self.fire_show_delay > 0:
                self.screen.blit(ft.render("开火", True, (160, 20, 10)), (220, 300))
                self.fire_show_delay -= 1
            if self.speed[0] or self.speed[1]:
                self.screen.blit(ft.render("移动", True, (160, 20, 10)), (100, 300))

            if msg.aim_method != self.aim_method:
                self.screen.blit(ft.render("瞄准模式切换中", True, (160, 20, 10)), (100, 250))
            else:
                if msg.aim_method != "manual":
                    self.screen.blit(ft.render("自动瞄准: %s" % AUTO_AIM_METHOD_NAME[msg.aim_method],
                                               True, (10, 180, 10)), (100, 250))
                else:
                    self.screen.blit(ft.render("手动瞄准", True, (250, 150, 50)), (100, 250))

            if msg.aim_method != "manual":
                pygame.draw.rect(
                    self.screen, (10, 180, 10), pygame.Rect(
                        msg.target[0] - 60, msg.target[1] - 60, 120, 120), 3)
                pygame.draw.circle(
                    self.screen, (10, 180, 10), msg.target, 3, 3)
                self.screen.blit(pygame.font.Font("assets/DX_BOLD.ttf", 16).render(
                    f"{msg.target[0]},{msg.target[1]}", True, (10, 180, 10)
                ), (msg.target[0] - 60, msg.target[1] - 60))

            if not self.debug:
                self.screen.blit(ft.render(f"BAT: {msg.bat}", True, (10, 255, 10)), (300, 50))
        pygame.display.flip()

    def _update_cur(self):
        cur_delta = (0, 0)

        if self.aim_method == "manual":
            cur_current = pygame.mouse.get_pos()
            if cur_current != (int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2)):
                cur_delta = (cur_current[0] - int(SCREEN_SIZE[0] / 2),
                             cur_current[1] - int(SCREEN_SIZE[1] / 2))
                pygame.mouse.set_pos(int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2))
        else:
            pygame.mouse.set_pos(int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2))

        return cur_delta

    def feedback(self, out_queue: mp.Queue):
        for event in pygame.event.get():
            speed, aim_method = self.speed, self.aim_method
            terminate, cur_delta = event.type == QUIT, (0, 0)

            if event.type == KEYDOWN and event.key in Window.SPEED_MAP:
                speed = (speed[0] + Window.SPEED_MAP[event.key][0], speed[1] + Window.SPEED_MAP[event.key][1])

            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    terminate = True

                elif event.key in (K_q, K_e):
                    aim_method = {K_q: AIM_METHOD_SELECT_LIST[self.aim_method], K_e: "manual"}[event.key]

            elif event.type == KEYUP and event.key in Window.SPEED_MAP:
                speed = (speed[0] - Window.SPEED_MAP[event.key][0], speed[1] - Window.SPEED_MAP[event.key][1])

            if not out_queue.full():
                if event.type == MOUSEBUTTONDOWN:
                    self.fire_show_delay = FIRE_UI_SHOW_TIME

                self.aim_method = aim_method

                out_queue.put(Msg2Controller(speed=speed, cur_delta=self._update_cur(), aim_method=self.aim_method,
                                             fire=event.type == MOUSEBUTTONDOWN, terminate=terminate))

                self.speed = speed

            else:
                logging.warning("CTR MSG QUEUE FULL")

        if out_queue.empty():
            out_queue.put(Msg2Controller(speed=self.speed, cur_delta=self._update_cur(), aim_method=self.aim_method))
