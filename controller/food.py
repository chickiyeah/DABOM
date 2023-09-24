import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from firebase_admin import auth
from urllib import parse
from controller.database import execute_sql
from controller.credentials import verify_token

import os
import requests
import json
import math

foodapi = APIRouter(prefix="/api/food", tags=['food'])

User_NotFound = {"code":"ER011", "message":"USER_NOT_FOUND"}    

unauthorized = {'code':'ER013','message':'UNAUTHORIZED (Authorzation Header Not Found)'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}
er101 = {'code':'ER101', 'message':'엑세스토큰이 올바르지 않습니다.'}

class search_input(BaseModel):
    keywords: str

class add_food(BaseModel):
    name: str
    category: str
    kcal: int
    barcode: int

@foodapi.post("/add")
async def food_add(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        f_data = await request.json()
        name = f_data['name']
        cate = f_data['category']
        kcal = f_data['kcal']
        barcode = f_data['barcode']
        weight = f_data['weight']
        print()
        bar = 1
        if barcode == 0:
            b_num = str(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'custom_food'")[0]['no'])
            b_num_len = "0"*(6-(len(str(int(b_num)+1))))
            n_num = "C{0}{1}-ZZ-AVG".format(b_num_len, int(b_num)+1)
            n_code ="C{0}{1}".format(b_num_len, int(b_num)+1)
            b_food_num = str(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'food_db'")[0]['no'])
            n_food_num = int(b_food_num)+1
            pname = execute_sql("SELECT Nickname FROM user WHERE ID = '{0}'".format(authorized[1]))[0]['Nickname']
            execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'custom_food'".format(int(b_num)+1))
            execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'food_db'".format(n_food_num))
            execute_sql("INSERT INTO foodb (NO, SAMPLE_ID, `에너지(kcal)`, new카테, 식품명, data_adder, 식품코드, `내용량_단위`, `총내용량(g)`, `1회제공량`) VALUES ({0},'{1}','{2}','{3}', '{4}','{5}','{6}','{7}',{8},{9})".format(n_food_num, n_num, kcal, cate, name, pname, n_code, "g", weight, weight))

            return n_num
        else:
            bar = len(execute_sql("SELECT barcode FROM foodb WHERE barcode = {0}".format(barcode)))
        
        if bar == 0:
            b_num = str(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'custom_food'")[0]['no'])
            b_num_len = "0"*(6-(len(str(int(b_num)+1))))
            n_num = "C{0}{1}-ZZ-AVG".format(b_num_len, int(b_num)+1)
            n_code ="C{0}{1}".format(b_num_len, int(b_num)+1)
            b_food_num = str(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'food_db'")[0]['no'])
            n_food_num = int(b_food_num)+1
            pname = execute_sql("SELECT Nickname FROM user WHERE ID = '{0}'".format(authorized[1]))[0]['Nickname']
            execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'custom_food'".format(int(b_num)+1))
            execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'food_db'".format(n_food_num))
            execute_sql("INSERT INTO foodb (NO, SAMPLE_ID, `에너지(kcal)`, new카테, 식품명, data_adder, 식품코드, barcode, `내용량_단위`, `총내용량(g)`, `1회제공량`) VALUES ({0},'{1}','{2}','{3}', '{4}','{5}','{6}',{7},'{8}',{9},{10})".format(n_food_num, n_num, kcal, cate, name, pname, n_code, barcode, "g", weight, weight))

            return n_num
        else:
            raise HTTPException(400, "해당 바코드는 이미 사용중입니다.")
        

er044 = {"code":"ER044","message":"키워드가 입력되지 않았습니다."}

@foodapi.post("/search/and")
async def food_search(request: Request ,authorized: bool = Depends(verify_token)):
    if authorized:
        data = await request.json()
        cate = data["category"]
        i_keywords = data["keywords"]
        #list면 keywords = json.loads(input.keywords)
        if input == "":
            raise HTTPException(400, er044)
        else:
            # , 으로 구분된 STR이면
            keywords = i_keywords.split(',')
            search = "SELECT SAMPLE_ID, 식품명, `에너지(kcal)` as 칼로리 FROM foodb WHERE "
            for keyword in keywords: 
                if keyword != "":
                    if keyword[:1] != "":
                        search = search + "{0} LIKE \"%{1}%\" OR ".format("식품명", keyword)
                    else:
                        search = search + "{0} LIKE \"%{1}%\" OR ".format("식품명", keyword[1:])

            res = execute_sql(search[0:-4]+f" AND `new카테` = '{cate}'")
            return res
    
@foodapi.post("/search/or")
async def food_search(input:search_input ,authorized: bool = Depends(verify_token)):
    if authorized:
        #list면 keywords = json.loads(input.keywords)
        if input == "":
            raise HTTPException(400, er044)
        else:
            # , 으로 구분된 STR이면
            keywords = input.keywords.split(',')
            search = "SELECT SAMPLE_ID, 식품명, `에너지(kcal)` as 칼로리 FROM foodb WHERE "
            for keyword in keywords:
                if keyword != "":
                    if keyword[:1] != "":
                        search = search + "{0} LIKE \"%{1}%\" OR ".format("식품명", keyword)
                    else:
                        search = search + "{0} LIKE \"%{1}%\" OR ".format("식품명", keyword[1:])

            res = execute_sql(search[0:-4])
            return res
    
@foodapi.get("/detail/{sample_id}")
async def food_datail(sample_id:str):
        detail = execute_sql("SELECT 식품명, 1회제공량, 내용량_단위, 유통사, new카테, `에너지(kcal)` FROM foodb WHERE SAMPLE_ID = '%s'" % sample_id)
        if len(detail) == 0:
            raise HTTPException(400, "Could not find food with this sample id.")
        
        detail = detail[0]
        gram = str(detail['1회제공량']) + " " + detail['내용량_단위']
        res = {
            "SAMPLE_ID": sample_id,
            "name": detail['식품명'],
            "category" : detail['new카테'],
            "company" : detail['유통사'],
            "kcal" : detail['에너지(kcal)']
        }    
        return res