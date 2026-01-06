import asyncio
import json
import os
import random
import string
import websockets

PORT = int(os.environ.get("PORT", 10000))

rooms = {}

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

            if msg_type == "CREATE_ROOM":
                player_name = payload["player_name"]
                room_id = generate_room_id()
                rooms[room_id] = {
                    "players": [player_name],
                    "sockets": [ws],
                    "tickets": {},
                    "numbers_drawn": set()
                }
                await ws.send(json.dumps({
                    "type": "ROOM_CREATED",
                    "data": {"room_id": room_id}
                }))
                await broadcast(room_id, {
                    "type": "PLAYERS_UPDATE",
                    "data": {"players": rooms[room_id]["players"]}
                })

            elif msg_type == "JOIN_ROOM":
                player_name = payload["player_name"]
                room_id = payload["room_id"]
                rooms[room_id]["players"].append(player_name)
                rooms[room_id]["sockets"].append(ws)
                await broadcast(room_id, {
                    "type": "PLAYERS_UPDATE",
                    "data": {"players": rooms[room_id]["players"]}
                })

            elif msg_type == "START_GAME":
                room = rooms[room_id]
                for i, player in enumerate(room["players"]):
                    ticket = generate_ticket()
                    room["tickets"][player] = ticket
                    await room["sockets"][i].send(json.dumps({
                        "type": "TICKET_ASSIGNED",
                        "data": {"ticket": ticket}
                    }))
                await broadcast(room_id, {
                    "type": "GAME_STARTED",
                    "data": {}
                })

            elif msg_type == "DRAW_NUMBER":
                room = rooms[room_id]
                if len(room["numbers_drawn"]) == 90:
                    continue
                num = random.randint(1, 90)
                while num in room["numbers_drawn"]:
                    num = random.randint(1, 90)
                room["numbers_drawn"].add(num)
                await broadcast(room_id, {
                    "type": "NUMBER_DRAWN",
                    "data": {"number": num}
                })

    except websockets.ConnectionClosed:
        pass

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())