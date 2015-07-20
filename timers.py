import asyncio


@asyncio.coroutine
def coro(loop):
    yield from asyncio.sleep(0.5, loop=loop)
    print("Called coro")



loop = asyncio.get_event_loop()

def cb(arg):
    print("Called", arg)


loop.create_task(coro(loop))
loop.call_soon(cb, 1)
loop.call_later(0.4, cb, 2)
loop.call_at(loop.time() + 0.6, cb, 3)
loop.call_later(0.7, loop.stop)


loop.run_forever()
print("DONE")
