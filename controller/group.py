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
import random
import string

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
        admin_token = "i>9/,tUmc_&==Ap|5)yk9$@H=T^ATpp]8UG@*E-nAWSag]pe<2"
        if token == admin_token:
            return True, "admin"
        else:
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

er023 = {'code': 'ER023', 'message':'해당 아이디에 해당하는 그룹은 존재하지 않습니다.'}
er024 = {'code': 'ER024', 'message':'해당 그룹의 관리자가 아닙니다.'}
er031 = {'code': 'ER031', 'message': '존재하지 않는 그룹입니다.'}
er032 = {'code': 'ER032', 'message': '접근 불가 그룹입니다.'}

async def group_log(group_id:int, type:string, req_id:string, tar_id:string):
    g_no = execute_sql("SELECT `no` FROM `food_no` WHERE `fetch` = 'group_log'")[0]['no'] + 1
    execute_sql("INSERT INTO `group_log` (no, group_id, type, req, tar) VALUES ({0},{1},'{2}','{3}','{4}')".format(g_no, group_id, type, req_id, tar_id)),
    execute_sql("UPDATE `food_no` SET `no` = {0} WHERE `fetch` = 'group_log'".format(g_no))
    return 'added'


@groupapi.get('/list/{page}')
async def list_group(page:int):
    spage = 9 * (page-1)
    groups = execute_sql("SELECT id as no, name, description, members, groupimg FROM `group` WHERE `deleted` = 'false' AND `banned` = 'false' LIMIT 9 OFFSET {0}".format(spage))
    return groups

@groupapi.get('/detail/{group_id}')
async def detail_group(group_id:int):
    
    group = execute_sql("SELECT *, `deleted`, `banned` FROM `group` WHERE id = {0}".format(group_id))

    if len(group) == 0:
        raise HTTPException(400, er031)
    
    if group[0]['deleted'] == 'true' or group[0]['banned'] == 'true':
        raise HTTPException(403, er032)
    
    return group[0]


@groupapi.post('/create')
async def create_group(data: create_group, authorized: bool = Depends(verify_token)):
    er022 = {'code': 'ER022', 'message': '시스템에 의해 당신의 그룹생성 권한은 박탈되었습니다. (접근 차단된 그룹의 소유자입니다.)'}
    er025 = {'code': 'ER025', 'message': '그룹타입은 Public, Private 만 허용됩니다.'}
    if authorized:
        ban = execute_sql("SELECT group_create_ban FROM user WHERE `ID` = '%s'" % authorized[1])[0]['group_create_ban']
        if ban == "True":
            raise HTTPException(403, er022)
        
        if data.type != 'Public' and data.type != 'Private':
            raise HTTPException(400, er025)
        
        baseimage = "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"


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

        res = execute_sql("INSERT INTO `group` (`id`, `name`, `description`, `owner`, `operator`, `members`, `warn`, `type`, `groupimg`, `deleted`, `banned`) VALUES ({0},'{1}','{2}','{3}','{4}', '{5}', {6},'{7}','{8}','false','false')".format(id, name, description, owner, operator, members, warn, data.type, image))
        execute_sql("UPDATE food_no SET `no` = {0} WHERE `fetch` = 'group_id'".format(id))
        await group_log(id, "create", authorized[1], "None")
        return "그룹을 생성했습니다."
    
@groupapi.post('/invite')
async def group_invite(group:invite_group, authorized: bool = Depends(verify_token)):
    if authorized:

        groups = execute_sql("SELECT `id`, `owner`, `operator`, `name` FROM `group` WHERE `id` = {0}".format(group.group_id))
        if len(groups) == 0:
            raise HTTPException(404, er023)
        
        n_group = groups[0]
        operators = json.loads(groups[0]['operator'])
        if authorized[1] != n_group['owner'] and not authorized[1] in operators and not authorized[1] == "admin":
            raise HTTPException(403, er024)
        
        email = execute_sql("SELECT `email` FROM user WHERE `ID` = '{0}'".format(group.target_id))[0]['email']

        f_list = execute_sql("SELECT `req_id`, `tar_id`, `group_id` FROM f_verify WHERE `type` = 'group'")
        data = {'req_id': authorized[1], 'tar_id': group.target_id, 'group_id': group.group_id}

        if data in f_list:
            execute_sql("DELETE FROM f_verify WHERE req_id = '%s' AND tar_id = '%s' AND group_id = %s" % (authorized[1], group.target_id, group.group_id))

        veri_list = execute_sql("SELECT `code` FROM f_verify WHERE `type` = 'group'")
        keys = []
        for key in veri_list:
            keys.append(key['code'])

        verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])

        while verifykey in keys:
            verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])

        r_key = authorized[1]

        link = "http://dabom.kro.kr/group/invite/{0}/{1}/{2}/{3}".format(group.group_id, r_key, group.target_id, verifykey)

        newno = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'log_invite'")[0]['no'])+1

        execute_sql("INSERT INTO f_verify (`code`, `req_id`, `tar_id`, `group_id`, `type`) VALUES ('{0}','{1}','{2}',{3},'{4}')".format(verifykey, r_key, group.target_id, group.group_id, "group")),

        execute_sql("INSERT INTO log_invite (no, type, req, tar) VALUES ({0},'{1}','{2}','{3}')".format(newno, "group_invite", r_key, group.target_id))

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
                                        <br><br>
                                        <a href='{1}'> 모임 초대 확인하기 </a>
                                        <br><br>                                      
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

        await group_log(group.group_id, "invite", r_key, group.target_id)

        return "모임 초대메일 전송됨"

