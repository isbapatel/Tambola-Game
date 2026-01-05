import asyncio
import json
import os
import random
import time
import pathlib
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import websockets

# ================= CONFIG =================
PORT = int(os.environ.get("PORT", 10000))
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"

ROOMS = {}
NUMBERS = list(range(1, 101))
GAME_DURATION = 180
DRAW_INTERVAL = 2


# ================= GAME LOGIC =================
class Room:
    def __init__(self, room_id, host_ws, host_name):
        self.room_id = room_id
        self.host = host_ws
        self.players = {host_ws: host_name}
        self.scores = {host_name: 0}
        self.used_numbers = set()
        self.started = False


async def broadcast(room, message):
    for ws in list(room.players.keys()):
        try:
            await ws.send(json.dumps(message))
        except:
            pass


async def game_loop(room):
    start = time.time()

    while time.time() - start < GAME_DURATION:
        await asyncio.sleep(DRAW_INTERVAL)
        remaining = list(set(NUMBERS) - room.used_numbers)
        if not remaining:
            break

        number = random.choice(remaining)
        room.used_numbers.add(number)

        for name in room.scores:
            room.scores[name] += 2

        await broadcast(room, {
            "type": "NUMBER_DRAWN",
            "data": {
                "number": number,
                "scores": room.scores
            }
        })

    leaderboard = sorted(room.scores.items(), key=lambda x: x[1], reverse=True)
    await broadcast(room, {
        "type": "GAME_OVER",
        "data": leaderboard
    })


# ================= WEBSOCKET =================
async def ws_handler(ws):
    try:
        async for message in ws:
            msg = json.loads(message)
            t = msg.get("type")
            d = msg.get("data", {})

            room = None
            for r in ROOMS.values():
                if ws in r.players:
                    room = r
                    break

            if t == "CREATE_ROOM":
                rid = ''.join(random.choices("ABCDEFGH123456789", k=6))
                ROOMS[rid] = Room(rid, ws, d["player_name"])
                await ws.send(json.dumps({
                    "type": "ROOM_CREATED",
                    "data": {"room_id": rid}
                }))

            elif t == "JOIN_ROOM":
                room = ROOMS.get(d["room_id"])
                if room:
                    room.players[ws] = d["player_name"]
                    room.scores[d["player_name"]] = 0

            elif t == "START_GAME":
                if room and ws == room.host and not room.started:
                    room.started = True
                    await broadcast(room, {"type": "GAME_STARTED", "data": {}})
                    asyncio.create_task(game_loop(room))

    except:
        pass


# ================= HTTP SERVER =================
class WebHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/" or path == "":
            return str(WEB_DIR / "index.html")
        return str(WEB_DIR / path.lstrip("/"))


def start_http():
    httpd = HTTPServer(("0.0.0.0", PORT), WebHandler)
    print(f"HTTP server running on port {PORT}")
    httpd.serve_forever()


# ================= MAIN =================
async def start_ws():
    async with websockets.serve(ws_handler, "0.0.0.0", PORT):
        print(f"WebSocket running on port {PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    threading.Thread(target=start_http, daemon=True).start()
    asyncio.run(start_ws())