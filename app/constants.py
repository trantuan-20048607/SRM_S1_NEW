# -*- coding: utf-8 -*-

import numpy as np
from robomaster import led

# --------------------
#     ⚪ 基础设置 ⚪
# --------------------

# 屏幕大小
SCREEN_SIZE = (1280, 720)

# 程序支持的颜色
COLOR_LIST = ("red", "blue")

# 敌人的颜色对应关系
COLOR_ENEMY_LIST = {
    "red": "blue",
    "blue": "red"
}

# 颜色定义
COLOR_RGB_LIST = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255)
}

# 副颜色定义
SUB_COLOR_RGB_LIST = {
    "red": COLOR_RGB_LIST["blue"],
    "blue": COLOR_RGB_LIST["red"]
}

# 瞄准死区
AIMING_DEAD_ZONE = (0.1, 0.1)

# 击打特效定义
HIT_EFFECT = {
    "red": led.EFFECT_OFF,
    "blue": led.EFFECT_FLASH
}

# 默认瞄准方式
DEFAULT_AIM_METHOD = "manual"

# 延迟判定阈值
QUEUE_BLOCK_THRESH = 2

# 限制显示帧率
UI_FPS_LIMIT = 60

# 限制控制器帧率
CTR_FPS_LIMIT = 45

# 准星类型: 0 关闭，1 十字，2 圆点
FIRE_IND_TYPE = 1

# 准星大小
FIRE_IND_SIZE = 12

# 开火消息显示时间（帧数）
FIRE_UI_SHOW_TIME = 6

# --------------------
#    ⚪ 手动瞄准设置 ⚪
# --------------------

# 手动瞄准灵敏度
AIMING_MAGNIFICATION = (180, 30)

# 反转 Y 轴
REVERSE_Y_AXIS = False

# --------------------
#    ⚪ 自瞄参数设置 ⚪
# --------------------

# 自动瞄准灵敏度
AUTO_AIM_MAGNIFICATION = (90, 15)

# 色彩提取范围定义
HSV_RANGE = {
    "red": [(np.array([176, 112, 102]), np.array([180, 255, 255])),
            (np.array([0, 112, 102]), np.array([8, 255, 255]))],
    "blue": (np.array([90, 112, 102]), np.array([100, 255, 255]))
}

# 参与识别的最小矩形面积
MIN_RECT_AREA = 16

# 判定识别有效所需的面积总和
MIN_VALID_TOTAL_AREA = 64

# 灰度门限
GRAY_THRESH = 16

# ROI 激活边界
ROI_LIMIT = 128

# --------------------
#    ⚪ 自瞄平滑设置 ⚪
# --------------------

# ROI 裁剪区域大小
ROI_SIZE = (324, 324)

# 瞄准方式切换顺序
AIM_METHOD_SELECT_LIST = {"manual": "tri",
                          "kalman": "direct",
                          "tri": "kalman",
                          "direct": "tri"}

# 自动瞄准方式列表
AUTO_AIM_METHOD_LIST = ("kalman", "tri", "direct")

# 各个自瞄方法的显示名称
AUTO_AIM_METHOD_NAME = {"tri": "差分反馈",
                        "kalman": "KALMAN",
                        "direct": "原始数据"}

# KALMAN 滤波器参数，详见 README
KALMAN_SHAKE_CONTROL = 1e-3
KALMAN_DELAY_CONTROL = 1e-1

# 差分反馈参数，详见 README
TRIANGULAR_DIFFERENCE_WEIGHT = ((1, 2, 1), (2, 2, 1), (3, 1, 0))
TRIANGULAR_SIDE_LEN_LEVEL = (24, 48)
