import json
import string
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, File, UploadFile, Cookie, Response, requests
from fastapi.responses import RedirectResponse
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
from controller.credentials import verify_token

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import utils

er028 = {"code":"ER028", "message":"처리 타입은 accept/reject 만 허용됩니다."}
er029 = {"code":"ER029", "message":"해당 유저와 이미 친구입니다."}
er030 = {"code":"ER030", "message":"해당 유저와 친구가 아닙니다."}

s = smtplib.SMTP("smtp.gmail.com", 587)
s.ehlo()
s.starttls()
s.login("noreply.dabom", "sxhmurnajtenjtbr")

bitly = pyshorteners.Shortener(api_key='6099ddc45ca69789ca421d865572f3d89c3c34ca')

friendapi = APIRouter(prefix="/api/friends", tags=["friend"])

firebaseConfig = {
    "apiKey": "AIzaSyC58Oh7Lyb7EoB0FWZQ-qMqfqLtiTJIIFw",
    "authDomain": "dabom-ca6fe.firebaseapp.com",
    "projectId": "dabom-ca6fe",
    "storageBucket": "dabom-ca6fe.appspot.com",
    "messagingSenderId": "607249280151",
    "appId": "1:607249280151:web:abcff56e0b43b1abb00dd2",
    "databaseURL":"https://dabom-ca6fe-default-rtdb.firebaseio.com/"
}

Auth = Firebase(firebaseConfig).auth()

User_NotFound = {"code":"ER011", "message":"USER_NOT_FOUND"}    

unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

class request_friend(BaseModel):
    id: str

@friendapi.get("/all")
async def get_friend(request: Request, authorzation: bool = Depends(verify_token)):
    if authorzation:
        f_res = []

        uid = authorzation[1]
        sql = "SELECT friends FROM user WHERE ID = '%s'" % (uid)
        res = json.loads(execute_sql(sql)[0]['friends'])
        if len(res) == 0:
            e_res = {
                'friends': [],
                'amount': 0
            }

            return e_res
        
        for uid in res:
            user = execute_sql("SELECT `Nickname`, `profile_image`, `ID` FROM `user` WHERE `ID` = %s", (uid))
            imsg = execute_sql("SELECT * FROM infomsg WHERE `ID` = %s", (uid))
            user[0]['imsg'] = imsg[0]['message']
            f_res.append(user[0])

        res = {
            'friends': f_res,
            'amount': len(res)
        }

        return res
        



@friendapi.get("/list")
async def friend_list(response: Response, page: int, access_token: Optional[str] = Cookie(None), refresh_token: Optional[str] = Cookie(None)):
    try:
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        user = auth.verify_id_token(access_token, check_revoked=True)
        print(user)
        if page <= 0:
            raise HTTPException(400, "Page Must be greater than 0")
        
        uid = user['user_id']
        page = page - 1
        sql = "SELECT friends FROM user WHERE ID = %s"
        res = json.loads(execute_sql(sql)[0]['friends'], (uid))
        if len(res) == 0:
            e_res = {
                'friends': [],
                'amount': 0,
                'page': page +1
            }

            return e_res
        
        sql = "SELECT * FROM infomsg WHERE"
        for e in res:
            sql = sql + " ID = '%s' OR" % e

        sql = sql[0:-3] + " LIMIT 7 OFFSET %s" % (page * 7)
        
        res = {
            'friends': execute_sql(sql, ()),
            'amount': len(res),
            'page': page +1
        }

        return res
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        raise HTTPException(status_code=401, detail=unauthorized_revoked)
    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        raise HTTPException(status_code=401, detail=unauthorized_userdisabled)
    except auth.InvalidIdTokenError:
        # Token is invalid
        if refresh_token == None:
            return RedirectResponse(url= "/login")

        try:
            currentuser = Auth.refresh(refresh_token)

            response.set_cookie(key="access_token", value=currentuser['idToken'], httponly=True)
            response.set_cookie(key="refresh_token", value=currentuser['refreshToken'], httponly=True)
            response.set_cookie(key="userId", value=currentuser['userId'], httponly=True)
            user = auth.verify_id_token(currentuser['idToken'], check_revoked=True)

            if page <= 0:
                raise HTTPException(400, "Page Must be greater than 0")
        
            uid = user['user_id']
            page = page - 1
            sql = "SELECT friends FROM user WHERE ID = '%s'"
            res = json.loads(execute_sql(sql)[0]['friends'], (uid))
            if len(res) == 0:
                e_res = {
                    'friends': [],
                    'amount': 0,
                    'page': page +1
                }

                return e_res
            
            sql = "SELECT * FROM infomsg WHERE"
            for e in res:
                sql = sql + " ID = '%s' OR" % e

            sql = sql[0:-3] + " LIMIT 7 OFFSET %s" % (page * 7)
            
            res = {
                'friends': execute_sql(sql, ()),
                'amount': len(res),
                'page': page +1
            }

            return res
        except requests.HTTPError as e:
            error = json.loads(e.args[1])['error']['message']
            if error == "TOKEN_EXPIRED":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            if error == "INVALID_REFRESH_TOKEN":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            print("Auto_Login_Error "+error)
        
    except auth.UserNotFoundError:
        raise HTTPException(status_code=401, detail=User_NotFound)
    except KeyError:
        raise HTTPException(status_code=400, detail=unauthorized)
    except ValueError:
        raise HTTPException(status_code=422)

