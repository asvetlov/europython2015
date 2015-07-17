import asyncio
import collections
import hiredis
import unittest


@asyncio.coroutine
def connect(*, host='127.0.0.1', port=6379, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    redis = Redis(host, port, loop)
    yield from redis._connect()
    return redis


class Redis:

    def __init__(self, host, port, loop):
        # private API!
        self._host = host
        self._port = port
        self._loop = loop
        self._reader = None
        self._writer = None
        self._task = None
        self._parser = hiredis.Reader()
        self._queue = collections.deque()


    def close(self):
        pass

    @asyncio.coroutine
    def wait_closed(self):
        pass

    @asyncio.coroutine
    def execute(self, cmd, *args):
        cmd = cmd.upper().strip()
        fut = asyncio.Future(loop=self._loop)
        self._queue.append(fut)
        self._writer.write(packet)
        return fut

    @asyncio.coroutine
    def _connect(self):
        r, w = yield from asyncio.open_connection(host=self._host,
                                                  port=self._port,
                                                  loop=self._loop)
        self._reader, self._writer  = r, w

    @asyncio.coroutine
    def _read_task(self):
        while not self._reader.at_eof():
            try:
                data = yield from self._reader.read(1024)
            except asyncio.CancelledError:
                break
            self._parser.feed(data)
            while True:
                try:
                    answer = self._parser.get()
                except hiredis.ProtocolError:
                    self.close()
                    return
                if not answer:
                    continue
                waiter = self._queue.popleft()
                if waiter.done():
                    continue
                if isinstance(answer, hiredis.RedisError):
                    waiter.set_exception(answer)
                else:
                    waiter.set_result(answer)



class TestRedis(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.redis = self.loop.run_until_complete(connect(loop=self.loop))

    def tearDown(self):
        self.redis.close()
        self.loop.run_until_complete(self.redis.wait_closed())
        self.loop.close()

    def test_alone_get(self):
        @asyncio.coroutine
        def go():
            ret = yield from self.redis.execute('get', 'missing_key')
            self.assertEqual(None, ret)

        self.loop.run_until_complete(go())


if __name__ == '__main__':
    unittest.main()
