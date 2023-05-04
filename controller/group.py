import json
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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

s = smtplib.SMTP("smtp.gmail.com", 587)
s.ehlo()
s.starttls()
s.login("noreply.dabom", "sxhmurnajtenjtbr")


groupapi = APIRouter(prefix="/api/group", tags=["group"])

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
    
class create_group(BaseModel):
    name:str
    description:str
    type:str
    image:Optional[str]

class invite_group(BaseModel):
    group_id: int
    target_id: str

@groupapi.get('/list')
async def list_group():
    groups = execute_sql("SELECT ")

@groupapi.post('/create')
async def create_group(data: create_group, authorized: bool = Depends(verify_token)):
    er022 = {'code': 'ER022', 'message': '시스템에 의해 당신의 그룹생성 권한은 박탈되었습니다. (접근 차단된 그룹의 소유자입니다.)'}
    er025 = {'code': 'ER025', 'message': '그룹타입은 Public, Private 만 허용됩니다.'}
    if authorized:
        ban = execute_sql("SELECT group_create_ban FROM user WHERE `ID` = %s" % authorized[1])[0]['group_create_ban']
        if ban:
            raise HTTPException(403, er022)
        
        if data.type != 'Public' and data.type != 'Private':
            raise HTTPException(400, er025)
        
        baseimage = "iVBORw0KGgoAAAANSUhEUgAAAgcAAADmCAYAAABBJiY1AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAlKSURBVHhe7d0vV5dJH8Dhe5+OL0A0kcAiCRrJZpJGo5EwSSItJk2QaJBoWLSRjFggYaLJCxBfwD47nuHsfs9RuWcQlt/MdZ3j2Xuam34f5+8ff/1tAADI/pf/CwDwnTgAAAJxAAAE4gAACMQBABCIAwAgEAcAQCAOAIBAHAAAgTgAAAJxAAAE4gAACMQBABCIAwAgEAcAQCAOAIBAHAAAgTgAAAJxAAAE4gAACMQBABCIAwAgEAcAQCAOAIBAHAAAgTgAAAJxAAAE4gAACMQBABCIAwAgEAcAQCAOAIBAHAAAgTgAAAJxAAAE4gAACMQBABCIAwAgEAcAQCAOAIBAHAAAgTgAAAJxAAAE4gAACMQBABCIAwAgEAcAQCAOAIBAHAAAgTgAAAJxAAAE4gAACMQBABCIAwAgEAcAQCAOAIBAHAAAgTgAAAJxAAAE4gAACMQBABCIAwAgEAcAQCAOAIBAHAAAgTgAAAJxAAAE4gAACMQBABCIAwAg+OOvv+Vv4BfOzs6Gy8vLPOLJkyfD1NRUHgEtEQcw0srKynB8fJxHnJ6eigNolGUFoNiDBw+EATRMHADFZmdn8xfQInEAFEszB0C7xAFQzMwBtE0cAMUePXqUv4AWiQOgmDiAtokDoNj09HT+AlokDoBiZg6gbeIAKGIzIrRPHABFHGOE9okDoMjc3Fz+AlrlbQUYaW9v7/vjSy35/Pnz9z8l1tfXh5cvX+YR0CJxAB179erV8O7duzwaZ3d3d3j27FkeAS2yrAAdu7i4yF/j2XMA7TNzAB1bWloavnz5kkfjjH2qOS3BHB0d5dH10vHI5eXlPLp9aZno8vIyj66X/m6OcNILcQAdm5mZyV/jpFmDk5OTPPq1w8PDYWNjI4+ut7CwMBwcHOTR7SsNo/R3S39H6IFlBehU6UbExB0H0AdxAJ0qmVK/Yr8B9EEcQKdqjmWaOYA+2HMAndra2hr29/fzaJzNzc1hdXU1j36tdM9Bcpcb/ko3YtpzQE/EAXRqbW2t6DRBUvIDWRMH95k4oCeWFaBTpf9yTsYcYQQmnziATtXEgXcVoA+WFSBLU+wtvJ0w5t2DdFJhfn4+j8ZJ+wE+fvyYR9ezrACTSxxAVvPOwH10fn6ev37u+Ph4WFlZyaNx0g9j+oEcSxzA5LKsAB2queNgeno6fwGtEwfQoZrlE+8KQD8sK0DW07JCzR0HpU81ly4rpM2OY+9Q+B3+/PPP4du3b3l0PcsK9EQcQNZTHKT9BmnfQYnSH8fSOCjd03BTHl6Cn7OsAB2q2XPgGCP0QxxAh0pfZEwPLrkACfphWQGyXpYVUhg8f/48j8ZJDy59+PAhj8YpXVZIAXKXDzvd9rIKTDJxAFkvcVBzx0HaiJg2JJZwzwFMLnEAWWkcpJ3193Gq/bobEvf29obXr1/n0Tjp/zW9yFhCHMDkEgeQlcZBukp4Es/+b29vDzs7O3k0TslTzVfEAUwuGxKhM6WbERMnFaAv4gA6U3OM0UkF6Is4gM7UXJ1s5gD6Ig6gI2nWoOTK4MSbCtAfcQAdubi4yF/jeY0R+uO0AmQ9nFY4Ojoa1tbW8micFy9eDG/fvs2j8dK7BTUx8jPpsaiSzZTpdEXJQ1HXSRc0pYuaoAfiALIe4qDmjoP19fVr7064C6WPRb1582ZYXl7OI6CEZQXoSMkrhFdsRoT+iAPoSM0dB6bSoT+WFSDrYVkhPbhUGginp6ej7jlIyxVfv37No9/v06dPRTMf6TbD29xMubi4aNmCZokDyHqIg5mZmfw1Tpo1ODk5yaNfW1paqlq2mFS1GzVhElhWgE7U/HA7xgh9EgfQiZpjhS5Agj6JA+hEzcyBOIA+iQPohGUFYCxxAJ3wVDMwljiATniqGRjLUUbISo8y3tf1+PSewObmZh794+nTp8UvMp6fn+ev6znKCO0QB5CVxsF99aMfrTRrMD8/n0fjlNxxkKRHnUrjY5I9fPjw+0VI0CJxAFnLcZD2G6TbEUukGwYPDg7yCOiJPQfQgZrpfm8qQL/MHEDW8szBf/FUc1piuM23Fu6aOx/oiTiArOU42NraGvb39/NonN3d3e+bG2sdHh4OGxsbeTT50hJLWmqBHlhWgA54qhkoIQ6gAzV3HLgdEfolDqADNTMH1tihX+IAGldzUmF2djZ/AT2yIRGys7OzJi7xScsB//5X//Hx8bCyspJH4/yOOw5sSITJJQ6gcTU/0qurqz+8grmEOIDJZVkBGuepZqCUmQNo3Nra2vd3D0rc9I6DpHTmIAXJXf7LvPQtCDMH9EQcQOPSfoO076DE+/fvh7m5uTyqUxoHv2OfQ4nSVyTFAT2xrACNSxstSz1+/Dh/AT0SB9C40hMY6WbEqampPAJ6ZFkBGvZfPtVcs+fgJg89lUrvTdhzAD8mDqBhNXccpI2IaUPiTTnKCJPLsgI0rGa/gdsRAXEADau548CbCoA4gIZ5cAmoIQ6gYZ5qBmqIA2iYmQOghjiARtXMGtiMCCTiABpVM2uQLkACcM8BNCo9LJQeXSrxO55qvpKOUZY++HSfLS8vW3KhG+IAGrW9vT3s7Ozk0TgpDFIgAH2zrACNcscBUEscQKMuLi7y13iOMQKJZQVo1NLSUvHsQVpWKN2UODc355QDNEYcQKNmZmby1+1aX1+/09cUgdtnWQEaVHOMEeCKOIAG1VyABHBFHECDap5qBrgiDqBBNccYAa6IA2hQzTFGgCviABpk5gC4CXEADRIHwE2IA2hMOqnw7du3PAIoJw6gMe44AG5KHEBj3HEA3JQ4gMa44wC4KW8rQGOOjo7uNBAWFxeHhYWFPAJaIA4AgMCyAgAQiAMAIBAHAEAgDgCAQBwAAIE4AAACcQAABOIAAAjEAQAQiAMAIBAHAEAgDgCAQBwAAIE4AAACcQAABOIAAAjEAQAQiAMAIBAHAEAgDgCAQBwAAIE4AAACcQAABOIAAAjEAQAQiAMAIBAHAEAgDgCAQBwAAIE4AAACcQAABOIAAAjEAQAQiAMAIBAHAEAgDgCAQBwAAIE4AAACcQAABOIAAAjEAQAQiAMAIBAHAEAgDgCAQBwAAIE4AAACcQAABOIAAAjEAQAQiAMAIBAHAEAgDgCAQBwAAIE4AAACcQAABOIAAAjEAQAQiAMAIBAHAEAgDgCAfxmG/wOtMVaOtMIE7QAAAABJRU5ErkJggg=="


        id = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'group_id'")[0]['no'])+1
        owner = authorized[1]
        name = data.name
        description = data.description
        operator = "[]"
        members = "[]"
        warn = 0
        if data.image == "" or data.image == None:
            image = baseimage
        else:
            image = data.image

        res = execute_sql("INSERT INTO group (id, name, description, owner, operator, members, warn, type, groupimg) VALUES ({0},'{1}','{2}','{3}','{4}', {5}, '{6})'".format(id, name, description, owner, operator, members, warn, image))

        return "그룹을 생성했습니다."
    
