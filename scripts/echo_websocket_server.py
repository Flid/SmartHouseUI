#!/usr/bin/env python
import click
import asyncio
import websockets


async def hello(websocket, path):
    while True:
        try:
            body = await websocket.recv()
            print(f'Received request for {path}, body={body!r}')
        except websockets.exceptions.ConnectionClosed:
            print('Connction closed')
            return


@click.command()
@click.option('--port', type=int, default=8765)
def main(port):
    click.echo(f'Starting a server on port {port}...')
    start_server = websockets.serve(hello, '0.0.0.0', port)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
