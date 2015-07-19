import asyncio
import aiohttp

@asyncio.coroutine
def go(client):
    print('Get data from httpbin.org')
    resp = yield from client.get('http://httpbin.org/get')
    print('Reponse code', resp.status)
    text = yield from resp.text()
    print(text)
    yield from resp.release()
    print("-"*60)

@asyncio.coroutine
def go_with_timeout(client):
    print('Get data from httpbin.org with timeout')
    try:
        coro = client.get('http://httpbin.org/delay/10')
        yield from asyncio.wait_for(coro, 2)
    except asyncio.TimeoutError:
        print("Timeout after waiting for 2 minutes")
    else:
        print("No timeout exception, should never happen")


loop = asyncio.get_event_loop()
client = aiohttp.ClientSession()
loop.run_until_complete(go(client))
loop.run_until_complete(go_with_timeout(client))
client.close()
print("DONE")
