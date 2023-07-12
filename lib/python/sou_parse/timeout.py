# # By user2283347 on SO https://stackoverflow.com/questions/366682/how-to-limit-execution-time-of-a-function-call
# from contextlib import contextmanager
# import threading
# import _thread

# class TimeoutException(Exception):
#     def __init__(self, msg=''):
#         self.msg = msg

# @contextmanager
# def time_limit(seconds, msg=''):
#     timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
#     timer.start()
#     try:
#         yield
#     except KeyboardInterrupt:
#         raise TimeoutException("Timed out for operation {}".format(msg))
#     finally:
#         # if the action ends in specified time, timer is canceled
#         timer.cancel()

# By acushner on SO https://stackoverflow.com/questions/21827874/timeout-a-function-windows
from threading import Thread
import functools


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e

            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret

        return wrapper

    return deco
