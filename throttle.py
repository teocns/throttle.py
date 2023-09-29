"""
    Helper class and functions to rate limiting function calls with Python Decorators
"""
# ----------------------------------------------------------------------------
# Import section for Python 2 and 3 compatible code
# from __future__ import absolute_import, division, print_function, unicode_literals
from __future__ import division    # This way: 3 / 2 == 1.5; 3 // 2 == 1

# ----------------------------------------------------------------------------
# Import section
#
import sys
import logging
import multiprocessing
import time
from functools import wraps


# -----------------------------------------------------------------------------
# class LastTime to be used with throttled
#
class LastTime:
    """
        >>> import throttled as rt
        >>> a = rt.LastTime()
        >>> a.add_cnt()
        >>> a.get_cnt()
        1
        >>> a.add_cnt()
        >>> a.get_cnt()
        2
    """

    def __init__(self, name='LT'):
        # Init variables to None
        self.name = name
        self.ratelock = None
        self.cnt = None
        self.last_time_called = None

        # Instantiate control variables
        self.ratelock = multiprocessing.Lock()
        self.cnt = multiprocessing.Value('i', 0)
        self.last_time_called = multiprocessing.Value('d', 0.0)
        self.lock_acquired = False
        logging.debug('\t__init__: name=[{!s}]'.format(self.name))

    def acquire(self):
        self.ratelock.acquire()
        self.lock_acquired = True

    def release(self):
        if self.lock_acquired:
            self.lock_acquired = False
            self.ratelock.release()

    def set_last_time_called(self):
        self.last_time_called.value = time.time()
        # self.debug('set_last_time_called')

    def get_last_time_called(self):
        return self.last_time_called.value

    def add_cnt(self):
        self.cnt.value += 1

    def get_cnt(self):
        return self.cnt.value

    def debug(self, debugname='LT'):
        now=time.time()
        logging.debug('___Rate name:[{!s}] '
                      'debug=[{!s}] '
                      '\n\t        cnt:[{!s}] '
                      '\n\tlast_called:{!s} '
                      '\n\t  timenow():{!s} '
                      .format(self.name,
                              debugname,
                              self.cnt.value,
                              time.strftime(
                                '%T.{}'
                                .format(str(self.last_time_called.value -
                                            int(self.last_time_called.value))
                                            .split('.')[1][:3]),
                                time.localtime(self.last_time_called.value)),
                              time.strftime(
                                '%T.{}'
                                .format(str(now -
                                            int(now))
                                            .split('.')[1][:3]),
                                time.localtime(now))))






# -----------------------------------------------------------------------------
# throttled
#
# retries execution of a function
def throttled(max_per_second, return_if_throttled=False,*,key=None):

    min_interval = 1.0 / max_per_second
    LT_cache = {}  # Cache for LastTime objects

    def decorate(func):
        @wraps(func)
        def throttled_function(*args, **kwargs):

            k = key(*args, **kwargs) if key else 'throttled'
            LT = LT_cache.get(k, None)
            if LT is None:
                LT = LastTime()
                LT_cache[k] = LT

            try:
                LT.acquire()
                current_time = time.time()

                if LT.get_last_time_called() == 0:
                    LT.set_last_time_called()

                elapsed = current_time - LT.get_last_time_called()
                left_to_wait = min_interval - elapsed

                if left_to_wait > 0:
                    if return_if_throttled:
                        return LT.release()

                    time.sleep(left_to_wait)

                ret = func(*args, **kwargs)
                LT.set_last_time_called()

            except Exception as ex:
                sys.stderr.write('Exception on throttled_function: {}\n'.format(ex))
                raise
            finally:
                LT.release()
            
            return ret

        return throttled_function

    return decorate



"""
    Authored by oPromessa, 2017
    Published on https://github.com/oPromessa/flickr-uploader/
    Inspired by: https://gist.github.com/gregburek/1441055
    Extended by teocns, 2023
"""
