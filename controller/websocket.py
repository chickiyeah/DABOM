#-*- coding: utf-8 -*-
import json
from fastapi import APIRouter, Cookie, HTTPException, Depends, Request, WebSocket, status
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect
import asyncio
import datetime
from typing import Optional
from broadcaster import Broadcast
from starlette.routing import Route, WebSocketRoute
from starlette.concurrency import run_until_first_complete
import redis
from controller.wordfilter import check_word
from controller.database import execute_sql
from firebase_admin import auth
import time

r = redis.Redis(host="35.212.168.183", port=6379, decode_responses=True, db=0)

chat = APIRouter(prefix="/chat", tags=['webSocket_chat'])

er023 = {'code': 'ER023', 'message':'해당 아이디에 해당하는 그룹은 존재하지 않습니다.'}
er024 = {'code': 'ER024', 'message':'해당 그룹의 관리자가 아닙니다.'}
er035={"code":"ER035","message":"존재하지 않는 채팅방입니다."}
unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}
async def verify_token(req: Request): 
    try:
        token = req.headers["Authorization"]  
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        user = auth.verify_id_token(token, check_revoked=True)
        # Token is valid and not revoked.
        return True, user['uid']
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        raise HTTPException(status_code=401, detail=unauthorized_revoked)
    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        raise HTTPException(status_code=401, detail=unauthorized_userdisabled)
    except auth.InvalidIdTokenError:
        # Token is invalid
        raise HTTPException(status_code=401, detail=unauthorized_invaild)
    except KeyError:
        raise HTTPException(status_code=400, detail=unauthorized)

#broadcast = Broadcast("redis://localhost:6379")
broadcast = Broadcast("redis://35.212.168.183:6379")
    
#print(broadcast)
CHANNEL = "CHAT"

async def echo_message(websocket: WebSocket):
    data = await websocket.receive_text()
    await websocket.send_text(f"Message text was: {data}")

async def send_time(websocket: WebSocket):
    await asyncio.sleep(10)
    await websocket.send_text(f"It is: {datetime.datetime.utcnow().isoformat()}")

API_TOKEN = "e[M[jUQ@PT7AMr(H],6Z/}Jil@bbFF&XO.x/>J00uf!^Cx~Q5d"


class MessageEvent(BaseModel):
    username: str
    message: str

async def mutecheck():
    while True:
        await asyncio.sleep(1)
        t = int(time.mktime(datetime.datetime.now().timetuple()))
        execute_sql(f"DELETE FROM `chat_mute` WHERE unmute_at < {t}")

async def receive_message(websocket: WebSocket, username: str, channel: str):
    async with broadcast.subscribe(channel) as subscriber:
        async for event in subscriber:
            message_event = MessageEvent.parse_raw(event.message)
            # Discard user's own messages
            if message_event.username != username:
                message_event.dict()
                msg = {
                    'username': username,
                    'message' : message_event.dict()['message']
                }
                await websocket.send_json(message_event.dict())


async def send_message(websocket: WebSocket, username: str, channel: str):
    data = await websocket.receive_text()
    curse = check_word(data, "ko")
    if curse != None:
        r.xadd(channel,{'time':datetime.datetime.utcnow().isoformat(), 'username':username, 'channel':channel, 'message' :curse})
        event = MessageEvent(username=username, message=curse)
        await broadcast.publish(channel, message=event.json())
    else:
        r.xadd(channel,{'time':datetime.datetime.utcnow().isoformat(), 'username':username, 'channel':channel, 'message' :data})
        event = MessageEvent(username=username, message=data)
        await broadcast.publish(channel, message=event.json())

async def join_channel(username: str, channel: str):
    r.xadd(channel,{'time':datetime.datetime.utcnow().isoformat(), 'username':"userupdate", 'channel':channel, 'message' :f"{username}님이 채팅방에 참여했습니다."})
    event = MessageEvent(username="userupdate", message=f"{username}님이 채팅방에 참여했습니다.")
    await broadcast.publish(channel, message=event.json())

