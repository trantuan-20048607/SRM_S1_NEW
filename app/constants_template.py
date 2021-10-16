# -*- coding: utf-8 -*-

from robomaster import led

# --------------------
#     ⚪ 系统设置 ⚪
# --------------------

# 队列阻塞阈值
QUEUE_BLOCK_THRESH = 2

# 限制显示帧率
UI_FPS_LIMIT = 60

# 限制控制器帧率
CTR_FPS_LIMIT = 30

# --------------------
#     ⚪ 界面设置 ⚪
# --------------------

# 屏幕大小
SCREEN_SIZE = (1280, 720)

# 窗口标题
WINDOW_TITLE = "SRM 校内赛"

# 字体文件
UI_FONT = "assets/DVS.ttf"

# UI 警报颜色
UI_COLOR_WARNING = (160, 20, 10)

# UI 提醒颜色
UI_COLOR_NOTICE = (250, 160, 0)

# UI 正常颜色
UI_COLOR_NORMAL = (10, 160, 10)

# 准星类型: 0 关闭，1 十字，2 圆点
FIRE_IND_TYPE = 1

# 准星大小
FIRE_IND_SIZE = 12

# 开火消息显示时间（帧数）
FIRE_UI_SHOW_TIME = 6

# --------------------
#    ⚪ 控制颜色设置 ⚪
# --------------------

# 已知颜色
COLOR_LIST = ("red", "blue")

# 颜色敌对关系
ENEMY_COLOR = {
    "red": "blue",
    "blue": "red"
}

# 颜色定义
COLOR_RGB = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255)
}

# 副颜色定义
SUB_COLOR_RGB = {
    "red": COLOR_RGB["blue"],
    "blue": COLOR_RGB["red"]
}

# 击打特效定义
HIT_EFFECT = {
    "red": led.EFFECT_OFF,
    "blue": led.EFFECT_FLASH
}

# --------------------
#    ⚪ 瞄准设置 ⚪
# --------------------

# 自动瞄准方式列表
AUTO_AIM_METHOD_LIST = ("default",)

# 各个自瞄方法的显示名称
AUTO_AIM_METHOD_NAME = {"default": "DEFAULT (NO FLT)"}

# 瞄准方式切换顺序
AIM_METHOD_SELECT_LIST = {"manual": "default"}

# 默认瞄准方式
DEFAULT_AIM_METHOD = "manual"

# 瞄准死区
AIMING_DEAD_ZONE = (0.1, 0.1)

# 手动瞄准灵敏度
MANUAL_AIM_SENSITIVITY = (180, 45)

# 自动瞄准灵敏度
AUTO_AIM_SENSITIVITY = (90, 15)

# 反转 Y 轴
REVERSE_Y_AXIS = False

# --------------------
#    ⚪ 自瞄参数设置 ⚪
# --------------------

# 此处填写自瞄处理参数

# --------------------
#    ⚪ 自瞄平滑设置 ⚪
# --------------------

# 此处填写滤波器参数
