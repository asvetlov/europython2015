import asyncio
import random


@asyncio.coroutine
def task(num, loop):
    for ch in 'abcdef':
        print('Thread', num, '->', ch)
        yield from asyncio.sleep(random.random() * 0.2, loop=loop)


loop = asyncio.get_event_loop()
tasks = []
for i in range(5):
    tasks.append(loop.create_task(task(i, loop)))

wait_all = asyncio.gather(*tasks, loop=loop)
loop.run_until_complete(wait_all)
