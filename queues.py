import asyncio


@asyncio.coroutine
def putter(queue):
    for i in range(5):
        print("Put", i)
        yield from queue.put(i)
    yield from queue.put(None)


@asyncio.coroutine
def getter(queue, loop):
    while True:
        val = yield from queue.get()
        if val is not None:
            print("Get", val)
        else:
            loop.stop()
            return


loop = asyncio.get_event_loop()
queue = asyncio.Queue(loop=loop)

loop.create_task(putter(queue))
loop.create_task(getter(queue, loop))
loop.run_forever()
print("DONE")
