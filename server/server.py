import asyncio
import json
import random
import os
import websockets

PORT = int(os.environ.get("PORT", 10000))

rooms = {}

# ---------------- UTIL ----------------

def generate_room_id():
    return ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))

def generate_ticket():
    return random.sample(range(1, 101), 15)

async def broadcast(room_id, message):
    for ws in rooms[room_id]["players"]:
        await ws.send(json.dumps(message))

# ---------------- GAME LOGIC ----------------

async def draw_numbers(room_id):
    room = rooms[room_id]
    numbers = list(range(1, 101))
    random.shuffle(numbers)

    for num in numbers:
        await asyncio.sleep(3)

        room["drawn"].add(num)

        for p in room["players"].values():
            if num in p["ticket"] and num not in p["marked"]:
                p["marked"].add(num)
                p["score"] += 2

        scores = {p["name"]: p["score"] for p in room["players"].values()}

        await broadcast(room_id, {
            "type": "NUMBER_DRAWN",
            "data": {
                "number": num,
                "scores": scores
            }
        })

    leaderboard = sorted(
        room["players"].values(),
        key=lambda x: x["score"],
        reverse=True
    )

    await broadcast(room_id, {
        "type": "GAME_OVER",
        "data": {
            "leaderboard": [
                {"name": p["name"], "score": p["score"]}
                for p in leaderboard
            ]
        }
    })

# ---------------- WS HANDLER ----------------

async def handler(ws):
    room_id = None

    async for msg in ws:
        payload = json.loads(msg)
        t = payload["type"]
        data = payload.get("data", {})

        # CREATE ROOM
        if t == "CREATE_ROOM":
            room_id = generate_room_id()
            rooms[room_id] = {
                "players": {},
                "drawn": set()
            }

            ticket = generate_ticket()
            rooms[room_id]["players"][ws] = {
                "name": data["player_name"],
                "ticket": ticket,
                "marked": set(),
                "score": 0
            }

            await ws.send(json.dumps({
                "type": "ROOM_CREATED",
                "data": {"room_id": room_id}
            }))

            await ws.send(json.dumps({
                "type": "TICKET_ASSIGNED",
                "data": {"ticket": ticket}
            }))

        # JOIN ROOM
        elif t == "JOIN_ROOM":
            room_id = data["room_id"]
            if room_id not in rooms:
                continue

            ticket = generate_ticket()
            rooms[room_id]["players"][ws] = {
                "name": data["player_name"],
                "ticket": ticket,
                "marked": set(),
                "score": 0
            }

            await ws.send(json.dumps({
                "type": "TICKET_ASSIGNED",
                "data": {"ticket": ticket}
            }))

            players = [p["name"] for p in rooms[room_id]["players"].values()]

            await broadcast(room_id, {
                "type": "PLAYER_LIST",
                "data": {"players": players}
            })

        # START GAME
        elif t == "START_GAME":
            asyncio.create_task(draw_numbers(room_id))

# ---------------- START ----------------

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print("WebSocket running on", PORT)
        await asyncio.Future()

asyncio.run(main())