@chat.delete("/delete_all")
async def delete_all(username: str, channel: str):
    if username != "ruddls030":
        raise HTTPException(400, "You are not allowed to delete")

    data = r.xread(streams={channel: 0})
    for streams in data:
        stream_name, messages = streams
        [ r.xdel( stream_name, i[0] ) for i in messages ]

    return "all message delete"

@chat.get("/members")
async def members(group: str):
    guilds = execute_sql(f"SELECT room, members FROM chatroom WHERE room = '{group}'")
    if guilds == None or len(guilds) == 0:
        raise HTTPException(400, er035)

    print(guilds)
    res = {}
    res['name'] = group
    res['members'] = guilds[0]['members']

    return res
er036 = {"code":"ER036","message":"뮤트 시간 타입이 올바르지 않습니다. (m, h ,d)"}
@chat.post("/mute")
async def mute(group: str, num: int, time_type: str, user_id: str, reason: Optional[str] = None, authorized: bool = Depends(verify_token)):
    if authorized:
        if not time_type in ['m','h','d']:
            raise HTTPException(400, er036)
        
        groups = execute_sql("SELECT `id`, `owner`, `operator`, `name` FROM `group` WHERE `id` = {0}".format(group))
        if len(groups) == 0:
            raise HTTPException(404, er023)
        
        n_group = groups[0]
        operators = json.loads(groups[0]['operator'])
        if authorized[1] != n_group['owner'] and not authorized[1] in operators and not authorized[1] == "admin":
            raise HTTPException(403, er024)
        
        cursec = int(time.mktime(datetime.datetime.now().timetuple()))
        if time_type == 's':
            plustime = num
            unmutesec = cursec + plustime      
        elif time_type == 'm':
            plustime = (num * 60)
            unmutesec = cursec + plustime
        elif time_type == 'h':
            plustime = ((num * 60) * 60)
            unmutesec = cursec + plustime
        elif time_type == 'd':
            plustime = (((num * 60) * 60) * 12)
            unmutesec = cursec + plustime

        a = execute_sql("SELECT id FROM chat_mute WHERE id = %s" % user_id)
        if len(a) == 0:
            execute_sql(f"INSERT INTO chat_mute VALUES('{user_id}', '{authorized[1]}', '{reason}',{unmutesec}, {group})")
        else:
            execute_sql(f"UPDATE chat_mute SET unmute_at = {unmutesec} WHERE id = '{user_id}' AND `group` = {group}")

@chat.post("/unmute")
async def unmute(group: str, user_id: str, authorized: bool = Depends(verify_token)):
    if authorized:
        groups = execute_sql("SELECT `id`, `owner`, `operator`, `name` FROM `group` WHERE `id` = {0}".format(group))
        if len(groups) == 0:
            raise HTTPException(404, er023)
        
        n_group = groups[0]
        operators = json.loads(groups[0]['operator'])
        if authorized[1] != n_group['owner'] and not authorized[1] in operators and not authorized[1] == "admin":
            raise HTTPException(403, er024)
        
        execute_sql(f"DELETE FROM `chat_mute` WHERE id = '{user_id}' AND `group` = {group}")
        return f"{user_id} unmuted"

er037 = {"code": "ER037", "message": "이미 차단된 유저입니다."}

@chat.post("/ban")
async def ban(group: str, user_id: str, reason: Optional[str] = None, authorized: bool = Depends(verify_token)):
    if authorized:
        groups = execute_sql("SELECT `id`, `owner`, `operator`, `name` FROM `group` WHERE `id` = {0}".format(group))
        if len(groups) == 0:
            raise HTTPException(404, er023)
        
        n_group = groups[0]
        operators = json.loads(groups[0]['operator'])
        if authorized[1] != n_group['owner'] and not authorized[1] in operators and not authorized[1] == "admin":
            raise HTTPException(403, er024)

        rl = execute_sql(f"SELECT `id` FROM chat_ban WHERE `id` = {user_id} AND `group_id` = {group}")

        if not len(rl) == 0:
            raise HTTPException(400, er037)
        
        execute_sql(f"INSERT INTO chat_ban VALUES ('{user_id}', '{authorized[1]}','{reason}',{group})")

