import asyncio


def f(lock):
    yield from lock.acquire()
    try:
        yield from asyncio.sleep(0.1)
    finally:
        lock.release()


loop = asyncio.get_event_loop()
lock = asyncio.Lock()

print('pass 1')
loop.run_until_complete(f(lock))


def g(lock):
    with (yield from lock):
        yield from asyncio.sleep(0.1)


print('pass 2')
loop.run_until_complete(g(lock))
