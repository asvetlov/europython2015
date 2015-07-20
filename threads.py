import asyncio


def threaded(arg):
    return arg + 1



loop = asyncio.get_event_loop()
ret = loop.run_in_executor(None, threaded, 1)
print(ret)
print(loop.run_until_complete(ret))
loop.close()
