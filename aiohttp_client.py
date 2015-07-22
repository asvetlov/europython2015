import asyncio
import aiohttp
import binascii


@asyncio.coroutine
def get(client):
    print('Get data from httpbin.org')
    resp = yield from client.get('http://httpbin.org/get')
    print('Reponse code', resp.status)
    text = yield from resp.text()
    print(text)
    yield from resp.release()


@asyncio.coroutine
def get_with_timeout(client):
    print('Get data from httpbin.org with timeout')
    try:
        coro = client.get('http://httpbin.org/delay/10')
        yield from asyncio.wait_for(coro, 2)
    except asyncio.TimeoutError:
        print("Timeout after waiting for 2 seconds")
    else:
        print("No timeout exception, should never happen")


@asyncio.coroutine
def get_random_data(client, num):
    resp = yield from client.get('http://httpbin.org/bytes/16')
    data = yield from resp.read()
    print("Data {}: {}".format(num, binascii.hexlify(data).decode('utf-8')))
    yield from resp.release()


@asyncio.coroutine
def get_multiple(client):
    print("Fetch by 10 parallel requests")
    coros = []
    for i in range(10):
        coros.append(get_random_data(client, i))

    yield from asyncio.gather(*coros)


loop = asyncio.get_event_loop()
client = aiohttp.ClientSession()

loop.run_until_complete(get(client))
print("-"*60)

loop.run_until_complete(get_with_timeout(client))
print("-"*60)

loop.run_until_complete(get_multiple(client))

client.close()
print("DONE")
