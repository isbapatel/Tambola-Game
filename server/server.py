import asyncio
import json
import random
import time
import websockets

rooms = {}

GAME_DURATION = 180       # seconds
DRAW_INTERVAL = 2         # seconds
NUMBER_POOL = list(range(1, 101))


async def safe_send(ws, msg):
    try:
        await ws.send(json.dumps(msg))
    except:
        pass


class Room:
    def __init__(self, room_id, host_ws, host_name):
        self.room_id = room_id
        self.host = host_ws
        self.players = {host_ws: host_name}
        self.player_numbers = {}
        self.player_rows = {}
        self.scores = {host_name: 0}
        self.used_numbers = set()
        self.started = False
        self.timer_task = None

        self._generate_ticket(host_name)

    def _generate_ticket(self, name):
        nums = random.sample(NUMBER_POOL, 15)
        self.player_numbers[name] = set(nums)
        self.player_rows[name] = [
            set(nums[0:5]),
            set(nums[5:10]),
            set(nums[10:15])
        ]

    async def broadcast(self, msg):
        for ws in list(self.players.keys()):
            await safe_send(ws, msg)


async def game_timer(room: Room):
    await asyncio.sleep(2)  # allow clients to open game screen
    start_time = time.time()

    try:
        while time.time() - start_time < GAME_DURATION:
            await asyncio.sleep(DRAW_INTERVAL)

            remaining = list(set(NUMBER_POOL) - room.used_numbers)
            if not remaining:
                break

            number = random.choice(remaining)
            room.used_numbers.add(number)

            for name, nums in room.player_numbers.items():
                if number in nums:
                    room.scores[name] += 2
                    for row in room.player_rows[name]:
                        if number in row:
                            row.remove(number)
                            if len(row) == 0:
                                room.scores[name] += 5

            await room.broadcast({
                "type": "NUMBER_DRAWN",
                "data": {
                    "number": number,
                    "scores": room.scores
                }
            })

            # 🔑 IMPORTANT: yield control explicitly
            await asyncio.sleep(0)

    finally:
        leaderboard = sorted(
            room.scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        await room.broadcast({
            "type": "GAME_OVER",
            "data": {
                "leaderboard": leaderboard
            }
        })


async def handle_message(ws, msg):
    msg_type = msg.get("type")
    data = msg.get("data", {})

    room = None
    for r in rooms.values():
        if ws in r.players:
            room = r
            break

    if msg_type == "CREATE_ROOM":
        room_id = ''.join(random.choices("ABCDEFGH123456789", k=6))
        room = Room(room_id, ws, data["player_name"])
        rooms[room_id] = room

        await safe_send(ws, {
            "type": "ROOM_CREATED",
            "data": {"room_id": room_id}
        })

    elif msg_type == "JOIN_ROOM":
        room_id = data["room_id"]
        name = data["player_name"]

        if room_id not in rooms:
            await safe_send(ws, {
                "type": "ERROR",
                "data": {"message": "ROOM_NOT_FOUND"}
            })
            return

        room = rooms[room_id]
        room.players[ws] = name
        room.scores[name] = 0
        room._generate_ticket(name)

    elif msg_type == "START_GAME":
        if not room or ws != room.host or room.started:
            return

        room.started = True
        room.timer_task = asyncio.create_task(game_timer(room))


async def handler(ws):
    try:
        async for message in ws:
            await handle_message(ws, json.loads(message))
    except:
        pass


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket Server running on port 8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
