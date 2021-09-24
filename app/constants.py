# -*- coding: utf-8 -*-

# --------------------
#   ⚪ 基础、界面设置 ⚪
# --------------------

# 屏幕大小
SCREEN_SIZE = (1280, 720)

# 程序支持的颜色
COLOR_LIST = ("red", "blue")

# 录制视频帧率
RECORDING_FPS = 30

# 默认瞄准方式
DEFAULT_AIM_METHOD = "manual"

# 延迟判定阈值
QUEUE_BLOCK_THRESH = 2

# 开火消息显示时间（刷新次数）
FIRE_UI_SHOW_TIME = 10

# --------------------
#     ⚪ 瞄准设置 ⚪
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

# KALMAN 滤波器参数，详见 README
KALMAN_SHAKE_CONTROL = 1e-3
KALMAN_DELAY_CONTROL = 1e-1

# 差分反馈参数，详见 README
TRIANGULAR_DIFFERENCE_WEIGHT = ((1, 3, 2), (2, 2, 1), (3, 1, 0))
TRIANGULAR_SIDE_LEN_LEVEL = (24, 48)
