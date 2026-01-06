import asyncio, json, os, random, string, websockets

PORT = int(os.environ.get("PORT", 10000))
rooms = {}

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def generate_ticket():
    t = [[0]*9 for _ in range(3)]
    for r in range(3):
        for c in random.sample(range(9),5):
            start = c*10+1
            end = 90 if c==8 else start+9
            t[r][c] = random.randint(start,end)
    return t

async def broadcast(room, msg):
    for ws in room["sockets"]:
        await ws.send(json.dumps(msg))

async def handler(ws):
    room_id=None
    player=None

    async for msg in ws:
        data=json.loads(msg)
        t=data["type"]
        d=data.get("data",{})

        if t=="CREATE_ROOM":
            player=d["player_name"]
            room_id=generate_room_id()
            rooms[room_id]={
                "players":[player],
                "sockets":[ws],
                "tickets":{},
                "numbers":set(),
                "scores":{},
                "line_claimed":False,
                "ended":False
            }
            await ws.send(json.dumps({"type":"ROOM_CREATED","data":{"room_id":room_id}}))

        elif t=="JOIN_ROOM":
            room_id=d["room_id"]
            player=d["player_name"]
            rooms[room_id]["players"].append(player)
            rooms[room_id]["sockets"].append(ws)

        elif t=="START_GAME":
            room=rooms[room_id]
            for i,p in enumerate(room["players"]):
                room["tickets"][p]=generate_ticket()
                room["scores"][p]=0
                await room["sockets"][i].send(json.dumps({
                    "type":"TICKET_ASSIGNED","data":{"ticket":room["tickets"][p]}
                }))
            await broadcast(room,{"type":"GAME_STARTED","data":{}})

        elif t=="DRAW_NUMBER":
            room=rooms[room_id]
            if room["ended"]: continue
            n=random.randint(1,90)
            while n in room["numbers"]:
                n=random.randint(1,90)
            room["numbers"].add(n)
            await broadcast(room,{"type":"NUMBER_DRAWN","data":{"number":n}})

        elif t=="CLAIM_LINE":
            room=rooms[room_id]
            if room["line_claimed"]:
                await ws.send(json.dumps({"type":"CLAIM_RESULT","data":{"message":"Line already claimed"}}))
                continue

            ticket=room["tickets"][player]
            drawn=room["numbers"]

            valid=any(all(n==0 or n in drawn for n in row) for row in ticket)

            if valid:
                room["line_claimed"]=True
                room["scores"][player]+=1
                await broadcast(room,{"type":"SCORE_UPDATE","data":{"scores":room["scores"]}})
                await ws.send(json.dumps({"type":"CLAIM_RESULT","data":{"message":"Line claimed!"}}))
            else:
                await ws.send(json.dumps({"type":"CLAIM_RESULT","data":{"message":"Invalid line"}}))

        elif t=="CLAIM_TAMBOLA":
            room=rooms[room_id]
            if room["ended"]:
                await ws.send(json.dumps({"type":"CLAIM_RESULT","data":{"message":"Game ended"}}))
                continue

            nums=[n for r in room["tickets"][player] for n in r if n!=0]
            if all(n in room["numbers"] for n in nums):
                room["ended"]=True
                room["scores"][player]+=5

                leaderboard=sorted(room["scores"].items(), key=lambda x:x[1], reverse=True)
                await broadcast(room,{
                    "type":"GAME_ENDED",
                    "data":{"leaderboard":[{"name":p,"score":s} for p,s in leaderboard]}
                })
            else:
                await ws.send(json.dumps({"type":"CLAIM_RESULT","data":{"message":"Invalid Tambola"}}))

async def main():
    async with websockets.serve(handler,"0.0.0.0",PORT):
        await asyncio.Future()

asyncio.run(main())