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
        if self._task is None:
            return
        self._writer.close()
        self._task.cancel()
        while self._queue:
            waiter = self._queue.popleft()
            waiter.cancel()

    @asyncio.coroutine
    def wait_closed(self):
        if self._task is None:
            return
        yield from self._task
        self._task = None

    def execute(self, cmd, *args):
        fut = asyncio.Future(loop=self._loop)
        self._queue.append(fut)
        buf = bytearray()

        def add(data):
            buf.extend(data + b'\r\n')

        args = (cmd,) + args

        add(b'*' + str(len(args)).encode('utf-8'))
        for arg in args:
            assert isinstance(arg, bytes)
            add(b'$' + str(len(arg)).encode('utf-8'))
            add(arg)

        self._writer.write(buf)
        return fut

    @asyncio.coroutine
    def _connect(self):
        r, w = yield from asyncio.open_connection(host=self._host,
                                                  port=self._port,
                                                  loop=self._loop)
        self._reader, self._writer  = r, w
        self._task = self._loop.create_task(self._read_task())

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
                    answer = self._parser.gets()
                except hiredis.ProtocolError:
                    self.close()
                    return
                if answer == False:
                    break
                waiter = self._queue.popleft()
                if waiter.done():
                    continue
                if isinstance(answer, hiredis.ReplyError):
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

    def test_get_missing_key(self):
        @asyncio.coroutine
        def go():
            ret = yield from self.redis.execute(b'GET', b'missing_key')
            self.assertIsNone(ret)

        self.loop.run_until_complete(go())

    def test_set_get(self):
        @asyncio.coroutine
        def go():
            yield from self.redis.execute(b'SET', b'key', b'val')
            ret = yield from self.redis.execute(b'GET', b'key')
            self.assertEqual(b'val', ret)

        self.loop.run_until_complete(go())


if __name__ == '__main__':
    unittest.main()
