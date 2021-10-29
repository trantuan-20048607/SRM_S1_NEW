# -*- coding: utf-8 -*-
"""
  ***********************************************
  * S1 Framework for SRM Intramural Competition *
  *          Python 3 OpenCV Edition            *
  ***********************************************

Version: 1.0.0
Author: Tran Tuan
Email: chenjun6403@163.com

"""

import argparse
import logging

from app.config import *
# TODO 在此处导入测试模块
from app.test import vision

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # TODO 在此处加入自定义测试模块
    parser.add_argument("--vision", default=False, help="VISION MODULE TEST", action="store_true")

    for color in COLOR_LIST:
        parser.add_argument(
            f"-{color[0]}", f"--{color}", default=False,
            help=f"{color.upper()} MODE", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG, filename="logs/test.log", filemode="w",
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")

    color = ""
    for col in COLOR_LIST:
        if eval(f"args.{col}"):
            assert color == ""
            color = col
    assert color != ""

    # TODO 在此处加入测试入口
    if args.vision:
        vision.start(color)
