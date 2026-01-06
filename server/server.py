import asyncio, json, os, random, string, websockets

PORT = int(os.environ.get("PORT", 10000))
rooms = {}

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def generate_ticket():
    t = [[0]*9 for _ in range(3)]
    for r in range(3):
        for c in random.sample(range(9), 5):
            start = c*10+1
            end = 90 if c==8 else start+9
            t[r][c] = random.randint(start, end)
    return t

async def broadcast(room, msg):
    for ws in room["sockets"]:
        await ws.send(json.dumps(msg))

async def handler(ws):
    room_id = None
    player = None

    async for msg in ws:
        data = json.loads(msg)
        t = data["type"]
        d = data.get("data", {})

        if t == "CREATE_ROOM":
            player = d["player_name"]
            room_id = generate_room_id()
            rooms[room_id] = {
                "players":[player],
                "sockets":[ws],
                "tickets":{},
                "numbers":set(),
                "scores":{}
            }
            await ws.send(json.dumps({"type":"ROOM_CREATED","data":{"room_id":room_id}}))

        elif t == "JOIN_ROOM":
            room_id = d["room_id"]
            player = d["player_name"]
            rooms[room_id]["players"].append(player)
            rooms[room_id]["sockets"].append(ws)

        elif t == "START_GAME":
            room = rooms[room_id]
            for i,p in enumerate(room["players"]):
                ticket = generate_ticket()
                room["tickets"][p] = ticket
                room["scores"][p] = 0
                await room["sockets"][i].send(json.dumps({
                    "type":"TICKET_ASSIGNED","data":{"ticket":ticket}
                }))
            await broadcast(room, {"type":"GAME_STARTED","data":{}})

        elif t == "DRAW_NUMBER":
            room = rooms[room_id]
            num = random.randint(1,90)
            while num in room["numbers"]:
                num = random.randint(1,90)
            room["numbers"].add(num)
            await broadcast(room, {"type":"NUMBER_DRAWN","data":{"number":num}})

        elif t in ("CLAIM_LINE","CLAIM_TAMBOLA"):
            room = rooms[room_id]
            ticket = room["tickets"][player]
            drawn = room["numbers"]

            valid = True
            nums = []

            for row in ticket:
                for n in row:
                    if n!=0:
                        nums.append(n)

            if t == "CLAIM_LINE":
                valid = any(
                    all(n==0 or n in drawn for n in row)
                    for row in ticket
                )
                score = 1
            else:
                valid = all(n in drawn for n in nums)
                score = 5

            if valid:
                room["scores"][player] += score
                await broadcast(room, {
                    "type":"SCORE_UPDATE",
                    "data":{"scores":room["scores"]}
                })
                await ws.send(json.dumps({
                    "type":"CLAIM_RESULT",
                    "data":{"message":"Claim accepted!"}
                }))
            else:
                await ws.send(json.dumps({
                    "type":"CLAIM_RESULT",
                    "data":{"message":"Invalid claim"}
                }))

async def main():
    async with websockets.serve(handler,"0.0.0.0",PORT):
        await asyncio.Future()

asyncio.run(main())