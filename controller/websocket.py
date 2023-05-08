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
r = redis.Redis(host="35.212.168.183", port=6379, decode_responses=True, db=0)

chat = APIRouter(prefix="", tags=['webSocket_chat'])


global current_user
current_user = {"guilds":{}}

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
    r.xadd(channel,{'time':datetime.datetime.utcnow().isoformat(), 'username':"system", 'channel':channel, 'message' :f"{username}님이 채팅방에 참여했습니다."})
    event = MessageEvent(username=username, message=f"{username}님이 채팅방에 참여했습니다.")
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

@chat.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,u_id:str, username: str = "Anonymous", channel: str = "lobby"):
    client = websocket.client.host
    print(client, u_id, username, channel)
    udata = {
        "ip" : client,
        "id": u_id,
        "nick": username,
    }
    guilds = execute_sql(f"SELECT room, members FROM chatroom WHERE room = '{channel}'")
    if len(guilds) == 0:
        member = [f'{u_id}']
        print(member)
        execute_sql(f"INSERT INTO chatroom (room, members) VALUES ('{channel}', '{json.dumps(member)}')")
    else:
        members = json.loads(guilds[0]['members'])
        members.append(u_id)
        execute_sql(f"UPDATE chatroom SET members = '{json.dumps(members)}' WHERE room = '{channel}'")

    if username == "Anonymous":
        await websocket.close()
    
    await join_channel(username, channel)

    await websocket.accept()

    await websocket.send_text(f"{username}님 안녕하세요! {channel} 채널에 참여했습니다!")
    await websocket.send_text("대화 내용을 불러오는 중입니다...")

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
        await websocket.close()


@chat.on_event("startup")
async def start_up():
    await broadcast.connect()

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

