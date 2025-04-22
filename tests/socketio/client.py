import asyncio
import socketio
import socketio.exceptions


async def pong_cb(*args, **kwargs):
    print(args, kwargs)


async def amain():
    async with socketio.AsyncSimpleClient() as sio:
        await sio.connect(
            "http://localhost:8015",
            namespace="/user",
            socketio_path="/ws/socket.io",
            auth=dict(
                token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc19hZG1pbiI6dHJ1ZSwiaXNzIjoiYXBwX25hbWUiLCJzdWIiOiJhZG1pbiIsImF1ZCI6ImFwcF9uYW1lIiwianRpIjoiODA3M2VhOTUtOTQyYS00OTZjLWFlNzUtM2ZlOTRlZDZmNjdhIiwidHR5cGUiOjEsImV4cCI6MTc0NTM0MTE3OSwiaWF0IjoxNzQ1MzM5Mzc5fQ.lPKysMOzxwW3AXNtOsBKdrScJKGW2qlXNvVockBUFQE"
            ),
            transports=["websocket"],
        )
        print("pre-connected")
        event = "ping"
        data = None
        data = "ping"
        count = 0
        while True:
            await sio.connected_event.wait()
            if not sio.connected or count >= 2:
                raise socketio.exceptions.DisconnectedError()
            print("connected")
            count += 1

            try:
                await sio.client.emit(
                    event, data, namespace=sio.namespace, callback=pong_cb
                )
                await asyncio.sleep(2)
            except socketio.exceptions.SocketIOError:
                pass


def main():
    asyncio.run(amain())


if __name__ == "__main__":
    main()
