import asyncio
import json
import os
import random
import string
import websockets

PORT = int(os.environ.get("PORT", 10000))

rooms = {}  # room_id -> { "players": [], "sockets": [] }

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

async def broadcast(room_id, message):
    for ws in rooms[room_id]["sockets"]:
        await ws.send(json.dumps(message))

async def handler(ws):
    room_id = None
    player_name = None

    try:
        async for msg in ws:
            data = json.loads(msg)
            msg_type = data["type"]
            payload = data.get("data", {})

            # -------- CREATE ROOM --------
            if msg_type == "CREATE_ROOM":
                player_name = payload["player_name"]
                room_id = generate_room_id()

                rooms[room_id] = {
                    "players": [player_name],
                    "sockets": [ws]
                }

                await ws.send(json.dumps({
                    "type": "ROOM_CREATED",
                    "data": { "room_id": room_id }
                }))

                await broadcast(room_id, {
                    "type": "PLAYERS_UPDATE",
                    "data": { "players": rooms[room_id]["players"] }
                })

            # -------- JOIN ROOM --------
            elif msg_type == "JOIN_ROOM":
                player_name = payload["player_name"]
                room_id = payload["room_id"]

                if room_id not in rooms:
                    await ws.send(json.dumps({
                        "type": "ERROR",
                        "data": { "message": "Room not found" }
                    }))
                    continue

                rooms[room_id]["players"].append(player_name)
                rooms[room_id]["sockets"].append(ws)

                # 🔥 IMPORTANT PART
                await broadcast(room_id, {
                    "type": "PLAYERS_UPDATE",
                    "data": { "players": rooms[room_id]["players"] }
                })

            # -------- START GAME --------
            elif msg_type == "START_GAME":
                await broadcast(room_id, {
                    "type": "GAME_STARTED",
                    "data": {}
                })

    except websockets.ConnectionClosed:
        pass

    finally:
        # -------- CLEANUP --------
        if room_id and room_id in rooms and ws in rooms[room_id]["sockets"]:
            idx = rooms[room_id]["sockets"].index(ws)
            rooms[room_id]["sockets"].pop(idx)
            rooms[room_id]["players"].pop(idx)

            if rooms[room_id]["sockets"]:
                await broadcast(room_id, {
                    "type": "PLAYERS_UPDATE",
                    "data": { "players": rooms[room_id]["players"] }
                })
            else:
                del rooms[room_id]

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print("Server running on", PORT)
        await asyncio.Future()

asyncio.run(main())