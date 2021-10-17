import argparse
import logging

from app.constants import *
from app.test import vision

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vision", default=False, help="VISION MODULE TEST", action="store_true")
    for color in COLOR_LIST:
        parser.add_argument(
            f"-{color[0]}", f"--{color}", default=False,
            help=f"{color.upper()} MODE", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG, filename="logs/test.log", filemode="w",
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    if args.vision:
        color = ""
        for col in COLOR_LIST:
            assert color == ""
            if eval(f"args.{col}"):
                color = col
                break
        assert color != ""
        vision.start(color)
