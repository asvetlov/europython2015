import asyncio
import aiohttp


def fetch_url(client, url):
    resp = yield from client.get(url)
    try:
        text = yield from resp.text()
        return text
    finally:
        yield from resp.release()


def fetch(client, url, retries=5, timeout=30):
    for i in range(retries):
        ret = yield from asyncio.wait_for(fetch_url(client, url),
                                          timeout)
        return ret


loop = asyncio.get_event_loop()
client = aiohttp.ClientSession()
try:
    txt = loop.run_until_complete(fetch(client, 'http://httpbin.org/get'))
    print(txt)
finally:
    client.close()