er038 = {"code":"ER038","message":"차단되지 않은 유저입니다."}
@chat.post('/pardon')
async def pardon(group: str, user_id: str, authorized: bool = Depends(verify_token)):
    if authorized:
        groups = execute_sql("SELECT `id`, `owner`, `operator`, `name` FROM `group` WHERE `id` = {0}".format(group))
        if len(groups) == 0:
            raise HTTPException(404, er023)
        
        n_group = groups[0]
        operators = json.loads(groups[0]['operator'])
        if authorized[1] != n_group['owner'] and not authorized[1] in operators and not authorized[1] == "admin":
            raise HTTPException(403, er024)

        rl = execute_sql(f"SELECT `id` FROM chat_ban WHERE `id` = {user_id} AND `group_id` = {group}")

        if len(rl) == 0:
            raise HTTPException(400, er038)
        
        execute_sql(f"DELETE FROM chat_ban WHERE `id` = {user_id} AND `group_id` = {group}")

@chat.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,u_id:str, username: str = "Anonymous", channel: str = "lobby"):
    guilds = execute_sql(f"SELECT room, members FROM chatroom WHERE room = '{channel}'")
    user_d = {
        'name': username,
        'id': u_id
    }
    if guilds == None or len(guilds) == 0:
        member = [f'{u_id}']
        execute_sql(f"INSERT INTO chatroom (room, members) VALUES ('{channel}', '{json.dumps(member)}')")
    else:
        members = json.loads(guilds[0]['members'])
        members.append(u_id)
        execute_sql(f"UPDATE chatroom SET members = '{json.dumps(members)}' WHERE room = '{channel}'")

    if username == "Anonymous":
        await websocket.close()
    
    await join_channel(username, channel)

    await websocket.accept()
    data = {
        'username' : "system",
        'message' : f"{username}님 안녕하세요! {channel} 채널에 참여했습니다!"
    }
    await websocket.send_json(data)
    data['message'] = "대화 내용을 불러오는 중입니다..."
    await websocket.send_json(data)

    comments = r.xread(streams={channel: 0})
    if len(comments) != 0:
        c_data = comments[0][1]
        for id, value in c_data:
            data = {
                'username' : value['username'],
                'message' : value['message']
            }
            await websocket.send_json(data)
            

    try:
        while True:
            receive_message_task = asyncio.create_task(
                receive_message(websocket, username, channel)
            )
            send_message_task = asyncio.create_task(send_message(websocket, username, channel))
            done, pending = await asyncio.wait(
                {receive_message_task, send_message_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        guilds = execute_sql(f"SELECT room, members FROM chatroom WHERE room = '{channel}'")
        members = json.loads(guilds[0]['members'])
        members.remove(u_id)
        execute_sql(f"UPDATE chatroom SET members = '{json.dumps(members)}' WHERE room = '{channel}'")
        print("socket closed")



@chat.on_event("startup")
async def start_up():
    await broadcast.connect()
    execute_sql("TRUNCATE chatroom")
    asyncio.create_task(mutecheck())

@chat.on_event("shutdown")
async def shutdown():
    await broadcast.disconnect()

    """
    try:
        while True:
            receive_message_task = asyncio.create_task(
                receive_message(websocket, username)
            )
            send_message_task = asyncio.create_task(send_message(websocket, username))
            done, pending = await asyncio.wait(
                {receive_message_task, send_message_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect as e:
        print(e)
        await websocket.close()
    """

"""
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@chat.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, username: str = "Anonymous",w_token: str = None):
    print(w_token)
    print(API_TOKEN)
    print(username)
    if w_token != API_TOKEN:
        print("here")
        print(w_token)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    await websocket.send_text(f"Hello, {username}!")
    try:
        while True:
            echo_message_task = asyncio.create_task(echo_message(websocket))
            send_time_task = asyncio.create_task(send_time(websocket))
            done, pending = await asyncio.wait(
                {echo_message_task, send_time_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        await websocket.close()

@chat.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
"""

