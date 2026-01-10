import asyncio, json, os, random, string, websockets

PORT = int(os.environ.get("PORT", 10000))
rooms = {}

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# ---------- REAL TAMBOLA TICKET ----------
def generate_ticket():
    ticket = [[0]*9 for _ in range(3)]

    for r in range(3):
        cols = random.sample(range(9), 5)
        for c in cols:
            ticket[r][c] = -1

    used = set()
    for c in range(9):
        rows = [r for r in range(3) if ticket[r][c] == -1]
        if not rows:
            continue

        start = c * 10 + 1
        end = 90 if c == 8 else start + 9
        nums = random.sample([n for n in range(start, end+1) if n not in used], len(rows))
        nums.sort()

        for r, n in zip(rows, nums):
            ticket[r][c] = n
            used.add(n)

    return ticket

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
                "players": [player],
                "sockets": [ws],
                "tickets": {},
                "numbers": set(),
                "scores": {},
                "claimed": set(),
                "ended": False
            }
            await ws.send(json.dumps({"type":"ROOM_CREATED","data":{"room_id":room_id}}))
            await broadcast(rooms[room_id],{"type":"PLAYERS_UPDATE","data":{"players":rooms[room_id]["players"]}})

        elif t == "JOIN_ROOM":
            room_id = d["room_id"]
            player = d["player_name"]
            room = rooms[room_id]
            room["players"].append(player)
            room["sockets"].append(ws)
            await broadcast(room,{"type":"PLAYERS_UPDATE","data":{"players":room["players"]}})

        elif t == "START_GAME":
            room = rooms[room_id]
            for i,p in enumerate(room["players"]):
                room["tickets"][p] = generate_ticket()
                room["scores"][p] = 0
                await room["sockets"][i].send(json.dumps({
                    "type":"TICKET_ASSIGNED","data":{"ticket":room["tickets"][p]}
                }))
            await broadcast(room,{"type":"GAME_STARTED","data":{}})

        elif t == "DRAW_NUMBER":
            room = rooms[room_id]
            if room["ended"]:
                continue
            n = random.randint(1,90)
            while n in room["numbers"]:
                n = random.randint(1,90)
            room["numbers"].add(n)
            await broadcast(room,{"type":"NUMBER_DRAWN","data":{"number":n}})

        elif t == "MAKE_CLAIM":
            room = rooms[room_id]
            claim = d["claim"]

            if claim in room["claimed"]:
                await ws.send(json.dumps({
                    "type":"CLAIM_RESULT",
                    "data":{"status":"ALREADY","claim":claim}
                }))
                continue

            ticket = room["tickets"][player]
            drawn = room["numbers"]

            rows = [
                [n for n in ticket[0] if n != 0],
                [n for n in ticket[1] if n != 0],
                [n for n in ticket[2] if n != 0]
            ]

            all_nums = [n for r in ticket for n in r if n != 0]

            valid = False

            if claim == "QUICK_5":
                valid = len(drawn) >= 5

            elif claim == "FOUR_CORNERS":
                corners = [ticket[0][0],ticket[0][8],ticket[2][0],ticket[2][8]]
                corners = [n for n in corners if n != 0]
                valid = all(n in drawn for n in corners)

            elif claim == "FIRST_LINE":
                valid = all(n in drawn for n in rows[0])

            elif claim == "SECOND_LINE":
                valid = all(n in drawn for n in rows[1])

            elif claim == "THIRD_LINE":
                valid = all(n in drawn for n in rows[2])

            elif claim == "TAMBOLA":
                valid = all(n in drawn for n in all_nums)

            if not valid:
                await ws.send(json.dumps({
                    "type":"CLAIM_RESULT",
                    "data":{"status":"INVALID","claim":claim}
                }))
                continue

            room["claimed"].add(claim)
            room["scores"][player] += 1

            await broadcast(room,{
                "type":"SCORE_UPDATE",
                "data":{"scores":room["scores"]}
            })

            await broadcast(room,{
                "type":"CLAIM_RESULT",
                "data":{"status":"SUCCESS","claim":claim,"player":player}
            })

            if claim == "TAMBOLA":
                room["ended"] = True
                leaderboard = sorted(room["scores"].items(), key=lambda x:x[1], reverse=True)
                await broadcast(room,{
                    "type":"GAME_ENDED",
                    "data":{"leaderboard":[{"name":p,"score":s} for p,s in leaderboard]}
                })

async def main():
    async with websockets.serve(handler,"0.0.0.0",PORT):
        await asyncio.Future()

asyncio.run(main())