@groupapi.post('/invite')
async def group_invite(group:invite_group, authorized: bool = Depends(verify_token)):
    if authorized:
        er023 = {'code': 'ER023', 'message':'해당 아이디에 해당하는 그룹은 존재하지 않습니다.'}
        er024 = {'code': 'ER024', 'message':'해당 그룹의 관리자가 아닙니다.'}
        groups = execute_sql("SELECT `id`, `owner`, `operator`, `name` FROM `group` WHERE `id` = {0}".format(group.group_id))
        if len(groups) == 0:
            raise HTTPException(404, er023)
        
        n_group = groups[0]
        operators = json.loads(groups[0]['operator'])
        if authorized[1] != n_group['owner'] or not authorized[1] in operators:
            raise HTTPException(403, er024)
        
        email = "SELECT `email` FROM user WHERE `ID` = '{0}'".format(group.target_id)

        link = "http://130.162.141.91/group/invite/{0}/{1}/{2}".format(group.group_id, authorized[1], group.target_id)

        newno = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'log_invite'")[0]['no'])+1

        execute_sql("INSERT INTO log_invite (no, type, req, tar) VALUES ({0},'{1}','{2}','{3}')".format(newno, "group_invite", authorized[1], group.target_id))

        execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'log_invite'".format(newno))

        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[다봄] {0} 모임으로부터 모임 초대가 도착했습니다!'.format(groups[0]['name'])
        msg['From'] = "noreply.dabom@gmail.com"
        msg['To'] = email

        text = "그룹 멤버 초대"
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
                                    <a style="text-decoration: none; color: rgba(0,0,0,0.87);" rel="noreferrer noopener"target="_blank">{0}</a> 모임이 회원님을 모임에 초대했습니다.
                                </div>
                                    <div style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 14px; color: rgba(0,0,0,0.87); line-height: 20px;padding-top: 20px; text-align: center;">    
                                        <p> {0} 모임이 회원님을 모임에 초대했습니다. </p>
                                        <p> 아래 링크를 클릭하여 모임 초대를 확인할수 있습니다. </p>
                                        <a href='{1}'> 모임 초대 확인하기 </a>
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
""".format(groups[0]['name'], link)
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        msg.attach(part1)
        msg.attach(part2)

        try:
            s.sendmail("noreply.dabom@gmail.com", email, msg.as_string())
        except smtplib.SMTPServerDisconnected:
            d = smtplib.SMTP("smtp.gmail.com", 587)
            d.ehlo()
            d.starttls()
            d.login("noreply.dabom", "sxhmurnajtenjtbr")
            d.sendmail("noreply.dabom@gmail.com", email, msg.as_string())
        except smtplib.SMTPSenderRefused: #sender refused to send message
            d = smtplib.SMTP("smtp.gmail.com", 587)
            d.ehlo()
            d.starttls()
            d.login("noreply.dabom", "sxhmurnajtenjtbr")
            d.sendmail("noreply.dabom@gmail.com", email, msg.as_string())