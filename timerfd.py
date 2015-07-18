import asyncio
import ctypes
import os
import time


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


