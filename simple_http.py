import asyncio


@asyncio.coroutine
def handle(reader, writer):
    data = ''
    while '\r\n\r\n' not in data:
        chunk = yield from reader.read(1024)
        data += chunk.decode('utf-8')

    query = data.splitlines()
    method, path, version = query[0].split(None, 2)
    resp = "Response on {method} {path}".format(method=method, path=path)
    bresp = resp.encode('utf-8')
    lresp = len(bresp)
    hdrs = "HTTP/1.0 200 OK\r\nContent-Length: {}\r\n\r\n".format(lresp)
    writer.write(hdrs.encode('utf-8'))
    writer.write(bresp)
    yield from writer.drain()
    writer.close()



loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle, '127.0.0.1', 8000, loop=loop)
server = loop.run_until_complete(coro)

print("Serving on http://{0[0]}:{0[1]}/".format(
    server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass


server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
