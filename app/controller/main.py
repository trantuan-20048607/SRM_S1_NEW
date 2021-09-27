# -*- coding: utf-8 -*-
import logging
import time

from robomaster import *

from app.constants import *
from app.controller.msg import *
from app.core import vision
from app.core.controller import *

__all__ = ["S1Controller"]


class S1Controller(Controller):
    MAX_HEAT = 150
    HIT_DMG = 15
    FIRE_HEAT = 25
    COOL_HEAT = 15
    MAX_BURN_DMG = 35
    INITIAL_HP = 600
    INITIAL_BAT = 100
    GIMBAL_SPEED_YAW = 100
    GIMBAL_SPEED_PITCH = 100

    def __init__(self, name: str, color: str, debug: bool):
        super(S1Controller, self).__init__()

        assert color in COLOR_LIST

        self.name = name
        self.color = color
        self.debug = debug
        self.hp = S1Controller.INITIAL_HP
        self.bat = S1Controller.INITIAL_BAT
        self.aim_method = DEFAULT_AIM_METHOD

        self.last_cool_time = time.time()
        self.hit_times, self.last_hit_times = 0, 0
        self.target = (int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2))

        if not debug:
            self.s1 = robot.Robot()
            self.s1.initialize(conn_type="ap", proto_type="udp")
            logging.debug(self.s1.set_robot_mode(mode=robot.GIMBAL_LEAD))
            self.s1.led.set_led(comp=led.COMP_ALL,
                                r=COLOR_RGB_LIST[color][0],
                                g=COLOR_RGB_LIST[color][1],
                                b=COLOR_RGB_LIST[color][2], effect=led.EFFECT_ON)
            self.s1.camera.start_video_stream(display=False)
            self.s1.armor.sub_ir_event(callback=self.ir_hit_callback)
            self.s1.battery.sub_battery_info(freq=5, callback=self.battery_callback)
            self.s1.gimbal.sub_angle(callback=self.angle_callback)
            self.s1.armor.set_hit_sensitivity(sensitivity=10)

        logging.debug(self)

    def get_img(self):
        return self.s1.camera.read_cv2_image()

    def act(self, img, msg: Msg2Controller):
        if msg.terminate:
            self.__die()
            return

        if not self.debug:
            self.s1.chassis.drive_speed(x=msg.speed[0], y=msg.speed[1], z=0, timeout=1)

        logging.debug(f"SPD X{msg.speed[0]} Y{msg.speed[1]}")

        if msg.aim_method != self.aim_method:
            self.aim_method = msg.aim_method

            if self.aim_method == "manual":
                logging.info("AUTO AIM OFF")
            else:
                logging.info(f"AUTO AIM SWITCHED TO {self.aim_method.upper()}")

        if self.aim_method != "manual":
            self.target = vision.feed(img, color=COLOR_ENEMY_LIST[self.color], tag=self.aim_method)
            yaw = (self.target[0] - int(SCREEN_SIZE[0] / 2)) / SCREEN_SIZE[0] * 125
            pitch = (int(SCREEN_SIZE[1] / 2) - self.target[1]) / SCREEN_SIZE[1] * 20

            logging.debug(f"AUTO AIM {self.target[0]}, {self.target[1]}")

        else:
            yaw = msg.cur_delta[0] / SCREEN_SIZE[0] * 120
            pitch = - msg.cur_delta[1] / SCREEN_SIZE[1] * 20

        logging.info(f"ROT Y{yaw} P{pitch}")

        if not self.debug:
            if self.action_state:
                if 50 > abs(yaw) >= 3 or 10 > abs(pitch) > 3:
                    self.gimbal_action = self.s1.gimbal.move(yaw=yaw, pitch=pitch,
                                                             pitch_speed=S1Controller.GIMBAL_SPEED_PITCH,
                                                             yaw_speed=S1Controller.GIMBAL_SPEED_YAW)
                    self.action_state = self.gimbal_action.is_completed
            else:
                self.action_state = self.gimbal_action.is_completed

        if msg.fire:
            if not self.debug:
                self.s1.blaster.set_led(200)
                self.s1.blaster.fire(blaster.INFRARED_FIRE, 1)

            self.heat += S1Controller.FIRE_HEAT
            if self.heat > S1Controller.MAX_HEAT:
                self.__bleed(tag="burn")

            logging.info("FIRE")

    def hit(self):
        if self.hit_times > self.last_hit_times:
            for _ in range(self.last_hit_times, self.hit_times):
                self.__bleed(tag="hit")
            self.last_hit_times = self.hit_times

    def cool(self):
        if 0.95 < time.time() - self.last_cool_time < 1.05:
            self.last_cool_time = time.time()
            self.heat = max(self.heat - S1Controller.COOL_HEAT, 0)

            logging.info("COOLING DOWN")

    def __bleed(self, tag: str):
        if tag == "hit":
            self.hp -= S1Controller.HIT_DMG
            if not self.debug:
                self.s1.led.set_led(comp=led.COMP_ALL,
                                    r=SUB_COLOR_RGB_LIST[self.color][0],
                                    g=SUB_COLOR_RGB_LIST[self.color][1],
                                    b=SUB_COLOR_RGB_LIST[self.color][2],
                                    effect={
                                        "red": led.EFFECT_OFF,
                                        "blue": led.EFFECT_FLASH
                                    }[self.color])
                time.sleep(0.03)
                self.s1.led.set_led(comp=led.COMP_ALL,
                                    r=COLOR_RGB_LIST[self.color][0],
                                    g=COLOR_RGB_LIST[self.color][1],
                                    b=COLOR_RGB_LIST[self.color][2], effect=led.EFFECT_ON)
        elif tag == "burn":
            burn_hp = max(self.heat - S1Controller.MAX_HEAT, S1Controller.MAX_BURN_DMG)
            self.hp -= burn_hp

        if self.hp <= 0:
            self.__die()

    def __die(self):
        self.hp = 0

        if not self.debug:
            self.s1.chassis.drive_speed(x=0, y=0, z=0, timeout=1)
            self.s1.led.set_led(comp=led.COMP_ALL,
                                r=SUB_COLOR_RGB_LIST[self.color][0],
                                g=SUB_COLOR_RGB_LIST[self.color][1],
                                b=SUB_COLOR_RGB_LIST[self.color][2],
                                effect=led.EFFECT_FLASH,
                                freq=1)
            self.s1.camera.stop_video_stream()
            self.s1.close()

        logging.info("DIE")

    def battery_callback(self, bat):

        logging.info(f"BAT {bat}")

        self.bat = bat

        return bat

    def ir_hit_callback(self, hit):

        logging.info(f"HIT {hit} TIMES")

        self.hit_times = hit

        return hit

    @staticmethod
    def angle_callback(x):
        return x
