import asyncio
import json
import threading
import websockets


class TambolaClient:
    def __init__(self, uri):
        self.uri = uri
        self.ws = None
        self.listeners = {}
        self.loop = asyncio.new_event_loop()

    # ---------------- START CLIENT ----------------
    def connect(self):
        threading.Thread(
            target=self._run_loop,
            daemon=True
        ).start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect())

    async def _connect(self):
        try:
            async with websockets.connect(self.uri) as websocket:
                self.ws = websocket
                await self._listen()
        except Exception as e:
            print("WebSocket error:", e)

    # ---------------- LISTEN ----------------
    async def _listen(self):
        async for message in self.ws:
            msg = json.loads(message)
            msg_type = msg.get("type")

            if msg_type in self.listeners:
                self.listeners[msg_type](msg["data"])

    # ---------------- SEND ----------------
    def send(self, msg_type, data=None):
        if not self.ws:
            print("WS not connected yet")
            return

        payload = {
            "type": msg_type,
            "data": data or {}
        }

        asyncio.run_coroutine_threadsafe(
            self.ws.send(json.dumps(payload)),
            self.loop
        )

    # ---------------- EVENT REGISTER ----------------
    def on(self, msg_type, callback):
        self.listeners[msg_type] = callback
