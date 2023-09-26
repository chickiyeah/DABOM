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
        eat_when = data['eat_when']
        s_with = data['with']
        to_kcal = data['total_kcal']
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p_num = int(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'post_no'")[0]['no'])
        n_p_num = p_num+1
        try:
            group = data['group']
            execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'" % n_p_num)
            sql = f"INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`group`,`eat_when`,`with`,`total_kcal`) VALUES ({n_p_num}, '{uid}', '{title}','{memo}',\"{foods}\",\"{friends}\",'{created_at}',\"{imgs}\",'{group}','{eat_when}','{s_with}',{to_kcal})"
            res = execute_sql(sql)
        except KeyError:
            execute_sql("UPDATE food_no SET `no` = %s WHERE `fetch` = 'post_no'" % n_p_num)
            sql = f"INSERT INTO UserEat (`no`,`id`,`title`,`desc`,`foods`,`friends`,`created_at`,`images`,`eat_when`,`with`,`total_kcal`) VALUES ({n_p_num}, '{uid}', '{title}','{memo}',\"{foods}\",\"{friends}\",'{created_at}',\"{imgs}\",'{eat_when}', '{s_with}', {to_kcal})"
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
        count = len(execute_sql(f"SELECT no from UserEat WHERE `group` = {group_id}  AND (deleted IS NULL OR deleted = 'false')"))
        res = execute_sql(f"SELECT * from UserEat WHERE `group` = {group_id} AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at ASC LIMIT 3 OFFSET {offset}")
        posts = []
        for post in res:
            comment = execute_sql(f"SELECT * from comments WHERE `post_id` = {post['no']} ORDER BY created_at ASC")
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
async def post_get(authorized: bool = Depends(verify_token)):
    if authorized:
        
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        nowspl = now.split('-')
        res = execute_sql(f"SELECT * from UserEat WHERE id = '{authorized[1]}'AND YEAR(created_at) = {nowspl[0]} AND MONTH(created_at) = {nowspl[1]} AND DAY(created_at) = {nowspl[2]} AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at DESC LIMIT 1")

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        j_res = {
            "post": res
        }
        
        return j_res

@diaryapi.post('/all')
async def post_get(request:Request, authorized: bool = Depends(verify_token)):
    if authorized:
        
        json = await request.json()
        count = len(execute_sql(f"SELECT no from UserEat WHERE id = '{authorized[1]}' AND (deleted IS NULL OR deleted = 'false')"))
        res = execute_sql(f"SELECT * from UserEat WHERE id = '{authorized[1]}' AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at DESC LIMIT 6 OFFSET {(int(json['page'])-1)*6}")

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        j_res = {
            "posts": res,
            "page": int(json['page']),
            "total": count
        }
        
        return j_res

@diaryapi.post('/alone')
async def post_get(request:Request, authorized: bool = Depends(verify_token)):
    if authorized:
        
        json = await request.json()
        count = len(execute_sql(f"SELECT no from UserEat WHERE YEAR(created_at) = {json['year']} AND MONTH(created_at) = {json['month']} AND id = '{authorized[1]}' AND `with` = 'alone' AND (deleted IS NULL OR deleted = 'false')"))
        res = execute_sql(f"SELECT * from UserEat WHERE YEAR(created_at) = {json['year']} AND MONTH(created_at) = {json['month']} AND id = '{authorized[1]}' AND `with` = 'alone' AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at {json['sort']} LIMIT 3 OFFSET {(int(json['page'])-1)*3}")

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        j_res = {
            "posts": res,
            "page": int(json['page']),
            "total": count
        }
        
        return j_res

@diaryapi.post('/with')
async def post_get(request:Request, authorized: bool = Depends(verify_token)):
    if authorized:
        json = await request.json()

        count = len(execute_sql(f"SELECT no from UserEat WHERE YEAR(created_at) = {json['year']} AND MONTH(created_at) = {json['month']} AND id = '{authorized[1]}' AND (`with` = 'friend' OR `with` = 'couple') AND (deleted IS NULL OR deleted = 'false')"))
        res = execute_sql(f"SELECT * from UserEat WHERE YEAR(created_at) = {json['year']} AND MONTH(created_at) = {json['month']} AND id = '{authorized[1]}' AND (`with` = 'friend' OR `with` = 'couple') AND (deleted IS NULL OR deleted = 'false') ORDER BY created_at {json['sort']} LIMIT 3 OFFSET {(int(json['page'])-1)*3}")

        if len(res) == 0:
            raise HTTPException(404, post_not_found)
        
        j_res = {
            "posts": res,
            "page": int(json['page']),
            "total": count
        }
        
        return j_res


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
async def post_delete(request: Request, authorzed: bool = Depends(verify_token)):
    if authorzed:
        data = await request.json()
        post_ids = data['post_ids']
        notes = execute_sql("SELECT `no` FROM UserEat WHERE `id` = '%s' AND (deleted IS NULL OR deleted = 'false')" % authorzed[1])
        note_num = []
        for note in notes:
            note_num.append(int(note['no']))

        print(note_num)

        sqls = []
        for post_id in post_ids:
            print(post_id)
            print(int(post_id) in note_num)
            sql = f"UPDATE UserEat SET `deleted` = 'true' WHERE `no` = {post_id}"
            sqls.append(sql)
            if not int(post_id) in note_num:
                raise HTTPException(403, post_not_owner)

        for sql in sqls:
            execute_sql(sql)

        return "글을 삭제하였습니다."
    
@diaryapi.post('/detail/{post_id}/comment/main')
async def write_main_comment(post_id:int, request: Request, authorized : bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        comment = html.escape(data['comment'])
        comment_id = execute_sql(f"SELECT `no` FROM `food_no` WHERE `fetch` = 'comments'")[0]['no'] + 1
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        execute_sql(f"INSERT INTO `comments` (`post_id`, `id`, `type`, `comment`, `writer`, `created_at`) VALUES ({post_id}, {comment_id}, 'main', '{comment}', '{authorized[1]}', '{created_at}')")
        execute_sql(f"UPDATE `food_no` SET `no` = {comment_id} WHERE `fetch` = 'comments'")        

        return "main comment writed"

@diaryapi.post('/detail/{post_id}/comment/{main_comment_id}/sub')
async def write_sub_comment(post_id:int, main_comment_id:int, request: Request, authorized : bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        comment = html.escape(data['comment'])
        comment_id = execute_sql(f"SELECT `no` FROM `food_no` WHERE `fetch` = 'comments'")[0]['no'] + 1
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        execute_sql(f"INSERT INTO `comments` (`post_id`, `id`, `type`, `comment`, `writer`, `created_at`, `main_comment`) VALUES ({post_id}, {comment_id}, 'sub', '{comment}', '{authorized[1]}', '{created_at}', {main_comment_id})")
        execute_sql(f"UPDATE `food_no` SET `no` = {comment_id} WHERE `fetch` = 'comments'")   

        return "sub comment writed"
    
@diaryapi.post('/detail/{post_id}/comment/{comment_id}/edit')
async def edit_comment(post_id: int, comment_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        new_comment = html.escape(data['comment'])
        
        comment = execute_sql(f"SELECT writer, `comment`, `deleted` FROM `comments` WHERE `id` = {comment_id} AND `post_id` = '{post_id}'")

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

        execute_sql(f"UPDATE `comments` SET `comment` = '{new_comment}' WHERE `id` = {comment_id}")
        execute_sql(f"INSERT INTO `comment_change_log` (`comment_id`, `editor`, `origin_comment`, `new_comment`, `edited_at`) VALUES ({comment_id}, '{authorized[1]}', '{o_comment}', '{new_comment}', '{edited_at}')")

        return "comment_updated"
    
@diaryapi.delete('/detail/{post_id}/comment/{comment_id}/remove')
async def edit_comment(post_id: int, comment_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:     
        comment = execute_sql(f"SELECT writer, `comment`, `deleted` FROM `comments` WHERE `id` = {comment_id} AND `post_id` = '{post_id}'")

        if (len(comment) == 0):
            raise HTTPException(404, "해당 댓글을 찾을수 없습니다.")

        writer = comment[0]['writer']
        deleted = comment[0]['deleted']

        if (deleted == 'true'):
            raise HTTPException(404, "해당 댓글을 찾을수 없습니다.")

        if (writer != authorized[1]):
            raise HTTPException(403, "댓글 삭제는 작성자만 가능합니다.")

        execute_sql(f"UPDATE `comments` SET `deleted` = 'true' WHERE `id` = {comment_id}")   

        return "comment_deleted"

@diaryapi.get("/detail/{post_id}/comments")
async def get_post_comments(post_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        notes = execute_sql(f"SELECT `no` FROM UserEat WHERE `id` = '{authorized[1]}' AND `no` = {post_id} AND (deleted IS NULL OR deleted = 'false')")

        if len(notes) == 0:
            raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")
        
        comments = execute_sql(f"SELECT * FROM comments WHERE `post_id` = {post_id} AND `type` = 'main' AND `deleted` = 'false' ORDER BY created_at DESC")

        r_comments = []

        for comment in comments:
            post_id = comment['post_id']
            id = comment['id']
            print(f"SELECT * FROM comments WHERE post_id = {post_id} AND `main_comment` = {id} AND `type` = 'sub' ORDER BY created_at ASC")
            subcomments = execute_sql(f"SELECT * FROM comments WHERE post_id = {post_id} AND `main_comment` = {id} AND `type` = 'sub' ORDER BY created_at ASC")
            comment['sub_comments'] = subcomments
            r_comments.append(html.unescape(comment))

        return r_comments


@diaryapi.get("/detail/{post_id}")
async def get_post_detail(post_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        notes = execute_sql(f"SELECT * FROM UserEat WHERE `id` = '{authorized[1]}' AND `no` = {post_id} AND (deleted IS NULL OR deleted = 'false')")

        if len(notes) == 0:
            raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")

        return notes[0]
    
@diaryapi.get("/detail/{group_id}/{post_id}")
async def get_group_post_detail(group_id: int, post_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        notes = execute_sql(f"SELECT * FROM UserEat WHERE `id` = '{authorized[1]}' AND `no` = {post_id} AND `group` = {group_id} AND (deleted IS NULL OR deleted = 'false')")

        if len(notes) == 0:
            raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")

        return notes[0]
    
@diaryapi.get("/detail/{group_id}/{post_id}/comments")
async def get_post_comments(group_id: int, post_id: int, request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        notes = execute_sql(f"SELECT `no` FROM UserEat WHERE `id` = '{authorized[1]}' AND `no` = {post_id} AND `group` = {group_id} AND (deleted IS NULL OR deleted = 'false')")

        if len(notes) == 0:
            raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")
        
        comments = execute_sql(f"SELECT * FROM comments WHERE `post_id` = {post_id} AND `type` = 'main' AND `deleted` = 'false' ORDER BY created_at DESC")

        r_comments = []

        for comment in comments:
            post_id = comment['post_id']
            id = comment['id']
            print(f"SELECT * FROM comments WHERE post_id = {post_id} AND `main_comment` = {id} AND `type` = 'sub' ORDER BY created_at ASC")
            subcomments = execute_sql(f"SELECT * FROM comments WHERE post_id = {post_id} AND `main_comment` = {id} AND `type` = 'sub' ORDER BY created_at ASC")
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
        sql = f"UPDATE UserEat SET `title` = '{title}', `desc` = '{memo}', `foods` = \"{foods}\", `friends` = \"{friends}\", `images` = \"{imgs}\", `eat_when` = '{eat_when}', `with` = '{s_with}', `total_kcal` = {to_kcal} WHERE `no` = {post_no}"
        
        res = execute_sql(sql)
        return res

@diaryapi.post("/{post_no}/like")
async def like_post(post_no:int, authorized: bool = Depends(verify_token)):
    if authorized:
        user = execute_sql(f"SELECT `liked_post` FROM user WHERE `ID` = '{authorized[1]}'")
        
        if len(user) == 0:
            raise HTTPException(404, "user not found")
        
        liked_post = json.loads(user[0]['liked_post'])

        if post_no in liked_post:
            raise HTTPException(403, "이미 좋아요를 누른 게시글 입니다.")
        else:    
            post_like = int(execute_sql(f"SELECT `likecount` FROM `UserEat` WHERE `no` = {post_no}")[0]['likecount'])
            liked_post.append(post_no)
            execute_sql(f"UPDATE `UserEat` SET `likecount` = {post_like + 1} WHERE `no` = {post_no}")
            execute_sql(f"UPDATE `user` SET `liked_post` = '{liked_post}' WHERE `ID` = '{authorized[1]}'")

        return True
    
@diaryapi.post("/{post_no}/unlike")
async def like_post(post_no:int, authorized: bool = Depends(verify_token)):
    if authorized:
        user = execute_sql(f"SELECT `liked_post` FROM user WHERE `ID` = '{authorized[1]}'")
        
        if len(user) == 0:
            raise HTTPException(404, "user not found")
        
        liked_post = json.loads(user[0]['liked_post'])

        if post_no in liked_post:
            post_like = int(execute_sql(f"SELECT `likecount` FROM `UserEat` WHERE `no` = {post_no}")[0]['likecount'])
            print(post_like - 1)

            liked_post.remove(post_no)
            execute_sql(f"UPDATE `UserEat` SET `likecount` = {post_like - 1} WHERE `no` = {post_no}")
            execute_sql(f"UPDATE `user` SET `liked_post` = '{liked_post}' WHERE `ID` = '{authorized[1]}'")
        else:
            raise HTTPException(404, "좋아요를 누른 게시글이 아닙니다.")

        return True
    
@diaryapi.post('/{post_id}/share')
async def post_delete(request: Request, post_id:int, authorzed: bool = Depends(verify_token)):
    if authorzed: 
        notes = execute_sql(f"SELECT `no` FROM UserEat WHERE `id` = '{authorzed[1]}' AND (deleted IS NULL OR deleted = 'false')")
        #print(notes)
        note_num = []
        for note in notes:
            note_num.append(int(note['no']))

        #print(note_num)
        veri_list = execute_sql("SELECT `code` FROM f_verify WHERE `type` = 'post_share'")
        keys = []
        for key in veri_list:
            keys.append(key['code'])

        verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])

        while verifykey in keys:
            verifykey = "".join([random.choice(string.ascii_letters) for _ in range(15)])

        if not int(post_id) in note_num:
            raise HTTPException(403, post_not_owner)

        execute_sql(f"INSERT INTO f_verify (`code`, `req_id`, `tar_id`, `group_id`, `type`) VALUES ('{verifykey}','{authorzed[1]}','post_{post_id}',0,'post_share')")

        return f"https://dabom.kro.kr/record_my?id={post_id}&v_key={verifykey}"
    
@diaryapi.post('/{post_id}/check_key')
async def share_key_check(request: Request, post_id: str):
        json = await request.json()
        key = json['verify_key']
        veri_list = execute_sql("SELECT `code` FROM f_verify WHERE `type` = 'post_share'")
        
        keys = []
        for key1 in veri_list:
            keys.append(key1['code'])

        print(keys)
        if key in keys:
            notes = execute_sql(f"SELECT * FROM UserEat WHERE `no` = {post_id} AND (deleted IS NULL OR deleted = 'false')")
            comments = execute_sql(f"SELECT * FROM comments WHERE `post_id` = {post_id} AND `type` = 'main' AND `deleted` = 'false' ORDER BY created_at DESC")

            r_comments = []

            for comment in comments:
                post_id = comment['post_id']
                id = comment['id']
                print(f"SELECT * FROM comments WHERE post_id = {post_id} AND `main_comment` = {id} AND `type` = 'sub' ORDER BY created_at ASC")
                subcomments = execute_sql(f"SELECT * FROM comments WHERE post_id = {post_id} AND `main_comment` = {id} AND `type` = 'sub' ORDER BY created_at ASC")
                comment['sub_comments'] = subcomments
                r_comments.append(html.unescape(comment))


            if len(notes) == 0:
                raise HTTPException(403, "글이 존재 하지 않거나, 해당 글에 접근할 권한이 없습니다.")
            r_note = notes[0]
            r_note['comments'] = r_comments
            return r_note
        else:
            raise HTTPException(403)