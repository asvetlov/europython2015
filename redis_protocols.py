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


class _RedisProto(asyncio.Protocol):

    def __init__(self, redis):
        self.transport = None
        self.parser = hiredis.Reader()
        self.queue = collections.deque()
        self.redis = redis

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport = None
        self.redis._protocol = None

    def data_received(self, data):
        self.parser.feed(data)
        while True:
            try:
                answer = self.parser.gets()
            except hiredis.ProtocolError:
                self.transport.close()
                return
            if answer == False:
                break
            waiter = self.queue.popleft()
            if waiter.done():
                continue
            if isinstance(answer, hiredis.ReplyError):
                waiter.set_exception(answer)
            else:
                waiter.set_result(answer)


class Redis:

    def __init__(self, host, port, loop):
        # private API!
        self._host = host
        self._port = port
        self._loop = loop
        self._transport = None
        self._protocol = None
        self._closed = asyncio.Future(loop=loop)

    def close(self):
        if self._protocol is None:
            return
        self._transport.close()
        while self._protocol.queue:
            waiter = self._protocol.queue.popleft()
            waiter.cancel()

    @asyncio.coroutine
    def wait_closed(self):
        if self._protocol is None:
            return
        yield from self._closed

    def execute(self, cmd, *args):
        fut = asyncio.Future(loop=self._loop)
        self._protocol.queue.append(fut)
        buf = bytearray()

        def add(data):
            buf.extend(data + b'\r\n')

        args = (cmd,) + args

        add(b'*' + str(len(args)).encode('utf-8'))
        for arg in args:
            assert isinstance(arg, bytes)
            add(b'$' + str(len(arg)).encode('utf-8'))
            add(arg)

        self._transport.write(buf)
        return fut

    @asyncio.coroutine
    def _connect(self):
        tr, pr = yield from self._loop.create_connection(
            lambda: _RedisProto(self),
            host=self._host,
            port=self._port)
        self._transport = tr
        self._protocol = pr



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
