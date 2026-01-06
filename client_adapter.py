import asyncio
import json
import threading
import websockets
import ssl


class TambolaClient:
    def __init__(self, uri):
        self.uri = uri
        self.ws = None
        self.listeners = {}
        self.loop = asyncio.new_event_loop()
        self.connected = False

    def connect(self):
        threading.Thread(
            target=self._run_loop,
            daemon=True
        ).start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect_forever())

    async def _connect_forever(self):
        while True:
            try:
                print("Connecting to server...")
                ssl_ctx = ssl.create_default_context() if self.uri.startswith("wss://") else None

                self.ws = await websockets.connect(
                    self.uri,
                    ssl=ssl_ctx,
                    ping_interval=20,
                    ping_timeout=20
                )

                self.connected = True
                print("Connected to server")
                await self._listen()

            except Exception as e:
                self.connected = False
                print("Connection lost, retrying...", e)
                await asyncio.sleep(5)

    async def _listen(self):
        async for message in self.ws:
            msg = json.loads(message)
            msg_type = msg.get("type")
            if msg_type in self.listeners:
                self.listeners[msg_type](msg["data"])

    def send(self, msg_type, data=None):
        if not self.connected:
            print("WS not connected yet")
            return

        payload = {"type": msg_type, "data": data or {}}
        asyncio.run_coroutine_threadsafe(
            self.ws.send(json.dumps(payload)),
            self.loop
        )

    def on(self, msg_type, callback):
        self.listeners[msg_type] = callback