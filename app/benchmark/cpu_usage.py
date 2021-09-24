# -*- coding: utf-8 -*-
import cProfile
import pstats
from functools import wraps
from pstats import SortKey

__all__ = ["cpu_usage"]


def cpu_usage(method):
    @wraps(method)
    def wrap(*args, **kwargs):
        with cProfile.Profile() as profile:
            result = method(*args, **kwargs)
        stats = pstats.Stats(profile).sort_stats(SortKey.CUMULATIVE)
        stats.print_stats()
        return result

    return wrap
