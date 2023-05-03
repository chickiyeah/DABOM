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
    title:str
    memo:Optional[str]
    kcal:int
    image:Optional[str]
    eat_category:str
    withfriend:Optional[list]

class update_diary(BaseModel):
    no:int
    food_name:str
    food_category:str
    title:str
    memo:Optional[str]
    kcal:int
    image:Optional[str]
    eat_category:str
    withfriend:Optional[list]

class delete_diary(BaseModel):
    no:int

unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

post_not_found = {'code':'ER001','message':'해당 넘버의 글은 존채하지 않습니다'}
post_not_owner = {'code':'ER002','message':'본인의 글만 수정/삭제할수 있습니다.'}


@diaryapi.post('/add')
async def post_add(data:add_diary, authorized: bool = Depends(verify_token)):
    if authorized:
        uid = authorized[1]
        imgbase64 = data.image
        f_name = data.food_name
        f_cate = data.food_category
        f_kcal = data.kcal
        title = data.title
        memo = data.memo
        e_cate = data.eat_category
        with_friend = str(data.withfriend)
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p_num = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'post_no'")[0]['no'])
        n_p_num = p_num+1
        execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'" % n_p_num)
        sql = "INSERT INTO UserEat (`NO`, `ID`, `먹은종류`, `음식명`, `음식종류`, `칼로리`, `음식이미지`, `메모`, `Created_At`, `친구`, `제목`) VALUES (%s,'%s','%s','%s','%s','%s',\"%s\",'%s','%s','%s','%s')" % (n_p_num, uid, e_cate, f_name, f_cate, f_kcal, imgbase64, memo, created_at, with_friend, title)
        res = execute_sql(sql)
        return res

@diaryapi.get('/with_friend/{page}')
async def get_with_friend(page:int, authorized: bool = Depends(verify_token)):
    if authorized:
        friends = json.loads(execute_sql("SELECT friends FROM user WHERE `ID` = '%s'" % authorized[1])[0]['friends'])
        s_friend = "ID = '%s' " % authorized[1]
        for friend in friends:
            s_friend = s_friend + "OR ID = '%s'" % friend
        
        diarys = execute_sql("SELECT * FROM UserEat WHERE %s LIMIT 10 OFFSET %s0" % (s_friend, page))

        return diarys


@diaryapi.patch('/update')
async def post_update(data:update_diary, authorized: bool = Depends(verify_token)):
    if authorized:
        uid = authorized[1]
        post_no = data.no
        imgbase64 = data.image
        f_name = data.food_name
        f_cate = data.food_category
        f_kcal = data.kcal
        title = data.title
        memo = data.memo
        e_cate = data.eat_category
        with_friend = str(data.withfriend)

        res = execute_sql("SELECT ID from UserEat WHERE `NO` = %s" % post_no)
        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        if res['NO'] != uid:
            raise HTTPException(403, post_not_owner)
        
        execute_sql("UPDATE UserEat SET `먹은종류` = '%s', `음식명` = '%s', `음식종류` = '%s', `칼로리` = %s, `음식이미지` = '%s', `메모` = '%s', `친구` = '%s', `제목` = '%s' WHERE `NO` = %s" % (e_cate, f_name, f_cate, f_kcal, imgbase64, memo, with_friend, title, post_no))
        return "글이 업데이트 되었습니다."
    
@diaryapi.delete('/delete')
async def post_delete(data: delete_diary, authorzed: bool = Depends(verify_token)):
    if authorzed:
        no = data.no
        note = execute_sql("SELECT `NO`, `제목` FROM UserEat WHERE ID = %s" % authorzed[1])
        if len(note) == 0:
            raise HTTPException(404, post_not_found)
        
        if no != int(note[0]['NO']):
            raise HTTPException(403, post_not_owner)
        
        execute_sql("UPDATE UserEat SET `NO` = '%s', `제목` = '%s' WHERE `NO` = %s" % ("DELETED-"+no, "DELETED-"+note[0]['제목'], no))
        return "글을 삭제하였습니다."
    
@diaryapi.get('/get/{post_no}')
async def post_get(post_no:int):
    res = execute_sql("SELECT * from UserEat WHERE `NO` = %s" % post_no)

    if len(res) == 0:
        raise HTTPException(404, post_not_found)
    
    return res