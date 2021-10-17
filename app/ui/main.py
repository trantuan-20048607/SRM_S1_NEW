# -*- coding: utf-8 -*-
import logging
import math
import multiprocessing as mp
import time

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

    def __init__(self, debug: bool, record: bool):
        pygame.init()
        pygame.event.set_allowed([MOUSEBUTTONDOWN, KEYUP, KEYDOWN])
        pygame.event.set_blocked(MOUSEMOTION)
        pygame.display.set_caption(WINDOW_TITLE)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.debug = debug
        self.record = record
        self.screen = pygame.display.set_mode(SCREEN_SIZE, flags=pygame.DOUBLEBUF)
        self.speed = (0, 0)
        self.cur_delta = (0, 0)
        self.fire_show_delay = 0
        self.fire_indicator_type = FIRE_IND_TYPE
        self.aim_method = DEFAULT_AIM_METHOD
        self.last_aim_target = (int(SCREEN_SIZE[0] * 0.5), int(SCREEN_SIZE[1] * 0.5))

    def _draw_indicator(self, x: int, y: int, type_: int):
        dist = int(4 * math.log(self.cur_delta[0] * self.cur_delta[0] + self.cur_delta[1] * self.cur_delta[1] + 1))
        if dist <= FIRE_IND_SIZE:
            color = UI_COLOR_NORMAL
        elif dist <= FIRE_IND_SIZE * 2:
            color = UI_COLOR_NOTICE
        else:
            color = UI_COLOR_WARNING
        if type_ == 1:
            dist = max(dist, FIRE_IND_SIZE / 2)
            pygame.draw.rect(self.screen, color, pygame.Rect(
                x - FIRE_IND_SIZE - dist, y - 1, FIRE_IND_SIZE, 2))
            pygame.draw.rect(self.screen, color, pygame.Rect(
                x + dist, y - 1, FIRE_IND_SIZE, 2))
            pygame.draw.rect(self.screen, color, pygame.Rect(
                x - 1, y - FIRE_IND_SIZE - dist, 2, FIRE_IND_SIZE))
            pygame.draw.rect(self.screen, color, pygame.Rect(
                x - 1, y + dist, 2, FIRE_IND_SIZE))
            pygame.draw.circle(self.screen, color, (x, y), 2)
        elif type_ == 2:
            dist = min(max(1.5 * dist, FIRE_IND_SIZE), 60)
            pygame.draw.circle(self.screen, color, (x, y), dist, 2)
            if dist > 8:
                pygame.draw.circle(self.screen, color, (x, y), 2)

    def _update_cur(self):
        if self.aim_method == "manual":
            self.cur_delta = (0, 0)
            cur_current = pygame.mouse.get_pos()
            if cur_current != (int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2)):
                self.cur_delta = (cur_current[0] - int(SCREEN_SIZE[0] / 2),
                                  cur_current[1] - int(SCREEN_SIZE[1] / 2))
                pygame.mouse.set_pos(int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2))
                logging.debug("RESET CUR POS")

    def update(self, msg: Msg2Window, ui_queue_size: int, ctr_queue_size: int, fps: tuple):
        if msg.err:
            for i in range(5):
                pygame.surfarray.blit_array(self.screen, cv.cvtColor(msg.img, cv.COLOR_BGR2RGB))
                self.screen.blit(pygame.font.Font(
                    UI_FONT, 70).render(
                    "CONTROLLER ERROR", True, UI_COLOR_WARNING),
                    (int((SCREEN_SIZE[0] - 640) / 2), int(SCREEN_SIZE[1] / 2) - 70))
                self.screen.blit(pygame.font.Font(
                    UI_FONT, 32).render(
                    f"PROGRAM WILL EXIT AUTOMATICALLY IN {5 - i} SECONDS", True, UI_COLOR_WARNING),
                    (int((SCREEN_SIZE[0] - 836) / 2), int(SCREEN_SIZE[1] / 2)))
                pygame.display.flip()
                time.sleep(1)
        else:
            pygame.surfarray.blit_array(self.screen, cv.cvtColor(msg.img, cv.COLOR_BGR2RGB))
            ft = pygame.font.Font(UI_FONT, 20)
            self.screen.blit(ft.render("FPS UI  %.0f/%.0f" % fps, True,
                                       UI_COLOR_NORMAL if fps[0] * 2 > UI_FPS_LIMIT else UI_COLOR_WARNING), (0, 0))
            self.screen.blit(ft.render("FPS CTR %.0f/%.0f" % msg.fps, True,
                                       UI_COLOR_NORMAL if msg.fps[0] * 2 > CTR_FPS_LIMIT else UI_COLOR_WARNING),
                             (0, 20))
            if self.record:
                self.screen.blit(ft.render("REC", True, UI_COLOR_WARNING), (0, 40))
            ft = pygame.font.Font(UI_FONT, 30)
            self.screen.blit(ft.render(
                f"HP {msg.hp}", True,
                UI_COLOR_NORMAL if msg.hp * 3 > S1Robot.INITIAL_HP else UI_COLOR_WARNING), (96, 64))
            if msg.heat > S1Robot.MAX_HEAT:
                self.screen.blit(ft.render(f"OVERHEAT {msg.heat}", True, UI_COLOR_WARNING), (96, 112))
            elif msg.heat > S1Robot.MAX_HEAT * 0.8:
                self.screen.blit(ft.render(f"HEAT {msg.heat}/{S1Robot.MAX_HEAT}",
                                           True, UI_COLOR_WARNING), (96, 112))
            elif msg.heat > S1Robot.MAX_HEAT * 0.6:
                self.screen.blit(ft.render(f"HEAT {msg.heat}/{S1Robot.MAX_HEAT}",
                                           True, UI_COLOR_NOTICE), (96, 112))
            else:
                self.screen.blit(ft.render(f"HEAT {msg.heat}/{S1Robot.MAX_HEAT}",
                                           True, UI_COLOR_NORMAL), (96, 112))
            if ui_queue_size > QUEUE_BLOCK_THRESH:
                self.screen.blit(ft.render("UI", True, UI_COLOR_WARNING), (96, 160))
            if ctr_queue_size > QUEUE_BLOCK_THRESH:
                self.screen.blit(ft.render("CTR", True, UI_COLOR_WARNING), (192, 160))
            if pygame.mouse.get_pos() != (int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2)) \
                    and msg.aim_method == "manual":
                self.screen.blit(ft.render("A", True, UI_COLOR_WARNING), (160, 256))
            if self.fire_show_delay > 0:
                self.screen.blit(ft.render("F", True, UI_COLOR_WARNING), (224, 256))
                self.fire_show_delay -= 1
            if self.speed[0] or self.speed[1]:
                self.screen.blit(ft.render("M", True, UI_COLOR_WARNING), (96, 256))
            if msg.aim_method != self.aim_method:
                self.screen.blit(ft.render("SWITCHING", True, UI_COLOR_WARNING), (96, 208))
            else:
                if msg.aim_method != "manual":
                    self.screen.blit(ft.render("%s" % AUTO_AIM_METHOD_NAME[msg.aim_method],
                                               True, UI_COLOR_NORMAL), (96, 208))
                else:
                    self.screen.blit(ft.render("MANUAL", True, UI_COLOR_NOTICE), (96, 208))
            if msg.aim_method == "manual":
                self._draw_indicator(int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2), self.fire_indicator_type)
            else:
                self.cur_delta = (msg.aim_target[0] - self.last_aim_target[0],
                                  msg.aim_target[1] - self.last_aim_target[1])
                self._draw_indicator(msg.aim_target[0], msg.aim_target[1], 2)
                self.last_aim_target = msg.aim_target
            if not self.debug:
                self.screen.blit(ft.render(
                    f" BAT {msg.bat}", True, (232, 188, 245)), (SCREEN_SIZE[0] - 192, 64))
            pygame.display.flip()

    def feedback(self, out_queue: mp.Queue):
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                while not out_queue.empty():
                    _ = out_queue.get()
                out_queue.put(Msg2Controller(terminate=True))
                break
            elif event.type == KEYDOWN and event.key == K_i:
                self.fire_indicator_type = (self.fire_indicator_type + 1) % 3
            elif event.type == KEYDOWN and event.key == K_r:
                if out_queue.full():
                    _ = out_queue.get()
                self._update_cur()
                out_queue.put(Msg2Controller(cur_delta=self.cur_delta,
                                             aim_method=self.aim_method,
                                             reset_auto_aim=True))
            elif event.type == MOUSEBUTTONDOWN:
                if out_queue.full():
                    _ = out_queue.get()
                self._update_cur()
                self.fire_show_delay = FIRE_UI_SHOW_TIME
                out_queue.put(Msg2Controller(cur_delta=self.cur_delta,
                                             aim_method=self.aim_method,
                                             fire=True))
            else:
                speed, aim_method = self.speed, self.aim_method
                if event.type == KEYDOWN and event.key in Window.SPEED_MAP:
                    speed = (speed[0] + Window.SPEED_MAP[event.key][0], speed[1] + Window.SPEED_MAP[event.key][1])
                elif event.type == KEYDOWN and event.key in (K_q, K_e):
                    aim_method = {K_q: AIM_METHOD_SELECT_LIST[self.aim_method], K_e: "manual"}[event.key]
                elif event.type == KEYUP and event.key in Window.SPEED_MAP:
                    speed = (speed[0] - Window.SPEED_MAP[event.key][0], speed[1] - Window.SPEED_MAP[event.key][1])
                if (self.speed != speed or self.aim_method != aim_method) and not out_queue.full():
                    self._update_cur()
                    self.speed = speed
                    self.aim_method = aim_method
                    pygame.mouse.set_visible(self.aim_method != "manual")
                    out_queue.put(Msg2Controller(speed=self.speed,
                                                 cur_delta=self.cur_delta,
                                                 aim_method=self.aim_method))
        if out_queue.empty():
            self._update_cur()
            out_queue.put(Msg2Controller(speed=self.speed,
                                         cur_delta=self.cur_delta,
                                         aim_method=self.aim_method))
