import asyncio
from aiohttp.web import Application, Response


@asyncio.coroutine
def simple(request):
    return Response(text='Text')


@asyncio.coroutine
def init(loop):
    app = Application(loop=loop)
    app.router.add_route('GET', '/', simple)

    handler = app.make_handler()
    srv = yield from loop.create_server(handler, '127.0.0.1', 8080)
    print("Server started at http://127.0.0.1:8080")
    return srv, handler

loop = asyncio.get_event_loop()
srv, handler = loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(handler.finish_connections())
    srv.close()
    loop.run_until_complete(srv.wait_closed())
