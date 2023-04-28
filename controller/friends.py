import json
import string
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, File, UploadFile
from pydantic import BaseModel
from controller.database import execute_sql
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import _auth_utils
from firebase import Firebase
import datetime
import smtplib
from email.message import EmailMessage
import random

restype_error = {"code":"ER025", "message":"Accept type is accept or reject"}
user_not_match_error = {"code":"ER026", "message":"User is not a member of this verifycode"}
request_user_not_match_error = {"code":"ER027", "message":"Request User is not Match with this verifycode"}
recive_user_not_match_error = {"code":"ER028", "message":"Target User is not Match with this verifycode"}
target_user_is_already_friend = {"code":"ER029", "message":"Target User is already Friend"}

s = smtplib.SMTP("smtp.gmail.com", 587)
s.ehlo()
s.starttls()
s.login("noreply.dabom", "sxhmurnajtenjtbr")

friendapi = APIRouter(prefix="/api/friends", tags=["friend"])

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

User_NotFound = {"code":"ER011", "message":"USER_NOT_FOUND"}    

unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

class request_friend(BaseModel):
    email: str

@friendapi.get("/list")
async def friend_list(authorized: bool = Depends(verify_token)):
    if authorized:
        uid = authorized[1]
        sql = "SELECT friends FROM user WHERE ID = '%s'" % uid
        res = json.loads(execute_sql(sql)[0]['friends'])
        if len(res) == 0:
            return "친구가 존재하지 않습니다."
        
        return res

@friendapi.post("/request")
async def friend_request(data:request_friend, authorized: bool = Depends(verify_token)):
    if authorized:
        targetmail = data.email
        
        try:
            target = auth.get_user_by_email(targetmail)
            targetid = target.uid
            target = target.email_verified

            uid = authorized[1]
            sql = "SELECT friends FROM user WHERE ID = '%s'" % uid
            res = json.loads(execute_sql(sql)[0]['friends'])

            if targetid in res:
                raise HTTPException(400, target_user_is_already_friend)
            
            if not target:
                raise HTTPException(400, User_NotFound)
            
            requestid = authorized[1]
            sql = "SELECT Nickname FROM user WHERE ID='%s'" % requestid
            requestnick = execute_sql(sql)[0]['Nickname']
            tarsql = "SELECT Nickname FROM user WHERE ID='%s'" % targetid
            targetnick = execute_sql(tarsql)[0]['Nickname']
            msg = EmailMessage()
            msg['Subject'] = '[다봄] %s 님으로 부터 친구요청이 도착했습니다.' % requestnick
            msg['From'] = "noreply.dabom@gmail.com"
            msg['To'] = targetmail
            versql = "SELECT code FROM f_verify"
            veri_list = execute_sql(versql)
            f_sql =  "SELECT req_id, tar_id FROM f_verify"
            f_list = execute_sql(f_sql)
            d = {"req_id": requestid, "tar_id": targetid}

            if d in f_list:
                delteme = "DELETE FROM f_verify WHERE req_id = '%s' AND tar_id = '%s'" % (requestid, targetid)
                execute_sql(delteme)

            keys = []
            for key in veri_list:
                keys.append(key['code'])

            verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])

            while verifykey in keys:
                verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])
            
            add_verifykey = "INSERT INTO f_verify (code, req_id, tar_id) VALUES ('%s','%s','%s')" % (verifykey, requestid, targetid)
            execute_sql(add_verifykey)

            link = "http://localhost:8000/friend/request/%s/%s/%s/%s/%s" % (requestid, requestnick, targetid, targetnick, verifykey)
            msg.set_content("안녕하세요 다봄 입니다.\n\n%s 님이 유저님에게 친구요청을 보냈습니다.\n아래 링크를 클릭해서 수락/거절 여부를 선택해주세요!\n\n\n%s\n\n\n※ 본 메일은 발신 전용 메일이며, 자세한 문의사항은 다봄 고객센터를 이용해 주시기 바랍니다." % (requestnick, link))
            
            try:
                s.send_message(msg)
            except smtplib.SMTPServerDisconnected:
                d = smtplib.SMTP("smtp.gmail.com", 587)
                d.ehlo()
                d.starttls()
                d.login("noreply.dabom", "sxhmurnajtenjtbr")
                d.send_message(msg)
            except smtplib.SMTPSenderRefused: #sender refused to send message
                d = smtplib.SMTP("smtp.gmail.com", 587)
                d.ehlo()
                d.starttls()
                d.login("noreply.dabom", "sxhmurnajtenjtbr")
                d.send_message(msg)   
            
            return "friend request send"
        except auth.UserNotFoundError:
            raise HTTPException(400, User_NotFound)
        
@friendapi.post("/{f_type}/{req_id}/{req_nick}/{tar_id}/{tar_nick}/{verify_id}")
async def edit_friend(f_type: str, req_id: str, req_nick:str, tar_id: str, tar_nick:str, verify_id: str):
    if not f_type == "accept" or f_type == "reject":
        raise HTTPException(403, restype_error)
    
    versql = "SELECT * FROM f_verify WHERE code = '%s'" % verify_id
    veri = execute_sql(versql)
    if len(veri) == 0:
        raise HTTPException(403, "Invalid verify")
    
    try:
        auth.get_user(req_id)
        auth.get_user(tar_id)
    except auth.UserNotFoundError:
        raise HTTPException(403, User_NotFound)

    data = veri[0]
    if data['req_id'] != req_id:
        raise HTTPException(403, request_user_not_match_error)
    
    if data['tar_id'] != tar_id:
        raise HTTPException(403, recive_user_not_match_error)

    if f_type == "accept":
        r_friend = json.loads(execute_sql("SELECT friends FROM user WHERE ID = '%s'" % (req_id))[0]['friends'])
        r_friend.append(tar_id)
        t_friend = json.loads(execute_sql("SELECT friends FROM user WHERE ID = '%s'" % (tar_id))[0]['friends'])
        t_friend.append(req_id)

        execute_sql("UPDATE user SET friends = '%s' WHERE ID = '%s'" % (json.dumps(r_friend), req_id))
        execute_sql("UPDATE user SET friends = '%s' WHERE ID = '%s'" % (json.dumps(t_friend), tar_id))
        execute_sql("DELETE FROM f_verify WHERE code = '%s'" % verify_id)
        return "Friend Request Accepted"

    if f_type == "reject":
        execute_sql("DELETE FROM f_verify WHERE code = '%s'" % verify_id)
        return "Friend Request Rejected"