@friendapi.post("/request")
async def friend_request(uid:str, userId: Optional[str] = Cookie(None)):
        t_id = uid
        er041 = {"code":"ER041","message":"본인에게 친구 요청을 할 수 없습니다."}

        if uid == userId:
            raise HTTPException(400, er041)
        
        try:
            target = auth.get_user_by_email(t_id)
            targetmail = target.email
            targetid = target.uid
            target = target.email_verified

            uid = userId
            sql = "SELECT friends FROM user WHERE ID = %s"
            res = json.loads(execute_sql(sql)[0]['friends'], (uid))

            if targetid in res:
                raise HTTPException(400, er029)
            
            if not target:
                raise HTTPException(400, User_NotFound)
            
            requestid = userId
            sql = "SELECT Nickname FROM user WHERE ID=%s"
            requestnick = execute_sql(sql, (requestid))[0]['Nickname']
            tarsql = "SELECT Nickname FROM user WHERE ID=%s"
            targetnick = execute_sql(tarsql, (targetid))[0]['Nickname']
            msg = MIMEMultipart('alternative')
            msg['Subject'] = '[다봄] %s 님으로 부터 친구요청이 도착했습니다.' % requestnick
            msg['From'] = utils.formataddr(("다봄","noreply.dabom@gmail.com"))
            msg['To'] = targetmail
            versql = "SELECT code FROM f_verify WHERE `type` = 'friend'"
            veri_list = execute_sql(versql, ())
            f_sql =  "SELECT req_id, tar_id FROM f_verify"
            f_list = execute_sql(f_sql, ())
            d = {"req_id": requestid, "tar_id": targetid}
            
            newno = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'log_invite'")[0]['no'])+1

            execute_sql("INSERT INTO log_invite (no, type, req, tar) VALUES (%s, %s, %s, %s)", (newno, "friend", requestid, targetid))

            execute_sql("UPDATE food_no SET no = %s WHERE `fetch` = 'log_invite'", (newno))

            if d in f_list:
                delteme = "DELETE FROM f_verify WHERE req_id = '%s' AND tar_id = '%s'"
                execute_sql(delteme, (requestid, targetid))

            keys = []
            for key in veri_list:
                keys.append(key['code'])

            verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])

            while verifykey in keys:
                verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])
            
            add_verifykey = "INSERT INTO f_verify (code, req_id, tar_id, `type`) VALUES ( %s, %s, %s, 'friend')"
            execute_sql(add_verifykey, (verifykey, requestid, targetid))

            link = "https://dabom.kro.kr/friend/request/%s/%s/%s/%s/%s" % (requestid, requestnick, targetid, targetnick, verifykey)
            text = "\n\n\n안녕하세요 다봄 입니다.\n\n%s 님이 유저님에게 친구요청을 보냈습니다.\n아래 링크를 클릭해서 수락/거절 여부를 선택해주세요!\n\n\n%s\n\n\n※ 본 메일은 발신 전용 메일이며, 자세한 문의사항은 다봄 <a href='https://dabom.channel.io/home'><strong>고객센터</strong></a>를 이용해 주시기 바랍니다."
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
                                        <p>자세한 문의사항은 다봄 <a href="https://dabom.channel.io/home"><strong>고객센터</strong></a>를 이용해 주시기 바랍니다.</p>
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
            
            return link
        except auth.UserNotFoundError:
            raise HTTPException(400, User_NotFound)
        
@friendapi.delete("/remove")
async def remove_friend(delid:str, authorized: bool = Depends(verify_token)):
    if authorized:
        try:
            auth.get_user(delid)
            f_list = json.loads(execute_sql("SELECT friends FROM user WHERE ID = %s", (authorized[1]))[0]['friends'])
            t_list = json.loads(execute_sql("SELECT friends FROM user WHERE ID = %s", (delid))[0]['friends'])
            #print(authorized[1])
            if delid in f_list:
                f_list.remove(delid)
                t_list.remove(authorized[1])
                execute_sql("UPDATE user SET friends = %s WHERE ID = %s", (json.dumps(f_list), authorized[1]))
                execute_sql("UPDATE user SET friends = %s WHERE ID = %s", (json.dumps(t_list), delid))
                return "Friend Removed"
            else:
                raise HTTPException(400, er030)
            
        except auth.UserNotFoundError:
            raise HTTPException(400, User_NotFound)

