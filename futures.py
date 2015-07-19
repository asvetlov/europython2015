import asyncio
import unittest


class TestFuture(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_fut(self):
        fut = asycnio.Future(loop=self.loop)
        self.assertFalse(fut.done())
        pass
