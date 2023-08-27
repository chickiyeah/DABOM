import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, File, UploadFile, Cookie
from pydantic import BaseModel
from controller.database import execute_sql
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import _auth_utils
from firebase import Firebase
import datetime
from controller.credentials import verify_token, verify_admin_token
diaryapi = APIRouter(prefix="/api/diary", tags=["diary"])


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

unauthorized = {'code':'ER013','message':'UNAUTHORIZED (Authorzation Header Not Found)'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

post_not_found = {'code':'ER001','message':'해당 넘버의 글은 존채하지 않습니다'}
post_not_owner = {'code':'ER002','message':'본인의 글만 수정/삭제할수 있습니다.'}


@diaryapi.post('/add')
async def post_add(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        uid = authorized[1]
        imgs = data['images']
        foods = data['foods']
        title = data['title']
        memo = data['desc']
        friends = data['friends']
        eat_when = data['eat_when']
        s_with = data['with']
        to_kcal = data['total_kcal']

        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p_num = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'post_no'")[0]['no'])
        n_p_num = p_num+1
        execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'" % n_p_num)
        sql = f"INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES ({n_p_num}, '{uid}', '{title}','{memo}',\"{foods}\",\"{friends}\",'{created_at}',\"{imgs}\",'{eat_when}', '{s_with}', {to_kcal})"
        res = execute_sql(sql)
        return res
    
@diaryapi.post('/add_g')
async def post_add(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        uid = authorized[1]
        imgs = data['images']
        foods = data['foods']
        title = data['title']
        memo = data['desc']
        friends = data['friends']
        group = data['group']
        eat_when = data['eat_when']
        s_with = data['with']
        to_kcal = data['total_kcal']

        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p_num = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'post_no'")[0]['no'])
        n_p_num = p_num+1
        execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'" % n_p_num)
        sql = f"INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`group`,`eat_when`,`with`,`total_kcal`) VALUES ({n_p_num}, '{uid}', '{title}','{memo}',\"{foods}\",\"{friends}\",'{created_at}',\"{imgs}\",'{group}','{eat_when}','{s_with}',{to_kcal})"
        res = execute_sql(sql)
        return res
    
@diaryapi.get('/group/{group_id}/{page}')
async def get_group_post(group_id:int, page:int, authorized :bool = Depends(verify_token)):
    g_mem = execute_sql(f"SELECT members FROM `group` WHERE `id` = {group_id}")[0]['members']

    if authorized[1] in g_mem:
        page = page - 1

        if (page < 0):
            page = 0

        offset = page*3
        count = len(execute_sql(f"SELECT no from UserEat WHERE `group` = {group_id}"))
        res = execute_sql(f"SELECT * from UserEat WHERE `group` = {group_id} ORDER BY created_at ASC LIMIT 3 OFFSET {offset}")
        posts = []
        for post in res:
            comment = execute_sql(f"SELECT * from post_comments WHERE `post_id` = {post['no']} ORDER BY created_at ASC")
            post['comments'] = comment
            posts.append(post)


        j_res = {
            "posts": posts,
            "page": page+1,
            "total": count
        }

        return j_res
    
    else:
        raise HTTPException(401)

@diaryapi.post('/alone')
async def post_get(request:Request, authorized: bool = Depends(verify_token)):
    if authorized:
        json = await request.json()
        res = execute_sql(f"SELECT * from UserEat WHERE YEAR(created_at) = {json['year']} AND MONTH(created_at) = {json['month']} AND id = '{authorized[1]}' AND `with` = 'alone' LIMIT 3 OFFSET {(int(json['page'])-1)*3}")

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        return res

@diaryapi.post('/with')
async def post_get(request:Request, authorized: bool = Depends(verify_token)):
    if authorized:
        json = await request.json()
        res = execute_sql(f"SELECT * from UserEat WHERE YEAR(created_at) = {json['year']} AND MONTH(created_at) = {json['month']} AND id = '{authorized[1]}' AND (`with` = 'friend' OR `with` = 'couple') LIMIT 3 OFFSET {(int(json['page'])-1)*3}")

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        return res


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