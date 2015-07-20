    import asyncio
    import janus

    loop = asyncio.get_event_loop()
    queue = janus.Queue(loop=loop)


    def threaded(sync_q):
        for i in range(100):
            sync_q.put(i)
        sync_q.join()


    @asyncio.coroutine
    def async_coro(async_q):
        for i in range(100):
            val = yield from async_q.get()
            assert val == i
            async_q.task_done()


    fut = loop.run_in_executor(None, threaded, queue.sync_q)
    loop.run_until_complete(async_coro(queue.async_q))
    loop.run_until_complete(fut)
