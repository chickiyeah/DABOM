#-*- coding: utf-8 -*-
import json
from fastapi import APIRouter, Cookie, HTTPException, Depends, Request, WebSocket, UploadFile, File
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from broadcaster import Broadcast
from starlette.routing import Route, WebSocketRoute
from starlette.concurrency import run_until_first_complete
import redis
from controller.wordfilter import check_word
from controller.database import execute_sql
from controller.onemsgdb import execute_pri_sql
from firebase_admin import auth
import time
from pytz import timezone

from controller.credentials import verify_token

from firebase import Firebase

KST = timezone("ASIA/SEOUL")

print(KST)

firebaseConfig = {
    "apiKey": "AIzaSyC58Oh7Lyb7EoB0FWZQ-qMqfqLtiTJIIFw",
    "authDomain": "dabom-ca6fe.firebaseapp.com",
    "projectId": "dabom-ca6fe",
    "storageBucket": "dabom-ca6fe.appspot.com",
    "messagingSenderId": "607249280151",
    "appId": "1:607249280151:web:abcff56e0b43b1abb00dd2",
    "databaseURL":"https://dabom-ca6fe-default-rtdb.firebaseio.com/"
}

Storage = Firebase(firebaseConfig).storage()

r = redis.Redis(host="35.212.135.37", port=6379, decode_responses=True, db=0)

chat = APIRouter(prefix="/chat", tags=['webSocket_chat'])

er023 = {'code': 'ER023', 'message':'해당 아이디에 해당하는 그룹은 존재하지 않습니다.'}
er024 = {'code': 'ER024', 'message':'해당 그룹의 관리자가 아닙니다.'}
er035={"code":"ER035","message":"존재하지 않는 채팅방입니다."}
unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

#broadcast = Broadcast("redis://localhost:6379")
broadcast = Broadcast("redis://35.212.168.183:6379")
    
#print(broadcast)
CHANNEL = "CHAT"

async def echo_message(websocket: WebSocket):
    data = await websocket.receive_text()
    await websocket.send_text(f"Message text was: {data}")

