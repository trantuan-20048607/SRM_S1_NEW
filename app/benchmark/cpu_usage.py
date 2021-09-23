# -*- coding: utf-8 -*-
from functools import wraps
import cProfile
import pstats
import io
from pstats import SortKey

__all__ = ["cpu_usage"]


def cpu_usage(func):
    @wraps(func)
    def wrap(*args, **kw):
        with cProfile.Profile() as pr:
            result = func(*args, **kw)
        ps = pstats.Stats(pr).sort_stats(SortKey.CUMULATIVE)
        ps.print_stats()
        return result

    return wrap
