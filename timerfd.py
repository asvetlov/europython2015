import asyncio
import ctypes
import os
import time
import unittest


clib = ctypes.CDLL('libc.so.6', use_errno=True)


class timespec(ctypes.Structure):
    _fields_ = [('tv_sec', ctypes.c_long),
                ('tv_nsec', ctypes.c_long)]


class itimerspec(ctypes.Structure):
    _fields_ = [('it_interval', timespec),
                ('it_value', timespec)]

timerfd_create = clib.timerfd_create
timerfd_create.argtypes = [ctypes.c_int, ctypes.c_int]

timerfd_settime = clib.timerfd_settime
timerfd_settime = [ctypes.c_int, ctypes.c_int,
                   ctypes.POINTER(itimerspec), ctypes.POINTER(itimerspec)]

TFD_NONBLOCK = os.O_NONBLOCK
CLOCK_MONOTONIC = time.CLOCK_MONOTONIC


class Timer:
    def __init__(self, *, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._fileno = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK)
        self._loop = loop

    def close(self):
        os.close(self._fileno)

    def start(self, timeout):
        secs = int(timeout)
        nsecs = int((timeout - secs) * 1000000)
        ts = timespec()
        ts.tv_sec = secs
        ts.tv_nsec = nsecs
        timerfd_settime(self._fileno, 0, ctypes.byref(ts), None)



class TestTimer(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_ctor(self):
        timer = Timer(loop=self.loop)
        self.assertIs(self.loop, timer._loop)
        timer.close()


if __name__ == '__main__':
    unittest.main()
