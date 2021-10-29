# -*- coding: utf-8 -*-

from robomaster import led

# --------------------
#     ⚪ 系统设置 ⚪
# --------------------

# 队列阻塞阈值
# 某个队列内消息超过该数量时，将在界面上警告延迟
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

# 用于 UI 的字体文件
# 若要修改此参数，请勿删除默认的 assets/DVS.ttf，该字体用于内置的报错提示
UI_FONT = "assets/DVS.ttf"

# UI 颜色，使用 RGB 表示
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

# 敌人的颜色
ENEMY_COLOR = {
    "red": "blue",
    "blue": "red"
}

# LED 颜色定义
COLOR = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255)
}

# LED 副颜色定义
SUB_COLOR = {
    "red": COLOR["blue"],
    "blue": COLOR["red"]
}

# 被击打特效定义
HIT_EFFECT = {
    "red": led.EFFECT_OFF,
    "blue": led.EFFECT_FLASH
}

# --------------------
#    ⚪ 瞄准设置 ⚪
# --------------------

# 自动瞄准方式列表
# 在此处列出所有自动瞄准方法，手动瞄准默认为 "manual" 且不可修改
AUTO_AIM_METHOD_LIST = ("kalman", "tri", "direct")

# 各个自瞄方法的显示名称
# 请勿写成中文，否则录制视频时（OpenCV）将无法显示名称
AUTO_AIM_METHOD_NAME = {"tri": "TRI FLT",
                        "kalman": "KALMAN FLT",
                        "direct": "NO FLT"}

# 瞄准方式切换顺序
# 处于左边的模式时，按下 Q 切换至右边模式，确保每一个模式都有对应的切换目标
AIM_METHOD_SELECT_LIST = {"manual": "tri",
                          "kalman": "direct",
                          "tri": "kalman",
                          "direct": "tri"}

# 默认瞄准方式，建议选择手动
DEFAULT_AIM_METHOD = "manual"

# 瞄准死区
AIMING_DEAD_ZONE = (0.1, 0.1)

# 手动瞄准灵敏度
MANUAL_AIM_SENSITIVITY = (180, 75)

# 自动瞄准灵敏度
AUTO_AIM_SENSITIVITY = (75, 20)

# 反转 Y 轴，用于鼠标模拟摇杆操作
REVERSE_Y_AXIS = False

# --------------------
#    ⚪ 自瞄参数设置 ⚪
# --------------------

# 参与识别的最小矩形面积
MIN_RECT_AREA = 128

# 判定识别有效所需的面积总和
MIN_VALID_TOTAL_AREA = 192

# 二值化门限
BIN_THRESH = {
    "red": 96,
    "blue": 72
}

# ROI 激活边界
ROI_LIMIT = 128

# --------------------
#    ⚪ 自瞄平滑设置 ⚪
# --------------------

# KALMAN 滤波器参数，详见 README
KALMAN_SHAKE_CONTROL = 1e-3
KALMAN_DELAY_CONTROL = 1e-1

# 差分反馈参数，详见 README
TRIANGULAR_DIFFERENCE_WEIGHT = ((1, 2, 1), (2, 2, 1), (3, 1, 0))
TRIANGULAR_SIDE_LEN_LEVEL = (24, 48)
