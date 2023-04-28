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

diaryapi = APIRouter(prefix="/api/diary", tags=["diary"])

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

class add_diary(BaseModel):
    food_name:str
    food_category:str
    memo:Optional[str]
    kcal:int
    image:str
    eat_category:str

unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}


@diaryapi.post('/add')
async def post_add(data:add_diary, authorized: bool = Depends(verify_token)):
    if authorized:
        uid = authorized[1]
        imgbase64 = data.image
        f_name = data.food_name
        f_cate = data.food_category
        f_kcal = data.kcal
        memo = data.memo
        e_cate = data.eat_category
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO UserEat (ID, 먹은종류, 음식명, 음식종류, 칼로리, 음식이미지, 메모, Created_At) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" % (uid, e_cate, f_name, f_cate, f_kcal, imgbase64, memo, created_at)
        res = execute_sql(sql)
        return res