@groupapi.post('/invite/{accept_type}/{group_id}/{req_id}/{tar_id}/{verifykey}')
async def process_invite(accept_type:str, group_id:int, req_id:str, tar_id:str, verifykey:str):
    er028 = {"code":"ER028", "message":"처리 타입은 accept/reject 만 허용됩니다."}
    if not accept_type == "accept" or accept_type == "reject":
        raise HTTPException(403, er028)
        
    data = execute_sql("SELECT `req_id`, `tar_id`, `group_id` FROM f_verify WHERE `code` = '{0}'".format(verifykey))
    er026 = {'code':'ER026', 'message':'올바르지 않은 인증키입니다.'}
    er027 = {'code':'ER027', 'message':'인증키에 저장된 정보와 일치하지 않습니다.'}

    if len(data) == 0:
        raise HTTPException(403, er026)

    data = data[0]
    if data['group_id'] != group_id:
        raise HTTPException(403, er027)
    
    if data['req_id'] != req_id:
        raise HTTPException(403, er027)
    
    if data['tar_id'] != tar_id:
        raise HTTPException(403, er027)
    
    if accept_type == 'accept':
        p_group = json.loads(execute_sql("SELECT `groups` FROM `user` WHERE `ID` = '%s'" % tar_id)[0]['groups'])
        p_group.append(group_id)
        execute_sql("UPDATE user SET `groups` = '{0}' WHERE ID = '{1}'".format(json.dumps(p_group), tar_id))
        g_members = json.loads(execute_sql("SELECT `members` FROM `group` WHERE id = '%s'" % group_id)[0]['members'])
        g_members.append(tar_id)
        execute_sql("UPDATE `group` SET members = '{0}' WHERE id = '{1}'".format(json.dumps(g_members), group_id))
        execute_sql("DELETE FROM f_verify WHERE `req_id` = '{0}' AND `tar_id` = '{1}' AND group_id = {2}".format(req_id, tar_id, group_id))
        await group_log(group_id, "invite_accept", req_id, tar_id, group_id)
        return "초대를 수락했습니다."
    elif accept_type == 'reject':
        execute_sql("DELETE FROM f_verify WHERE `req_id` = '{0}' AND `tar_id` = '{1}' AND group_id = {2}".format(req_id, tar_id, group_id))
        await group_log(group_id, "invite_reject", req_id, tar_id, group_id)
        return "초대를 거부하였습니다."

@groupapi.delete("/delete")
async def remove_group(group_id:int, authorized: bool = Depends(verify_token)):
    if authorized:
        group = execute_sql("SELECT `id`, `owner`, `operator`, `members`, `deleted`, `banned` FROM `group` WHERE `id` = %s" % group_id)

        if len(group) == 0:
            raise HTTPException(400, er031)
        
        group = group[0]
        if group['deleted'] == 'true' or group['banned'] == 'true':
            raise HTTPException(403, er032)

        if authorized[1] != group['owner'] and not authorized[1] in json.loads(group['operator']) and not authorized[1] == "admin":
            raise HTTPException(403, er024)
        
        members = json.loads(group['members'])

        for member in members:
            p_group = json.loads(execute_sql("SELECT `groups` FROM user WHERE ID = '%s'" % member)[0]['groups'])
            p_group.remove(group_id)
            execute_sql("UPDATE user SET `groups` = '{0}' WHERE ID = '{1}'".format(p_group, member)) 

        execute_sql("UPDATE `group` SET `deleted` = 'true' WHERE id = {0}".format(group_id))
        await group_log(group_id, "delete", authorized[1], group_id)

        return "그룹을 제거했습니다."
    
er033 =  {'code':'ER033', 'message':'해당 유저는 해당그룹의 멤버가 아닙니다.'}

