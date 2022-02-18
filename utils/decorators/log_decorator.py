#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import wraps
import time

from utils.logger import Logger


def fun_entry_exit(*, entry=True, exit=True):

    def wrapper(func):
        name = func.__name__

        @wraps(func)
        def wrapped(*args, **kwargs):
            if entry:
                Logger.info("Entering '{}' (args={}, kwargs={})".format(name, args, kwargs))
            result = func(*args, **kwargs)
            if exit:
                Logger.info("Exiting '{}' (result={})".format(name, result))
            return result

        return wrapped

    return wrapper


def fun_timeit(func):

    @wraps(func)
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        Logger.info("Function '{}' executed in {:f} s".format(func.__name__, end - start))
        return result

    return wrapped
