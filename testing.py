import asyncio
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_sleep(self):
        @asyncio.coroutine
        def go():
           t0 = self.loop.time()
           yield from asyncio.sleep(0.5, loop=self.loop)
           t1 = self.loop.time()
           self.assertTrue(0.4 <= t1-t0 <= 0.6, t1-t0)

        self.loop.run_until_complete(go())


if __name__ == '__main__':
    unittest.main()