@groupapi.post("/kick_member")
async def kick_member(member_id:str, group_id:int, authorized: bool = Depends(verify_token)):
    if authorized:
        group = execute_sql("SELECT `owner`, `operator`, `members` FROM `group` WHERE `id` = %s", group_id)
        if len(group) == 0:
            raise HTTPException(400, er031)
        
        n_group = group[0]
        if authorized[1] != n_group['owner'] and not authorized[1] in json.loads(n_group['operator']) and not authorized[1] == "admin":
            raise HTTPException(403, er024)

        members = json.loads(n_group['members'])
        if not member_id in members:
            raise HTTPException(400, er033)
            
        mem_g = json.loads(execute_sql("SELECT `groups` FROM user WHERE `ID` = '{0}' OR `ID` = 'DELETED-{0}'".format(member_id))[0]['groups'])

        mem_g.remove(group_id)
        members.remove(member_id)
            
        execute_sql("UPDATE `user` SET `groups` = {0} WHERE `ID` = '{1}' OR `ID` = 'DELETED-{1}'".format(mem_g ,member_id))
        execute_sql("UPDATE `group` SET `members` = {0} WHERE `id` = '{1}'".format(members, group_id))

        await group_log(group_id, "kick", authorized[1] or "admin", member_id)

        return "멤버를 추방했습니다."

er034 = {'code':'ER034', 'message':'해당 멤버는 이미 모임의 관리자입니다.'}

@groupapi.post("/appoint")
async def appoint_operator(group_id:int, user_id:str, authorized: bool = Depends(verify_token)):
    if authorized:
        group = execute_sql("SELECT `id`, `owner`,`operator`,`members` FROM `group` WHERE `id` = %s" % group_id)

        if len(group) == 0:
            raise HTTPException(404, er031)    

        d_group = group[0]

        if authorized[1] != d_group['owner'] and not authorized[1] in json.loads(d_group['operator']) and not authorized[1] == "admin":
            raise HTTPException(403, er024)
        
        if not user_id in json.loads(d_group['members']):
            raise HTTPException(400, er033)
        
        operators = json.loads(d_group['operator'])

        if user_id in operators or user_id == d_group['owner']:
            raise HTTPException(400, er034)
        
        operators = operators.append(user_id)
        execute_sql("UPDATE `group` SET `operator` = '%s' WHERE `id` = %s" % operators, group_id)
        await group_log(group_id, "appoint", authorized[1] or "admin", user_id)

        return "%s 님을 %s 모임의 관리자로 임명했습니다."
    
@groupapi.post("be_deprived")
async def be_deprived(group_id:int, user_id:str, authorized: bool = Depends(verify_token)):
    if authorized:
        group = execute_sql("SELECT `id`, `owner`,`operator`,`members` FROM `group` WHERE `id` = %s" % group_id)

        if len(group) == 0:
            raise HTTPException(404, er031)    

        d_group = group[0]

        if authorized[1] != d_group['owner'] and not authorized[1] in json.loads(d_group['operator']) and not authorized[1] == "admin":
            raise HTTPException(403, er024)
        
        if not user_id in json.loads(d_group['members']):
            raise HTTPException(400, er033)
        
        operators = json.loads(d_group['operator'])

        if user_id in operators or user_id == d_group['owner']:
            raise HTTPException(400, er034)
        
        operators = operators.remove(user_id)
        execute_sql("UPDATE `group` SET `operator` = '%s' WHERE `id` = %s" % operators, group_id)
        await group_log(group_id, "be_deprived", authorized[1] or "admin", user_id)

        return "%s 님을 %s 모임의 관리자로 임명했습니다."

class group_warn(BaseModel):
    group_id:int

@groupapi.post("/warn")
async def group_warn(group: group_warn, admin: bool = Depends(verify_token)):
    if admin and admin[1] == "admin":
        warn = execute_sql("SELECT warn, deleted, banned, owner, members FROM `group` WHERE `id` = %s" % group.group_id)

        if len(warn) == 0:
            raise HTTPException(404, er031)
        
        deleted = warn[0]['deleted']
        banned = warn[0]['banned']
        owner = warn[0]['owner']
        
        if deleted == "true" or banned == "true":
            raise HTTPException(403, er032)

        newwarn = warn[0]['warn'] + 1

        if newwarn > 3:
            execute_sql("UPDATE `group` SET `banned` = 'true', `warn` = {0} WHERE id = {1}".format(newwarn, group.group_id))
            execute_sql("UPDATE `user` SET `group_create_ban` = 'true' WHERE `ID` = '{0}'".format(owner))
            members = json.loads(warn[0]['members'])
            for member in members:
                g = execute_sql("SELECT groups FROM user WHERE `ID` = '{0}'".format(member))
                g.remove(group.group_id)
                execute_sql("UPDATE `user` SET `groups` = '{0}' WHERE `ID` = '{1}'".format(json.dumps(g), member))

            return "경고 최대 횟수를 초과하여 그룹이 제거되고 모든 멤버가 추방되었으며 그룹의 소유자는 더이상 그룹을 생성하지 못합니다."

        group_log(group.group_id, "warn", "admin", group.group_id)
        return "경고 횟수를 누적했습니다. 새 경고 누적치 : %s 번" % newwarn