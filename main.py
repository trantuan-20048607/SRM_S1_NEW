# -*- coding: utf-8 -*-
import argparse
import logging

from app.constants import *
from app.core.container import *

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", default=False, help="DEBUG MODE", action="store_true")

    for color in COLOR_LIST:
        parser.add_argument(
            f"-{color[0]}", f"--{color}", default=False,
            help=f"{color.upper()} MODE", action="store_true")

    parser.add_argument("--record", default=False, help="RECORDING VIDEO", action="store_true")
    args = parser.parse_args()

    color = ""
    for c in COLOR_LIST:
        assert color == ""
        if eval(f"args.{c}"):
            color = c
            break

    assert color != ""

    logging.basicConfig(level={True: logging.DEBUG, False: logging.INFO}[args.debug],
                        filename="logs/app.log", filemode="w",
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")

    app = Container(color, args.debug, args.record)
    app.start()
