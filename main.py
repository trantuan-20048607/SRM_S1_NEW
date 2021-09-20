# -*- coding: utf-8 -*-
import argparse
import logging
from app.core.container import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", default=False, help="DEBUG MODE", action="store_true")
    parser.add_argument("-r", "--red", default=False, help="RED MODE", action="store_true")
    parser.add_argument("-b", "--blue", default=False, help="BLUE MODE", action="store_true")
    parser.add_argument("--record", default=False, help="RECORDING VIDEO", action="store_true")
    args = parser.parse_args()
    assert args.red ^ args.blue
    assert args.debug ^ args.record
    color = ""
    if args.red:
        color = "red"
    elif args.blue:
        color = "blue"
    logging.basicConfig(level={True: logging.DEBUG, False: logging.INFO}[args.debug],
                        filename="logs/app.log", filemode='w',
                        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    app = Container(color, args.debug, args.record)
    app.start()
