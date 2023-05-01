import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from firebase_admin import auth
from urllib import parse
from controller.database import execute_sql

import os
import requests
import json
import math

foodapi = APIRouter(prefix="/api/food", tags=['food'])

User_NotFound = {"code":"ER011", "message":"USER_NOT_FOUND"}    

unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

class search_input(BaseModel):
    keywords: str

class add_food(BaseModel):
    name: str
    category: str
    kcal: int

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

@foodapi.post("/add")
async def food_add(data: add_food, authorized: bool = Depends(verify_token)):
    if authorized:
        name = data.name
        cate = data.category
        kcal = data.kcal
        b_num = str(execute_sql("SELECT id FROM custom_food")[0]['id'])
        b_num_len = "0"*(6-(len(str(int(b_num)+1))))
        n_num = "C{0}{1}-ZZ-AVG".format(b_num_len, int(b_num)+1)
        n_code ="C{0}{1}".format(b_num_len, int(b_num)+1)
        pname = execute_sql("SELECT Nickname FROM user WHERE ID = '{0}'".format(authorized[1]))[0]['Nickname']
        execute_sql("UPDATE custom_food SET id = {0} WHERE `fetch` = 'chi'".format(int(b_num)+1))
        execute_sql("INSERT INTO foodb (SAMPLE_ID, `에너지(kcal)`, new카테, 식품명, data_adder, 식품코드) VALUES ('{0}','{1}','{2}','{3}', '{4}','{5}')".format(n_num, kcal, cate, name, pname, n_code))

        return "food added"
        


@foodapi.post("/search/and")
async def food_search(input:search_input ,authorized: bool = Depends(verify_token)):
    if authorized:
        #list면 keywords = json.loads(input.keywords)

        # , 으로 구분된 STR이면
        keywords = input.keywords.split(',')
        search = "SELECT SAMPLE_ID, 식품명, 유통사 FROM foodb WHERE "
        for keyword in keywords:
            if keyword != "":
                text = keyword.split("=")
                search = search + "{0} LIKE \"%{1}%\" AND ".format(text[0], text[1])

        res = execute_sql(search[0:-4])
        return res
    
@foodapi.post("/search/or")
async def food_search(input:search_input ,authorized: bool = Depends(verify_token)):
    if authorized:
        #list면 keywords = json.loads(input.keywords)

        # , 으로 구분된 STR이면
        keywords = input.keywords.split(',')
        search = "SELECT SAMPLE_ID, 식품명, 유통사 FROM foodb WHERE "
        for keyword in keywords:
            if keyword != "":
                text = keyword.split("=")
                search = search + "{0} LIKE \"%{1}%\" OR ".format(text[0], text[1])

        res = execute_sql(search[0:-4])
        return res
    
@foodapi.get("/detail/{sample_id}")
async def food_datail(sample_id:str, authorized: bool = Depends(verify_token)):
    if authorized:
        detail = execute_sql("SELECT 식품명, 1회제공량, 내용량_단위, 유통사, new카테, `에너지(kcal)` FROM foodb WHERE SAMPLE_ID = '%s'" % sample_id)
        if len(detail) == 0:
            raise HTTPException(400, "Could not find food with this sample id.")
        
        detail = detail[0]
        gram = str(detail['1회제공량']) + " " + detail['내용량_단위']
        res = {
            "SAMPLE_ID": sample_id,
            "식품명": detail['식품명'],
            "카테고리" : detail['new카테'],
            "유통사" : detail['유통사'],
            "칼로리 (%s)" % gram : detail['에너지(kcal)']
        }    
        return res