import html
import json
import random
import string
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
#오늘일지 작성
async def post_add(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        uid = authorized[1]
        imgs = json.dumps(data['images'])
        foods = json.dumps(data['foods'])
        title = data['title']
        memo = data['desc']
        friends = json.dumps(data['friends'])
        eat_when = data['eat_when']
        s_with = data['with']
        to_kcal = data['total_kcal']

        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p_num = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'post_no'")[0]['no'])
        n_p_num = p_num+1
        execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'", (n_p_num))
        temp_post = execute_sql("SELECT * FROM temp_post WHERE `id` = %s", (uid))
        
        if len(temp_post) == 0:
            sql = "INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s)"
            res = execute_sql(sql, (n_p_num, uid, title, memo, foods, friends, created_at, imgs, eat_when, s_with, to_kcal))
        else:
            sql = "DELETE FROM temp_post WHERE `id` = %s"
            execute_sql(sql, (uid))
            sql = "INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s)"
            res = execute_sql(sql, (n_p_num, uid, title, memo, foods, friends, created_at, imgs, eat_when, s_with, to_kcal))

        
        return res
    
@diaryapi.post('/add_g')
#오늘 일지 작성 ( 그룹 에서 )
async def post_add(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        uid = authorized[1]
        imgs = json.dumps(data['images'])
        foods = json.dumps(data['foods'])
        title = data['title']
        memo = data['desc']
        friends = json.dumps(data['friends'])
        eat_when = data['eat_when']
        s_with = data['with']
        to_kcal = data['total_kcal']
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p_num = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'post_no'")[0]['no'])
        n_p_num = p_num+1
        temp_post = execute_sql("SELECT * FROM temp_post WHERE `id` = %s", (uid))
        
        if len(temp_post) == 0:
            try:
                group = data['group']
                execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'", (n_p_num))
                sql = "INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`group`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                res = execute_sql(sql, (n_p_num, uid, title, memo, foods, friends, created_at, imgs, group, eat_when, s_with, to_kcal))
            except KeyError:
                execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'", (n_p_num))
                sql = "INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                res = execute_sql(sql, (n_p_num, uid, title, memo, foods, friends, created_at, imgs,  eat_when, s_with, to_kcal))
        else:
            try:
                group = data['group']
                sql = "DELETE FROM temp_post WHERE `id` = %s"
                execute_sql(sql, (uid))
                execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'", (n_p_num))
                sql = "INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`group`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                res = execute_sql(sql, (n_p_num, uid, title, memo, foods, friends, created_at, imgs, group, eat_when, s_with, to_kcal))
            except KeyError:
                sql = "DELETE FROM temp_post WHERE `id` = %s"
                execute_sql(sql, (uid))
                execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'", (n_p_num))
                sql = "INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                res = execute_sql(sql, (n_p_num, uid, title, memo, foods, friends, created_at, imgs,  eat_when, s_with, to_kcal))

        return res

@diaryapi.get('/get_temp')
#임시 게시물 가져오기
async def temp_get(authorized: bool = Depends(verify_token)):
    if authorized:
        uid = authorized[1]
        temp_post = execute_sql("SELECT * FROM temp_post WHERE `id` = %s", (uid))
        
        if len(temp_post) == 0:
            raise HTTPException(404, "임시 게시글이 없습니다.")

        return temp_post

@diaryapi.post('/add_temp')
#임시 게시물 저장
async def post_add(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        uid = authorized[1]
        imgs = json.dumps(data['images'])
        foods = json.dumps(data['foods'])
        title = data['title']
        memo = data['desc']
        friends = json.dumps(data['friends'])
        eat_when = data['eat_when']
        s_with = data['with']
        to_kcal = data['total_kcal']

        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temp_post = execute_sql("SELECT * FROM temp_post WHERE `id` = %s", (uid))
        
        if len(temp_post) == 0:
            sql = "INSERT INTO temp_post (`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            res = execute_sql(sql, (uid, title, memo, foods, friends, created_at, imgs, eat_when, s_with, to_kcal))
        else:
            sql = "DELETE FROM temp_post WHERE `id` = %s"
            execute_sql(sql, (uid))
            sql = "INSERT INTO temp_post (`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            res = execute_sql(sql, (uid, title, memo, foods, friends, created_at, imgs, eat_when, s_with, to_kcal))

        return res
    
@diaryapi.post('/add_g_temp')
# 임시게시물 저장 (그룹)
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
        temp_post = execute_sql("SELECT * FROM temp_post WHERE `id` = %s", (uid))
        
        if len(temp_post) == 0:
            try:
                group = data['group']
                sql = "INSERT INTO temp_post (`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`group`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                res = execute_sql(sql, (uid, title, memo, foods, friends, created_at, imgs, group, eat_when, s_with, to_kcal))
            except KeyError:
                sql = "INSERT INTO temp_post (`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                res = execute_sql(sql, (uid, title, memo, foods, friends, created_at, imgs, eat_when, s_with, to_kcal))
        else:
            try:
                group = data['group']
                sql = "DELETE FROM temp_post WHERE `id` = %s"
                execute_sql(sql, (uid))
                sql = "INSERT INTO temp_post (`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`group`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                res = execute_sql(sql, (uid, title, memo, foods, friends, created_at, imgs, group, eat_when, s_with, to_kcal))
            except KeyError:
                sql = "DELETE FROM temp_post WHERE `id` = %s"
                execute_sql(sql, (uid))
                sql = "INSERT INTO temp_post (`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                res = execute_sql(sql, (uid, title, memo, foods, friends, created_at, imgs, eat_when, s_with, to_kcal))

        return res
    
@diaryapi.get('/group/{group_id}/{page}')
#그룹의 글 가져오기
async def get_group_post(group_id:int, page:int, authorized :bool = Depends(verify_token)):
    g_mem = execute_sql(f"SELECT members FROM `group` WHERE `id` = {group_id}", ())[0]['members']

    if authorized[1] in g_mem:
        page = page - 1

        if (page < 0):
            page = 0

        offset = page*3
        count = len(execute_sql("SELECT no from UserEat WHERE `group` = %s AND (deleted IS NULL OR deleted = 'false')", (group_id)))
        res = execute_sql("SELECT * from UserEat WHERE `group` = %s AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at ASC LIMIT 3 OFFSET %s", (group_id, offset))
        posts = []
        for post in res:
            comment = execute_sql("SELECT * from comments WHERE `post_id` = %s ORDER BY created_at ASC", (post['no']))
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

@diaryapi.get('/pola')
#폴라로이드 이미지 하나 가져오기
async def post_get(authorized: bool = Depends(verify_token)):
    if authorized:
        
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        nowspl = now.split('-')
        res = execute_sql("SELECT * from UserEat WHERE id = %s AND YEAR(created_at) = %s AND MONTH(created_at) = %s AND DAY(created_at) = %s AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at DESC LIMIT 1", (authorized[1], nowspl[0], nowspl[1], nowspl[2]))

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        j_res = {
            "post": res
        }
        
        return j_res

@diaryapi.post('/all')
#다봄기록 전체 가져오기 ( 개인 )
async def post_get(request:Request, authorized: bool = Depends(verify_token)):
    if authorized:
        
        json = await request.json()
        count = len(execute_sql("SELECT no from UserEat WHERE id = %s AND (deleted IS NULL OR deleted = 'false')", (authorized[1])))
        res = execute_sql(f"SELECT * from UserEat WHERE id = %s AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at DESC LIMIT 6 OFFSET %s", (authorized[1], (int(json['page'])-1)*6))

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        j_res = {
            "posts": res,
            "page": int(json['page']),
            "total": count
        }
        
        return j_res

@diaryapi.post('/alone')
#다봄기록 내기록 (개인) 글 가져오기
async def post_get(request:Request, authorized: bool = Depends(verify_token)):
    if authorized:
        
        json = await request.json()
        count = len(execute_sql("SELECT no from UserEat WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s AND id = %s AND `with` = 'alone' AND (deleted IS NULL OR deleted = 'false')", (json['year'], json['month'], authorized[1])))
        res = execute_sql("SELECT * from UserEat WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s AND id = %s AND `with` = 'alone' AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at "+json['sort']+" LIMIT 3 OFFSET %s", (json['year'], json['month'], authorized[1], (int(json['page'])-1)*3))

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        j_res = {
            "posts": res,
            "page": int(json['page']),
            "total": count
        }
        
        return j_res

@diaryapi.post('/with')
#다봄기록 친구와함께 글 가져오기
async def post_get(request:Request, authorized: bool = Depends(verify_token)):
    if authorized:
        json = await request.json()

        count = len(execute_sql("SELECT no from UserEat WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s AND id = %s AND (`with` = 'friend' OR `with` = 'couple') AND (deleted IS NULL OR deleted = 'false')", (json['year'], json['month'], authorized[1])))
        res = execute_sql("SELECT * from UserEat WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s AND id = %s AND (`with` = 'friend' OR `with` = 'couple') AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at "+json['sort']+" LIMIT 3 OFFSET %s", (json['year'], json['month'], authorized[1], (int(json['page'])-1)*3))

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        j_res = {
            "posts": res,
            "page": int(json['page']),
            "total": count
        }
        
        return j_res


@diaryapi.patch('/update')
#다봄기록 글 업데이트
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

        res = execute_sql("SELECT ID from UserEat WHERE `NO` = %s", (post_no))
        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        if res['NO'] != uid:
            raise HTTPException(403, post_not_owner)
        
        execute_sql("UPDATE UserEat SET `먹은종류` = %s, `음식명` = %s, `음식종류` = %s, `칼로리` = %s, `음식이미지` = %s, `메모` = %s, `친구` = %s, `제목` = %s WHERE `NO` = %s", (e_cate, f_name, f_cate, f_kcal, imgbase64, memo, with_friend, title, post_no))
        return "글이 업데이트 되었습니다."

@diaryapi.delete('/delete')
#다봄기록 글 삭제
async def post_delete(request: Request, authorzed: bool = Depends(verify_token)):
    if authorzed:
        data = await request.json()
        post_ids = data['post_ids']
        notes = execute_sql("SELECT `no` FROM UserEat WHERE `id` = %s AND (deleted IS NULL OR deleted = 'false')", authorzed[1])
        note_num = []
        for note in notes:
            note_num.append(int(note['no']))

        sqls = []
        for post_id in post_ids:
            sql = "UPDATE UserEat SET `deleted` = 'true' WHERE `no` = %s" % post_id
            sqls.append(sql)
            if not int(post_id) in note_num:
                raise HTTPException(403, post_not_owner)

        for sql in sqls:
            execute_sql(sql, ())

        return "글을 삭제하였습니다."
    
@diaryapi.post('/detail/{post_id}/comment/main')
#다봄기록 메인 댓글
async def write_main_comment(post_id:int, request: Request, authorized : bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        comment = html.escape(data['comment'])
        comment_id = execute_sql(f"SELECT `no` FROM `food_no` WHERE `fetch` = 'comments'", ())[0]['no'] + 1
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        execute_sql("INSERT INTO `comments` (`post_id`, `id`, `type`, `comment`, `writer`, `created_at`) VALUES (%s, %s, 'main', %s, %s, %s)", (post_id, comment_id, comment, authorized[1], created_at))
        execute_sql("UPDATE `food_no` SET `no` = %s WHERE `fetch` = 'comments'", comment_id)        

        return "main comment writed"

@diaryapi.post('/detail/{post_id}/comment/{main_comment_id}/sub')
#다봄기록 서브댓글
async def write_sub_comment(post_id:int, main_comment_id:int, request: Request, authorized : bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        comment = html.escape(data['comment'])
        comment_id = execute_sql(f"SELECT `no` FROM `food_no` WHERE `fetch` = 'comments'", ())[0]['no'] + 1
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        execute_sql("INSERT INTO `comments` (`post_id`, `id`, `type`, `comment`, `writer`, `main_comment`) VALUES (%s, %s, 'sub', %s, %s, %s)",  (post_id, comment_id, comment, authorized[1], main_comment_id))
        execute_sql("UPDATE `food_no` SET `no` = %s WHERE `fetch` = 'comments'", (comment_id))   

        return "sub comment writed"
    
@diaryapi.post('/detail/{post_id}/comment/{comment_id}/edit')
#다봄기록 댓글 수정
async def edit_comment(post_id: int, comment_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        new_comment = html.escape(data['comment'])
        
        comment = execute_sql("SELECT writer, `comment`, `deleted` FROM `comments` WHERE `id` = %s AND `post_id` = %s", (comment_id, post_id))

        if (len(comment) == 0):
            raise HTTPException(404, "해당 댓글을 찾을수 없습니다.")

        writer = comment[0]['writer']
        o_comment = comment[0]['comment']
        deleted = comment[0]['deleted']

        if (deleted == 'true'):
            raise HTTPException(404, "해당 댓글을 찾을수 없습니다.")

        if (writer != authorized[1]):
            raise HTTPException(403, "댓글 수정은 작성자만 가능합니다.")
        
        edited_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        execute_sql("UPDATE `comments` SET `comment` = %s WHERE `id` = %s", (new_comment, comment_id))
        execute_sql("INSERT INTO `comment_change_log` (`comment_id`, `editor`, `origin_comment`, `new_comment`, `edited_at`) VALUES (%s, %s, %s, %s, %s)", (comment_id, authorized[1], o_comment, new_comment, edited_at))

        return "comment_updated"
    
@diaryapi.delete('/detail/{post_id}/comment/{comment_id}/remove')
#다봄기록 댓글 삭제
async def edit_comment(post_id: int, comment_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:     
        comment = execute_sql("SELECT writer, `comment`, `deleted` FROM `comments` WHERE `id` = %s AND `post_id` = %s", (comment_id, post_id))

        if (len(comment) == 0):
            raise HTTPException(404, "해당 댓글을 찾을수 없습니다.")

        writer = comment[0]['writer']
        deleted = comment[0]['deleted']

        if (deleted == 'true'):
            raise HTTPException(404, "해당 댓글을 찾을수 없습니다.")

        if (writer != authorized[1]):
            raise HTTPException(403, "댓글 삭제는 작성자만 가능합니다.")

        execute_sql("UPDATE `comments` SET `deleted` = 'true' WHERE `id` = %s", (comment_id))   

        return "comment_deleted"

@diaryapi.get("/detail/{post_id}/comments")
#다봄기록 댓글 가져오기 ( 이거 주로 사용 )
async def get_post_comments(post_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        notes = execute_sql("SELECT `no` FROM UserEat WHERE `id` = %s AND `no` = %s AND (deleted IS NULL OR deleted = 'false')", (authorized[1], post_id))

        if len(notes) == 0:
            raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")
        
        comments = execute_sql("SELECT * FROM comments WHERE `post_id` = %s AND `type` = 'main' AND `deleted` = 'false' ORDER BY created_at DESC", (post_id))

        r_comments = []

        for comment in comments:
            post_id = comment['post_id']
            id = comment['id']
            print("SELECT * FROM comments WHERE post_id = %s AND `main_comment` = %s AND `type` = 'sub' ORDER BY created_at ASC", (post_id, id))
            subcomments = execute_sql("SELECT * FROM comments WHERE post_id = %s AND `main_comment` = %s AND `type` = 'sub' ORDER BY created_at ASC", (post_id, id))
            comment['sub_comments'] = subcomments
            r_comments.append(html.unescape(comment))

        return r_comments


@diaryapi.get("/detail/{post_id}")
#다봄기록 글 상세 정보
async def get_post_detail(post_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        notes = execute_sql("SELECT * FROM UserEat WHERE `id` = %s AND `no` = %s AND (deleted IS NULL OR deleted = 'false')", (authorized[1], post_id))

        if len(notes) == 0:
            raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")

        return notes[0]
    
@diaryapi.get("/detail/{group_id}/{post_id}")
async def get_group_post_detail(group_id: int, post_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        notes = execute_sql("SELECT * FROM UserEat WHERE `id` = %s AND `no` = %s AND `group` = %s AND (deleted IS NULL OR deleted = 'false')", (authorized[1], post_id, group_id))

        if len(notes) == 0:
            raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")

        return notes[0]
    
@diaryapi.get("/detail/{group_id}/{post_id}/comments")
async def get_post_comments(group_id: int, post_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        notes = execute_sql("SELECT `no` FROM UserEat WHERE `id` = %s AND `no` = %s AND `group` = %s AND (deleted IS NULL OR deleted = 'false')", (authorized[1], post_id, group_id))

        if len(notes) == 0:
            raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")
        
        comments = execute_sql("SELECT * FROM comments WHERE `post_id` = %s AND `type` = 'main' AND `deleted` = 'false' ORDER BY created_at DESC", (post_id))

        r_comments = []

        for comment in comments:
            post_id = comment['post_id']
            id = comment['id']
            print("SELECT * FROM comments WHERE post_id = %s AND `main_comment` = %s AND `type` = 'sub' ORDER BY created_at ASC", (post_id, id))
            subcomments = execute_sql("SELECT * FROM comments WHERE post_id = %s AND `main_comment` = %s AND `type` = 'sub' ORDER BY created_at ASC", (post_id, id))
            comment['sub_comments'] = subcomments
            r_comments.append(html.unescape(comment))

        return r_comments
    
@diaryapi.post('/update')
async def post_add(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        post_no = data['post_id']
        imgs = data['images']
        foods = data['foods']
        title = data['title']
        memo = data['desc']
        friends = data['friends']
        eat_when = data['eat_when']
        s_with = data['with']
        to_kcal = data['total_kcal']

        #execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'" % n_p_num)
        #sql = f"INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES ({n_p_num}, '{uid}', '{title}','{memo}',\"{foods}\",\"{friends}\",'{created_at}',\"{imgs}\",'{eat_when}', '{s_with}', {to_kcal})"
        sql = "UPDATE UserEat SET `title` = %s, `desc` = %s, `foods` = %s, `friends` = %s, `images` = %s, `eat_when` = %s, `with` = %s, `total_kcal` = %s WHERE `no` = %s"
        
        res = execute_sql(sql, (title, memo, foods, friends, imgs, eat_when, s_with, to_kcal, post_no))
        return res

@diaryapi.post("/{post_no}/like")
async def like_post(post_no:int, authorized: bool = Depends(verify_token)):
    if authorized:
        user = execute_sql("SELECT `liked_post` FROM user WHERE `ID` = %s", (authorized[1]))
        
        if len(user) == 0:
            raise HTTPException(404, "user not found")
        
        liked_post = json.loads(user[0]['liked_post'])

        if post_no in liked_post:
            raise HTTPException(403, "이미 좋아요를 누른 게시글 입니다.")
        else:    
            post_like = int(execute_sql("SELECT `likecount` FROM `UserEat` WHERE `no` = %s", (post_no))[0]['likecount'] )
            liked_post.append(post_no)
            execute_sql("UPDATE `UserEat` SET `likecount` = %s WHERE `no` = %s", (post_like + 1, post_no))
            execute_sql("UPDATE `user` SET `liked_post` = %s WHERE `ID` = %s", (json.dumps(liked_post), authorized[1]))

        return True
    
@diaryapi.post("/{post_no}/unlike")
async def like_post(post_no:int, authorized: bool = Depends(verify_token)):
    if authorized:
        user = execute_sql("SELECT `liked_post` FROM user WHERE `ID` = %s", (authorized[1]))
        
        if len(user) == 0:
            raise HTTPException(404, "user not found")
        
        liked_post = json.loads(user[0]['liked_post'])

        if post_no in liked_post:
            post_like = int(execute_sql("SELECT `likecount` FROM `UserEat` WHERE `no` = %s")[0]['likecount'], (post_no))

            liked_post.remove(post_no)
            execute_sql("UPDATE `UserEat` SET `likecount` = %s WHERE `no` = %s", (post_like - 1, post_no))
            execute_sql("UPDATE `user` SET `liked_post` = %s WHERE `ID` = %s", (json.dumps(liked_post), authorized[1]))
        else:
            raise HTTPException(404, "좋아요를 누른 게시글이 아닙니다.")

        return True
    
@diaryapi.post('/{post_id}/share')
async def post_delete(request: Request, post_id:int, authorzed: bool = Depends(verify_token)):
    if authorzed: 
        notes = execute_sql("SELECT `no` FROM UserEat WHERE `id` = %s AND (deleted IS NULL OR deleted = 'false')", (authorzed[1]))
        #print(notes)
        note_num = []
        for note in notes:
            note_num.append(int(note['no']))

        #print(note_num)
        veri_list = execute_sql("SELECT `code` FROM f_verify WHERE `type` = 'post_share'", ())
        keys = []
        for key in veri_list:
            keys.append(key['code'])

        verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])

        while verifykey in keys:
            verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])

        if not int(post_id) in note_num:
            raise HTTPException(403, post_not_owner)

        execute_sql("INSERT INTO f_verify (`code`, `req_id`, `tar_id`, `group_id`, `type`) VALUES (%s, %s, %s ,0,'post_share')", (verifykey, authorzed[1], "post_"+post_id))

        return f"https://dabom.kro.kr/record_my?id={post_id}&v_key={verifykey}"
    
@diaryapi.post('/{post_id}/check_key')
async def share_key_check(request: Request, post_id: str):
        json = await request.json()
        key = json['verify_key']
        veri_list = execute_sql("SELECT `code` FROM f_verify WHERE `type` = 'post_share'", ())
        
        keys = []
        for key1 in veri_list:
            keys.append(key1['code'])

        print(keys)
        if key in keys:
            notes = execute_sql("SELECT * FROM UserEat WHERE `no` = %s AND (deleted IS NULL OR deleted = 'false')", (post_id))
            comments = execute_sql("SELECT * FROM comments WHERE `post_id` = %s AND `type` = 'main' AND `deleted` = 'false' ORDER BY created_at DESC", (post_id))

            r_comments = []

            for comment in comments:
                post_id = comment['post_id']
                id = comment['id']
                subcomments = execute_sql("SELECT * FROM comments WHERE post_id = %s AND `main_comment` = %s AND `type` = 'sub' ORDER BY created_at ASC", (post_id, id))
                comment['sub_comments'] = subcomments
                r_comments.append(html.unescape(comment))


            if len(notes) == 0:
                raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")
            r_note = notes[0]
            r_note['comments'] = r_comments
            return r_note
        else:
            raise HTTPException(403)