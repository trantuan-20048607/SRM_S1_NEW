# -*- coding: utf-8 -*-

import logging
import threading
import time

from robomaster import *

from app.config import *
from app.controller.const import S1Robot
from app.controller.msg import *
from app.core import vision
from app.core.controller import *

__all__ = ["S1Controller"]


class S1Controller(Controller):
    def __init__(self, name: str, color: str, debug: bool):
        super(S1Controller, self).__init__()

        assert color in COLOR_LIST

        self.name = name
        self.debug = debug
        self.color = color
        self.hp = S1Robot.INITIAL_HP
        self.heat = 0
        self.bat = 0
        self.speed = (0, 0)
        self.cool_time = time.time()
        self.aim_method = DEFAULT_AIM_METHOD
        self.aim_target = (int(SCREEN_SIZE[0] / 2), int(SCREEN_SIZE[1] / 2))
        self.lock = {
            "heat": threading.Lock(),
            "hp": threading.Lock(),
            "cool_time": threading.Lock()
        }
        threading.Thread(target=self._cool).start()
        if not self.debug:
            self.s1 = robot.Robot()
            self.s1.initialize(conn_type="ap", proto_type="udp")
            self.s1.set_robot_mode(mode=robot.GIMBAL_LEAD)
            self.s1.led.set_led(comp=led.COMP_ALL,
                                r=COLOR[color][0],
                                g=COLOR[color][1],
                                b=COLOR[color][2], effect=led.EFFECT_ON)
            self.s1.camera.start_video_stream(display=False)
            self.s1.armor.sub_ir_event(callback=self._ir_hit_callback)
            self.s1.battery.sub_battery_info(freq=5, callback=self._battery_callback)
            self.s1.gimbal.sub_angle(callback=self._angle_callback)
            self.s1.armor.set_hit_sensitivity(sensitivity=10)
            self.action_state = True
            self.gimbal_action = None

    def _modify_hp(self, hp):
        self.lock["hp"].acquire()
        self.hp = hp
        logging.info(f"HP {self.hp} / {S1Robot.INITIAL_HP}")
        self.lock["hp"].release()

    def _modify_heat(self, heat):
        self.lock["heat"].acquire()
        self.heat = heat
        logging.info(f"HEAT {self.heat}")
        self.lock["heat"].release()

    def _reset_cool_time(self):
        self.lock["cool_time"].acquire()
        self.cool_time = time.time()
        self.lock["cool_time"].release()

    def _cool(self):
        while self.hp > 0:
            if 0.95 < time.time() - self.cool_time <= 1.05:
                logging.info("COOLING")
                self._reset_cool_time()
                self._modify_heat(max(self.heat - S1Robot.COOL_HEAT, 0))
            time.sleep(0.1)

    def _bleed(self, tag):
        if tag == "hit":
            logging.info("HIT")
            if self.hp <= S1Robot.HIT_DMG:
                self.die()
            else:
                self._modify_hp(self.hp - S1Robot.HIT_DMG)
                if not self.debug:
                    self.s1.led.set_led(comp=led.COMP_ALL,
                                        r=SUB_COLOR[self.color][0],
                                        g=SUB_COLOR[self.color][1],
                                        b=SUB_COLOR[self.color][2],
                                        effect=HIT_EFFECT[self.color])
                    time.sleep(0.03)
                    self.s1.led.set_led(comp=led.COMP_ALL,
                                        r=COLOR[self.color][0],
                                        g=COLOR[self.color][1],
                                        b=COLOR[self.color][2], effect=led.EFFECT_ON)
        elif tag == "burn":
            logging.info("BURNING")
            dmg = min(self.heat - S1Robot.MAX_HEAT, S1Robot.MAX_BURN_DMG)
            if self.hp <= dmg:
                self.die()
            else:
                self._modify_hp(self.hp - dmg)

    def _battery_callback(self, bat):
        self.bat = bat
        return bat

    def _ir_hit_callback(self, hit):
        self._bleed(tag="hit")
        return hit

    @staticmethod
    def _angle_callback(angle: tuple):
        return angle

    def img(self) -> np.ndarray:
        return self.s1.camera.read_cv2_image()

    def act(self, img: np.ndarray, msg: Msg2Controller):
        if msg.terminate:
            self.die()
            return
        if self.speed != msg.speed:
            if not self.debug:
                self.s1.chassis.drive_speed(x=msg.speed[0], y=msg.speed[1], z=0, timeout=1)
            self.speed = msg.speed
            logging.debug(f"SPD CHG X{msg.speed[0]} Y{msg.speed[1]}")
        if self.aim_method != msg.aim_method:
            self.aim_method = msg.aim_method
            logging.info(f"AIM MTD CHG {self.aim_method.upper()}")
        if self.aim_method != "manual":
            if msg.reset_auto_aim:
                vision.reset()
            self.aim_target = vision.feed(img, color=ENEMY_COLOR[self.color], type_=self.aim_method)
            if msg.auto_aim_take_effect:
                yaw = (self.aim_target[0] - int(SCREEN_SIZE[0] * 0.5)) / SCREEN_SIZE[0] * AUTO_AIM_SENSITIVITY[0]
                pitch = (int(SCREEN_SIZE[1] * 0.5) - self.aim_target[1]) / SCREEN_SIZE[1] * AUTO_AIM_SENSITIVITY[1]
            else:
                yaw, pitch = 0.0, 0.0
            logging.info(f"TGT {self.aim_target[0]}, {self.aim_target[1]}")
        else:
            yaw = msg.cur_delta[0] / SCREEN_SIZE[0] * MANUAL_AIM_SENSITIVITY[0]
            pitch = - msg.cur_delta[1] / SCREEN_SIZE[1] * MANUAL_AIM_SENSITIVITY[1]
            if REVERSE_Y_AXIS:
                pitch = - pitch
        logging.info("ROT Y%.2f P%.2f" % (yaw, pitch))
        print("ROT Y%.2f P%.2f" % (yaw, pitch))
        if not self.debug:
            if self.speed == (0, 0) and \
                    yaw <= AIMING_DEAD_ZONE[0] and pitch <= AIMING_DEAD_ZONE[1]:
                self.s1.set_robot_mode(mode=robot.GIMBAL_LEAD)
            if self.gimbal_action:
                self.action_state = self.gimbal_action.is_completed
            if self.action_state and (
                    50 > abs(yaw) > AIMING_DEAD_ZONE[0] or 10 > abs(pitch) > AIMING_DEAD_ZONE[1]):
                self.gimbal_action = self.s1.gimbal.move(yaw=yaw, pitch=pitch,
                                                         pitch_speed=S1Robot.GIMBAL_SPEED_PITCH,
                                                         yaw_speed=S1Robot.GIMBAL_SPEED_YAW)
        if msg.fire:
            logging.info("FIRE")
            if not self.debug:
                self.s1.blaster.set_led(200)
                self.s1.blaster.fire(blaster.INFRARED_FIRE, 1)
            if self.heat == 0:
                self._reset_cool_time()
            self._modify_heat(self.heat + S1Robot.FIRE_HEAT)
            if self.heat > S1Robot.MAX_HEAT:
                self._bleed(tag="burn")

    def die(self):
        logging.info("DIE")
        self._modify_hp(0)
        if not self.debug:
            self.s1.chassis.drive_speed(x=0, y=0, z=0, timeout=1)
            self.s1.led.set_led(comp=led.COMP_ALL,
                                r=SUB_COLOR[self.color][0],
                                g=SUB_COLOR[self.color][1],
                                b=SUB_COLOR[self.color][2],
                                effect=led.EFFECT_FLASH,
                                freq=1)
            self.s1.camera.stop_video_stream()
            self.s1.close()
