# -*- coding: utf-8 -*-
import logging
from functools import wraps
from time import time

__all__ = ["timer"]


def timer(method):
    @wraps(method)
    def wrap(*args, **kwargs):
        time_start = time()
        result = method(*args, **kwargs)
        time_end = time()
        logging.debug('FUNC: %r TOOK: %2.4f sec' % (method.__name__, time_end - time_start))
        return result

    return wrap