async def send_time(websocket: WebSocket):
    now = str(datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"))
    await asyncio.sleep(10)
    await websocket.send_text(f"It is: {now}")

API_TOKEN = "e[M[jUQ@PT7AMr(H],6Z/}Jil@bbFF&XO.x/>J00uf!^Cx~Q5d"


class MessageEvent(BaseModel):
    u_id: str
    username: str
    message: str
    time: str
    pf_image: str

async def mutecheck():
    """while True:
        await asyncio.sleep(1)
        t = int(time.mktime(datetime.now().timetuple()))
        execute_sql(f"DELETE FROM `chat_mute` WHERE unmute_at < {t}")"""

async def logfile(author, msg, channel):
    f_data = msg.split('/*/')[1]
    f_type = f_data.split('/')[0]
    f_type_extension = f_data.split('/')[1]
    f_file_extension = f_data.split('/')[2]
    f_name = f_data.split('/')[3]
    f_link = f_data.split('/_/')[1].replace("\"","")
    now = str(datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"))
    print(now)
    res = execute_sql(f"INSERT INTO chat_file (file_type, file_type_ext, file_name_ext, file_link, author, channel, at, file_name) VALUES ('{f_type}','{f_type_extension}','{f_file_extension}','{f_link}','{author}','{channel}','{now}','{f_name}')")
    print(res)

async def receive_message(websocket: WebSocket, username: str, channel: str, u_id: str):
    async with broadcast.subscribe(channel) as subscriber:
        async for event in subscriber:
            message_event = MessageEvent.parse_raw(event.message)
            # Discard user's own messages
            if message_event.u_id != u_id:
                await websocket.send_json(message_event.dict())


async def send_message(websocket: WebSocket, username: str, channel: str, u_id: str):
    data = await websocket.receive_text()
    print(u_id)
    user = execute_sql("SELECT `Nickname`, `profile_image` FROM `user` WHERE `ID` = '"+u_id+"'")
    print(user)
    pf_image = user[0]['profile_image']
    curse = check_word(data, "ko")
    now = str(datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S"))
    msg = data
    if "file_message/*/" in msg and u_id == u_id:
        asyncio.create_task(logfile(u_id, msg, channel))

    if curse != None:
        r.xadd(channel,{'time':now, 'username':username, 'channel':channel, 'message' :curse, 'u_id':u_id, 'pf_image':pf_image})
        event = MessageEvent(u_id=u_id, username=username, message=curse, time=now, pf_image=pf_image)
        if "pri" in channel:
            execute_pri_sql(f"INSERT INTO `chat` (`id`, `group`, `filter_message`, `send_at`, `origin_message`, `nickname`) VALUES ('{u_id}','{channel}','{curse}', '{now}', '{data}', '{username}')")
        elif "@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr" in channel:
            print(data)
            if data.count("/*/") == 6:
                datas = data.split("/*/")
                print(datas)
                if datas[0] != "alert":
                    raise HTTPException(403)
                else:
                    type = datas[1]
                    tar_id = datas[2]
                    profile_image = datas[3]
                    url = datas[4]
                    title = datas[5]
                    tar_msg = datas[6]
                    execute_pri_sql(f"INSERT INTO `alert` (`id`, `msg`, `read`, `send_at`, `type`, `target_id`, `url`, `title`, `profile_image`)) VALUES ('{u_id}','{tar_msg}', 'False', '{now}', '{type}', '{tar_id}', '{url}', '{title}', '{profile_image}')")
            else:
                raise HTTPException(403)
        else:
            execute_sql(f"INSERT INTO `chat` (`id`, `group`, `filter_message`, `send_at`, `origin_message`, `nickname`) VALUES ('{u_id}','{channel}','{curse}', '{now}', '{data}', '{username}')")
        
        await broadcast.publish(channel, message=event.json())
    else:
        r.xadd(channel,{'time':now, 'username':username, 'channel':channel, 'message' :data, 'u_id':u_id, 'pf_image':pf_image})
        event = MessageEvent(u_id=u_id, username=username, message=data, time=now, pf_image=pf_image)
        if "pri" in channel:
            execute_pri_sql(f"INSERT INTO `chat` (`id`, `group`, `filter_message`, `send_at`, `origin_message`, `nickname`) VALUES ('{u_id}','{channel}','{curse}', '{now}', '{data}', '{username}')")
        elif "@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr" in channel:
            if data.count("/*/") == 6:
                datas = data.split("/*/")
                if datas[0] != "alert":
                    raise HTTPException(403)
                else:
                    type = datas[1]
                    tar_id = datas[2]
                    profile_image = datas[3]
                    url = datas[4]
                    title = datas[5]
                    tar_msg = datas[6]
                    execute_pri_sql(f"INSERT INTO `alert` (`id`, `msg`, `read`, `send_at`, `type`, `target_id`, `url`, `title`, `profile_image`) VALUES ('{u_id}','{tar_msg}', 'False', '{now}', '{type}', '{tar_id}', '{url}', '{title}', '{profile_image}')")
            else:
                raise HTTPException(403)
        else:
            execute_sql(f"INSERT INTO `chat` (`id`, `group`, `filter_message`, `send_at`, `origin_message`, `nickname`) VALUES ('{u_id}','{channel}','{curse}', '{now}', '{data}', '{username}')")
        
        await broadcast.publish(channel, message=event.json())

async def join_channel(username: str, channel: str):
    now = str(datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"))
    r.xadd(channel,{'time':now, 'username':"userupdate", 'channel':channel, 'message' :f"{username}님이 채팅방에 참여했습니다.", 'u_id':"system", 'pf_image':"../assets/images/default-profile.png"})
    event = MessageEvent(u_id="system", username="userupdate", message=f"{username}님이 채팅방에 참여했습니다.", time=now, pf_image="../assets/images/default-profile.png")
    await broadcast.publish(channel, message=event.json())

async def exit_channel(username: str, channel: str):
    now = str(datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"))
    r.xadd(channel,{'time':now, 'username':"userupdate", 'channel':channel, 'message' :f"{username}님이 채팅방에서 퇴장했습니다.", 'u_id':"system", 'pf_image':"../assets/images/default-profile.png"})
    event = MessageEvent(u_id="system", username="userupdate", message=f"{username}님이 채팅방에서 퇴장했습니다.", time=now, pf_image="../assets/images/default-profile.png")
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

@chat.post("/uploadfile")
async def upload(ext:str, name:str, image: UploadFile = File(), access_token: Optional[str] = Cookie(None)):
    now = datetime.now(KST).strftime("%Y-%m-%d_%H:%M:%S")  
    try:
        user = auth.verify_id_token(access_token, check_revoked=True)
        uid = user['user_id']
    except:
        uid = "register_"+now

    
    a = Storage.child(f"/dabom/{uid}/{now}_{name}.{ext}").put(image.file)
    print(now)
    print(f"https://firebasestorage.googleapis.com/v0/b/dabom-ca6fe.appspot.com/o/dabom%2F{uid}%2F{now}_{name}.{ext}?alt=media&token={a['downloadTokens']}")
    return f"https://firebasestorage.googleapis.com/v0/b/dabom-ca6fe.appspot.com/o/dabom%2F{uid}%2F{now}_{name}.{ext}?alt=media&token={a['downloadTokens']}"


@chat.get("/members")
async def members(group: str):
    guilds = execute_sql(f"SELECT room, members FROM chatroom WHERE room = '{group}'")
    print(guilds) 
    if guilds == None or len(guilds) == 0:
        raise HTTPException(400, er035)

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
        
        cursec = int(time.mktime(datetime.now().timetuple()))
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
    print(u_id)
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

    if "pri" in channel:
        comments = execute_pri_sql(f"SELECT * FROM chat WHERE `group` = '{channel}' ORDER BY send_at DESC LIMIT 100")
        if len(comments) != 0:
            for comment in comments:
                user = execute_sql("SELECT `Nickname`, `profile_image` FROM `user` WHERE `ID` = '"+u_id+"'")
                pf_image = user[0]['profile_image']
                if comment['filter_message'] == "None":
                    event = MessageEvent(u_id=comment['id'], username=comment['nickname'], message=comment['origin_message'], time=str(comment['send_at']), pf_image=pf_image)
                else:
                    event = MessageEvent(u_id=comment['id'], username=comment['nickname'], message=comment['filter_message'], time=str(comment['send_at']), pf_image=pf_image)
                
                await websocket.send_json(event.json())


    #comments = r.xread(streams={channel: 0})
    #if len(comments) != 0:
    #    c_data = comments[0][1]
    #    for id, value in c_data:
    #        await websocket.send_json(value)
            

    try:
        while True:
            receive_message_task = asyncio.create_task(
                receive_message(websocket, username, channel, u_id)
            )
            send_message_task = asyncio.create_task(send_message(websocket, username, channel, u_id))
            done, pending = await asyncio.wait(
                {receive_message_task, send_message_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect as close:

        guilds = execute_sql(f"SELECT room, members FROM chatroom WHERE room = '{channel}'")
        print(close.code)
        members = json.loads(guilds[0]['members'])
        members.remove(u_id)
        await exit_channel(username, channel)
        execute_sql(f"UPDATE chatroom SET members = '{json.dumps(members)}' WHERE room = '{channel}'")
        print("socket closed")



@chat.on_event("startup")
async def start_up():
    await broadcast.connect()
    execute_sql("TRUNCATE chatroom")
    #asyncio.create_task(mutecheck())

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

"""
    if "Va8%r@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr" in channel:
        alerts = execute_pri_sql(f"SELECT * FROM alert WHERE `id` = '{u_id}' AND `read` = 'False'")
        if len(alerts) > 0:
            for alert in alerts:
                user = execute_sql("SELECT `Nickname`, `profile_image` FROM `user` WHERE `ID` = '"+alert['id']+"'")
                msg = 'alert/'+alert['type']+'/'+alert['target_id']+'/'+alert['msg']
                event = MessageEvent(u_id=alert['id'], username=user[0]['Nickname'], message=msg, time=str(alert['send_at']), pf_image=user[0]['profile_image'])
                await websocket.send_json(event.json())
"""
