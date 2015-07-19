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


loop = asyncio.get_event_loop()
client = aiohttp.ClientSession()
loop.run_until_complete(go(client))
client.close()
print("DONE")
