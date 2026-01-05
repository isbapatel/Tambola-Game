import asyncio
import json
import os
import random
import time
import websockets

# ================= CONFIG =================
PORT = int(os.environ.get("PORT", 10000))

ROOMS = {}
NUMBERS = list(range(1, 101))
GAME_DURATION = 180      # seconds
DRAW_INTERVAL = 2        # seconds


# ================= ROOM =================
class Room:
    def __init__(self, room_id, host_ws, host_name):
        self.room_id = room_id
        self.host = host_ws
        self.players = {host_ws: host_name}
        self.scores = {host_name: 0}
        self.used_numbers = set()
        self.started = False


# ================= HELPERS =================
async def broadcast(room, payload):
    dead = []
    for ws in room.players:
        try:
            await ws.send(json.dumps(payload))
        except:
            dead.append(ws)

    for ws in dead:
        room.players.pop(ws, None)


async def game_loop(room):
    start_time = time.time()

    while time.time() - start_time < GAME_DURATION:
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
            msg_type = msg.get("type")
            data = msg.get("data", {})

            current_room = None
            for room in ROOMS.values():
                if ws in room.players:
                    current_room = room
                    break

            if msg_type == "CREATE_ROOM":
                room_id = ''.join(random.choices("ABCDEFGH123456789", k=6))
                ROOMS[room_id] = Room(room_id, ws, data["player_name"])

                await ws.send(json.dumps({
                    "type": "ROOM_CREATED",
                    "data": {"room_id": room_id}
                }))

            elif msg_type == "JOIN_ROOM":
                room = ROOMS.get(data["room_id"])
                if room:
                    room.players[ws] = data["player_name"]
                    room.scores[data["player_name"]] = 0

                    await broadcast(room, {
                        "type": "PLAYER_JOINED",
                        "data": {"players": list(room.scores.keys())}
                    })

            elif msg_type == "START_GAME":
                if current_room and ws == current_room.host and not current_room.started:
                    current_room.started = True
                    await broadcast(current_room, {
                        "type": "GAME_STARTED",
                        "data": {}
                    })
                    asyncio.create_task(game_loop(current_room))

    except:
        pass


# ================= MAIN =================
async def main():
    print(f"WebSocket server running on port {PORT}")
    async with websockets.serve(ws_handler, "0.0.0.0", PORT):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())