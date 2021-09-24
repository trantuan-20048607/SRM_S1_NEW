# -*- coding: utf-8 -*-
import logging
from functools import wraps
from time import time

__all__ = ["timing"]


def timing(func):
    @wraps(func)
    def wrap(*args, **kw):
        time_start = time()
        result = func(*args, **kw)
        time_end = time()
        logging.debug('FUNC: %r TOOK: %2.4f sec' % (func.__name__, time_end - time_start))
        return result

    return wrap