er037 = {"code":"ER037","message":"이미 차단된 유저입니다."}
er038 = {"code":"ER038","message":"차단되지 않은 유저입니다."}

@friendapi.get("/banlist")
async def ban_list_friend(page:int, userId: Optional[str] = Cookie(None)):
    if page > 0:
        page = page - 1
    else:
        page = 0

    try:
        b_list = json.loads(execute_sql("SELECT friend_ban FROM user WHERE `ID` = %s", (userId))[0]['friend_ban'])
    except IndexError:
        return []

    return b_list

@friendapi.post("/ban")
async def ban_friend(user_id: str, userId: Optional[str] = Cookie(None)):
        try:
            auth.get_user(user_id)
            b_list = json.loads(execute_sql("SELECT friend_ban FROM user WHERE `ID` = %s;", (userId))[0]['friend_ban'])
            if user_id in b_list:
                raise HTTPException(400, er037)

            f_list = json.loads(execute_sql("SELECT friends FROM user WHERE `ID` = %s;", (userId))[0]['friends'])
            t_list = json.loads(execute_sql("SELECT friends FROM user WHERE `ID` = %s;", (user_id))[0]['friends'])
            if user_id in f_list:
                f_list.remove(user_id)
                t_list.remove(userId)
                #print("UPDATE user SET friends = '%s' WHERE `ID` = '%s" % (f_list, userId))
                execute_sql("UPDATE user SET friends = %s WHERE `ID` = %s", (json.dumps(f_list), userId))
                execute_sql("UPDATE user SET friends = %s WHERE `ID` = %s", (json.dumps(t_list), user_id))

            b_list.append(user_id)
            execute_sql("UPDATE user SET friend_ban = %s WHERE `ID` = %s", (json.dumps(b_list), userId))
            return "유저를 차단했습니다."         

        except auth.UserNotFoundError:
            raise HTTPException(400, User_NotFound)

@friendapi.post("/pardon")
async def pardon_friend(user_id: str, userId: Optional[str] = Cookie(None)):
        try:
            auth.get_user(user_id)
            b_list = json.loads(execute_sql("SELECT friend_ban FROM user WHERE ID = %s", (userId))[0]['friend_ban'])
            if not user_id in b_list:
                raise HTTPException(400, er038)
            
            b_list.remove(user_id)
            execute_sql("UPDATE user SET friend_ban = %s WHERE ID = %s", (json.dumps(b_list), userId))
            return "유저를 차단해제했습니다."

        except auth.UserNotFoundError:
            raise HTTPException(400, User_NotFound)

@friendapi.post("/{f_type}/{req_id}/{req_nick}/{tar_id}/{tar_nick}/{verify_id}")
async def edit_friend(f_type: str, req_id: str, req_nick:str, tar_id: str, tar_nick:str, verify_id: str):
    print(f_type == "reject")
    if f_type != "accept" and f_type != "reject":
        raise HTTPException(403, er028)
    
    versql = "SELECT * FROM f_verify WHERE code = %s"
    veri = execute_sql(versql, verify_id)
    er026 = {'code':'ER026', 'message':'올바르지 않은 인증키입니다.'}
    er027 = {'code':'ER027', 'message':'인증키에 저장된 정보와 일치하지 않습니다.'}
    if len(veri) == 0:
        raise HTTPException(403, er026)
    
    try:
        auth.get_user(req_id)
        auth.get_user(tar_id)
    except auth.UserNotFoundError:
        raise HTTPException(403, User_NotFound)

    data = veri[0]
    if data['req_id'] != req_id:
        raise HTTPException(403, er027)
    
    if data['tar_id'] != tar_id:
        raise HTTPException(403, er027)

    if f_type == "accept":
        r_friend = json.loads(execute_sql("SELECT friends FROM user WHERE ID = %s", (req_id))[0]['friends'])      
        if (tar_id in r_friend):
            execute_sql("DELETE FROM f_verify WHERE code = %s", verify_id)
            raise HTTPException(400, er026)
        else:
            r_friend.append(tar_id)
            t_friend = json.loads(execute_sql("SELECT friends FROM user WHERE ID = %s", (tar_id))[0]['friends'])
            t_friend.append(req_id)

            execute_sql("UPDATE user SET friends = %s WHERE ID = %s", (json.dumps(r_friend), req_id))
            execute_sql("UPDATE user SET friends = %s WHERE ID = %s", (json.dumps(t_friend), tar_id))
            execute_sql("DELETE FROM f_verify WHERE code = %s", (verify_id))
            return "Friend Request Accepted"

    if f_type == "reject":
        execute_sql("DELETE FROM f_verify WHERE code = %s", (verify_id))
        return "Friend Request Rejected"