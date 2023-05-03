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

@groupapi.post('/create')
async def create_group(data: create_group, authorized: bool = Depends(verify_token)):
    er022 = {'code': 'ER022', 'message': '시스템에 의해 당신의 그룹생성 권한은 박탈되었습니다. (접근 차단된 그룹의 소유자입니다.)'}
    if authorized:
        ban = execute_sql("SELECT group_create_ban FROM user WHERE `ID` = %s" % authorized[1])[0]['group_create_ban']
        if ban:
            raise HTTPException(403, er022)

        id = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'group_id'")[0]['no'])+1
        owner = authorized[1]
        name = data.name
        description = data.description
        operator = "[]"
        members = "[]"
        warn = 0

        res = execute_sql("INSERT INTO group (id, name, description, owner, operator, members, warn) VALUES ({0},'{1}','{2}','{3}','{4}',{5})".format(id, name, description, owner, operator, members, warn))

        return "그룹을 생성했습니다."