import asyncio
import json
import os
import random
import string
import websockets

PORT = int(os.environ.get("PORT", 10000))

rooms = {}  
# room_id -> {
#   players: [],
#   sockets: [],
#   tickets: {}   # player_name -> ticket
# }

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


def generate_ticket():
    ticket = [[0]*9 for _ in range(3)]

    for row in range(3):
        cols = random.sample(range(9), 5)
        for col in cols:
            start = col * 10 + 1
            end = 90 if col == 8 else start + 9
            ticket[row][col] = random.randint(start, end)

    return ticket


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
                    "sockets": [ws],
                    "tickets": {}
                }

                await ws.send(json.dumps({
                    "type": "ROOM_CREATED",
                    "data": { "room_id": room_id }
                }))

                await broadcast_players(room_id)

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

                await broadcast_players(room_id)

            # -------- START GAME --------
            elif msg_type == "START_GAME":
                room = rooms[room_id]

                # generate tickets
                for i, player in enumerate(room["players"]):
                    ticket = generate_ticket()
                    room["tickets"][player] = ticket

                    await room["sockets"][i].send(json.dumps({
                        "type": "TICKET_ASSIGNED",
                        "data": { "ticket": ticket }
                    }))

                # notify all game started
                for s in room["sockets"]:
                    await s.send(json.dumps({
                        "type": "GAME_STARTED",
                        "data": {}
                    }))

    except websockets.ConnectionClosed:
        pass

    finally:
        if room_id and room_id in rooms and ws in rooms[room_id]["sockets"]:
            idx = rooms[room_id]["sockets"].index(ws)
            rooms[room_id]["sockets"].pop(idx)
            rooms[room_id]["players"].pop(idx)

            if rooms[room_id]["sockets"]:
                await broadcast_players(room_id)
            else:
                del rooms[room_id]


async def broadcast_players(room_id):
    players = rooms[room_id]["players"]
    for ws in rooms[room_id]["sockets"]:
        await ws.send(json.dumps({
            "type": "PLAYERS_UPDATE",
            "data": { "players": players }
        }))


async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print("Server running on", PORT)
        await asyncio.Future()

asyncio.run(main())