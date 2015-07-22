import asyncio


@asyncio.coroutine
def normal():
    fut = asyncio.Future()
    print(fut)

    fut.set_result(123)
    print(fut)
    print(fut.result(), fut.exception())
    ret = yield from fut
    print(ret)


@asyncio.coroutine
def exceptions():
    fut = asyncio.Future()
    print(fut)
    fut.set_exception(ValueError("Failure"))
    print(fut)
    print(fut.exception())
    try:
        yield from fut
    except Exception as exc:
        print(exc)


def callbacks():
    fut = asyncio.Future()

    def cb(f):
        print('Callback', f)
        print(f.result())

    fut.add_done_callback(cb)

    fut.set_result(123)

    loop.stop()
    loop.run_forever()


loop = asyncio.get_event_loop()
#print("---- Normal ----")
#loop.run_until_complete(normal())
print("---- Exceptions ----")
loop.run_until_complete(exceptions())
#print("---- Callbacks ----")
#callbacks()
