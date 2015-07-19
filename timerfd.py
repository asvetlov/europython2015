import asyncio
import ctypes
import os
import time
import unittest
import sys


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
timerfd_settime.argtypes = [ctypes.c_int, ctypes.c_int,
                            ctypes.POINTER(itimerspec),
                            ctypes.POINTER(itimerspec)]

TFD_NONBLOCK = os.O_NONBLOCK
CLOCK_MONOTONIC = time.CLOCK_MONOTONIC


class Timer:
    def __init__(self, *, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._fileno = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK)
        self._loop = loop
        loop.add_reader(self._fileno, self._reader)
        self._waiter = None

    def close(self):
        self._loop.remove_reader(self._fileno)
        os.close(self._fileno)

    def start(self, timeout):
        assert self._waiter is None, self._waiter
        secs = int(timeout)
        nsecs = int((timeout - secs) * 1000000)
        param = itimerspec()
        param.it_value.tv_sec = secs
        param.it_value.tv_nsec = nsecs
        param.it_interval.tv_sec = 0
        param.it_interval.tv_nsec = 0
        timerfd_settime(self._fileno, 0, ctypes.byref(param), None)
        self._waiter = asyncio.Future(loop=self._loop)

    def _reader(self):
        try:
            data = os.read(self._fileno, 8)
        except BlockingIOError:
            return
        else:
            if self._waiter.done():
                return
            else:
                self._waiter.set_result(int.from_bytes(data, sys.byteorder))

    @asyncio.coroutine
    def wait(self):
        assert self._waiter is not None
        try:
            ret = yield from self._waiter
            return ret
        finally:
            self._waiter = None



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

    def test_wait(self):
        timer = Timer(loop=self.loop)
        @asyncio.coroutine
        def go():
            timer.start(0.5)
            t0 = self.loop.time()
            ret = yield from timer.wait()
            t1 = self.loop.time()
            self.assertGreater(0.5, t1-t0)
            self.assertEqual(1, ret)

        self.loop.run_until_complete(go())
        timer.close()


if __name__ == '__main__':
    unittest.main()
