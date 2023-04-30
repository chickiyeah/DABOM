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
import pyshorteners

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

restype_error = {"code":"ER025", "message":"Accept type is accept or reject"}
user_not_match_error = {"code":"ER026", "message":"User is not a member of this verifycode"}
request_user_not_match_error = {"code":"ER027", "message":"Request User is not Match with this verifycode"}
recive_user_not_match_error = {"code":"ER028", "message":"Target User is not Match with this verifycode"}
target_user_is_already_friend = {"code":"ER029", "message":"Target User is already Friend"}
target_user_is_not_friend = {"code":"ER030", "message":"Target User is not Friend"}

s = smtplib.SMTP("smtp.gmail.com", 587)
s.ehlo()
s.starttls()
s.login("noreply.dabom", "sxhmurnajtenjtbr")

bitly = pyshorteners.Shortener(api_key='6099ddc45ca69789ca421d865572f3d89c3c34ca')

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

@friendapi.get("/list/{page}")
async def friend_list(page: int, authorized: bool = Depends(verify_token)):
    if authorized:
        if page <= 0:
            raise HTTPException(400, "Page Must be greater than 0")
        
        uid = authorized[1]
        sql = "SELECT friends FROM user WHERE ID = '%s'" % uid
        res = json.loads(execute_sql(sql)[0]['friends'])
        if len(res) == 0:
            return "친구가 존재하지 않습니다."
        
        sql = "SELECT * FROM infomsg WHERE"
        for e in res:
            sql = sql + " ID = '%s' OR" % e

        sql = sql[0:-3] + " LIMIT 10 OFFSET %s0" % (page - 1)

        return execute_sql(sql)

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
            msg = MIMEMultipart('alternative')
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

            link = "http://130.162.141.91/friend/request/%s/%s/%s/%s/%s" % (requestid, requestnick, targetid, targetnick, verifykey)
            text = "\n\n\n안녕하세요 다봄 입니다.\n\n%s 님이 유저님에게 친구요청을 보냈습니다.\n아래 링크를 클릭해서 수락/거절 여부를 선택해주세요!\n\n\n%s\n\n\n※ 본 메일은 발신 전용 메일이며, 자세한 문의사항은 다봄 고객센터를 이용해 주시기 바랍니다."
            html = """\
<html>
  <head></head>
  <body>
    <div>
        <xlink href="//fonts.googleapis.com/css?family=Google+Sans" rel="stylesheet" type="text/css"
            <tr align="center" height="32" style="height: 32px;">
                <td>
                    <table border="0" cellspacing="0" cellpadding="0"
                    style="padding-bottom: 20px; max-width: 516px; min-width: 220px; margin-left:auto; margin-right:auto; margin-top:6rem">
                        <tbody>
                        <tr>
                        <td>
                            <div align="center" style="border-style: solid; border-width: thin; border-color:#dadce0; border-radius: 8px; padding: 40px 20px;">
                                <img src='https://firebasestorage.googleapis.com/v0/b/dabom-ca6fe.appspot.com/o/dabomlogo.png?alt=media&token=8b895151-37d3-4bbe-ae65-efdd6adb6ff7' width="74" height="54" style="margin-bottom: 16px;" loading="lazy"/>
                                <div style="font-family: 'Google Sans',Roboto,RobotoDraft,Helvetica,Arial,sans-serif;border-bottom: thin solid #dadce0; color: rgba(0,0,0,0.87); line-height: 32px; padding-bottom: 24px;text-align: center; word-break: break-word;><div style="font-size: 24px;">
                                    <a style="text-decoration: none; color: rgba(0,0,0,0.87);" rel="noreferrer noopener"target="_blank">{0}</a> 님이 유저님에게 친구요청을 보냈습니다.
                                </div>
                                    <div style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 14px; color: rgba(0,0,0,0.87); line-height: 20px;padding-top: 20px; text-align: center;">    
                                        <p>아래 링크를 클릭해서 수락/거절 여부를 선택해주세요!</p>
                                        <a href='{1}'> 친구 요청 보러가기 </a>
                                        <br/>
                                        <br/>
                                        <p>※ 본 메일은 발신 전용 메일이며,</p>
                                        <p>자세한 문의사항은 다봄 고객센터를 이용해 주시기 바랍니다.</p>
                                    </div>
                                </div>
                            </div>
                        </td></tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </div>
  </body>
</html>
""".format(requestnick, link)
            # Record the MIME types of both parts - text/plain and text/html.
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(part1)
            msg.attach(part2)
            #msg.set_content("<div><img src='https://firebasestorage.googleapis.com/v0/b/dabom-ca6fe.appspot.com/o/dabomlogo.png?alt=media&token=8b895151-37d3-4bbe-ae65-efdd6adb6ff7'>안녕하세요 다봄 입니다.\n\n%s 님이 유저님에게 친구요청을 보냈습니다.\n아래 링크를 클릭해서 수락/거절 여부를 선택해주세요!\n\n\n%s\n\n\n※ 본 메일은 발신 전용 메일이며, 자세한 문의사항은 다봄 고객센터를 이용해 주시기 바랍니다.</div>" % (requestnick, slink))
            msg.add_header('Content-Disposition', 'attachment', filename="dabomlogo")
            try:
                s.sendmail("noreply.dabom@gmail.com", targetmail, msg.as_string())
            except smtplib.SMTPServerDisconnected:
                d = smtplib.SMTP("smtp.gmail.com", 587)
                d.ehlo()
                d.starttls()
                d.login("noreply.dabom", "sxhmurnajtenjtbr")
                d.sendmail("noreply.dabom@gmail.com", targetmail, msg.as_string())
            except smtplib.SMTPSenderRefused: #sender refused to send message
                d = smtplib.SMTP("smtp.gmail.com", 587)
                d.ehlo()
                d.starttls()
                d.login("noreply.dabom", "sxhmurnajtenjtbr")
                d.sendmail("noreply.dabom@gmail.com", targetmail, msg.as_string())   
            
            return "friend request send"
        except auth.UserNotFoundError:
            raise HTTPException(400, User_NotFound)
        
@friendapi.post("/remove")
async def remove_friend(delid:str, authorized: bool = Depends(verify_token)):
    if authorized:
        try:
            auth.get_user(delid)
            f_list = execute_sql("SELECT friends FROM user WHERE ID = '%s'" % authorized[1])
            t_list = execute_sql("SELECT friends FROM user WHERE ID = '%s'" % delid)
            if delid in f_list:
                f_list.remove(delid)
                t_list.remove(authorized[1])
                execute_sql("UPDATE user SET friends = '%s' WHERE ID = '%s'" % (f_list, authorized[1]))
                execute_sql("UPDATE user SET friends = '%s' WHERE ID = '%s'" % (t_list, delid))
                return "Friend Removed"
            else:
                raise HTTPException(400, target_user_is_not_friend)
            
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