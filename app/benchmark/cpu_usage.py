# -*- coding: utf-8 -*-
import cProfile
import pstats
from functools import wraps
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
