import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from firebase_admin import auth
from urllib import parse
from controller.database import execute_sql
from controller.credentials import verify_token, verify_admin_token

import os
import requests
import json
import math

from bs4 import BeautifulSoup

nutrient = APIRouter(prefix="/api/nutrient",tags=["음식 영양소"])

unauthorized = {'code':'ER001','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER002','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER003','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER004','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

invaild_barcode_length = {'code':'ER005','message':'INVAILD BARCODE LENGTH'}

no_data = {'code':'ER017','message':'데이터가 없습니다.'}
sikyak_no_data = {'code':'ER017-S','message':'NO DATA FOUND'}
value_error = {'code':'ER018','message':'입력값이 올바르지 않습니다.'}
#siktak_all_using = {'code':'ER007','message':'ALL CREDENTIALS IS USING'} #식약처 인증키 모두 사용중



def verify_user_token(req: Request):

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
        raise HTTPException(status_code=401, detail=unauthorized)

class calculate(BaseModel):
    pal: float

class get_barcode(BaseModel):
    barcode: str

class get_nutritions(BaseModel):
    name: str

class barcode(BaseModel):
    barcode: str

class test(BaseModel):
    barcode: str

class productDetail(BaseModel):
    Kancode: str

sikyakcredit = [
    '27b7c5d1f7aa43528a46', # 나경원 인증키 1
    '3399d07f7f2e43e5ba47', # 나경원 인증키 2
    'ac2053a9d9eb438fbdc2', # 나경원 인증키 3
    '175adde5fbf24b95b618', # 주운 인증키
    '7e53820846dd445bbfd0', # 연수아 인증키
    ]

#식약청 코드 
#C005 - 바코드 정보 조회
#I2790 - 음식 영양성분 조회
age_error = {"code":"ER019","DETAIL":"나이는 숫자여야합니다."}
gender_error = {"code":"ER020","DETAIL":"성별을 male 이거나 female 이어야합니다."}
month_error = {"code":"ER021","DETAIL":"0세이하 개월수는 0~11 개월 입니다."}


@nutrient.get('/calculate/kcal')
async def calculate_kcal(pal: calculate,authorized: bool = Depends(verify_user_token)):
    pal = pal.pal
    if authorized:
        uid = authorized[1]
        sql = "SELECT height, weight, gender, age FROM user WHERE ID = '%s'" % uid
        user = execute_sql(sql)[0]
        if user['height'] != "" and user['weight'] != "" and (user['gender'] == "male" or user['gender'] == "female"):
            if user['gender'] == "male":
                base = 66.47 + (13.75*float(user['weight'])) + (5*float(user['height'])) - (6.76 * int(user['age']))
                return str(int(float(base) * pal))+" kcal"
            else:
                base = 665.1 + (9.56*(float(user['weight']))) + (1.85 * float(user['height'])) - (4.68 * int(user['age']))
                return str(int(float(base) * pal))+" kcal"
            
        else:
            return "2000 kcal"
        
@nutrient.post('/culcutaete/tandanji')
async def calculate_tandanji(pal: calculate,authorized: bool = Depends(verify_user_token)):
    pal = pal.pal
    if authorized:
        uid = authorized[1]
        sql = "SELECT height, weight, gender, age FROM user WHERE ID = '%s'" % uid
        user = execute_sql(sql)[0]
        if user['height'] != "" and user['weight'] != "" and (user['gender'] == "male" or user['gender'] == "female"):
            if user['gender'] == "male":
                base = 66.47 + (13.75*float(user['weight'])) + (5*float(user['height'])) - (6.76 * int(user['age']))
                move = (float(base) * pal) + base
            else:
                base = 665.1 + (9.56*(float(user['weight']))) + (1.85 * float(user['height'])) - (4.68 * int(user['age']))
                move = (float(base) * pal) + base
            
        else:
            return "2000 kcal"
        
@nutrient.get('/calculate/bmi')
async def calculate_bmi(authorized: bool = Depends(verify_token)):
    if authorized:
        uid = authorized[1]
        sql = "SELECT Nickname, height, weight FROM user WHERE ID = '%s'" % uid
        data = execute_sql(sql)[0]
        if data['height'] == "" or data['weight'] == "":
            raise HTTPException(400, value_error)
        else:
            height = float(data['height']) * 0.01
            bmi = float(data['weight'])/(height*height)

            bmi = math.floor(bmi * 10)/10
            
            print(bmi)

            if bmi >= 30:
                status = "고도비만"
            elif ((bmi >= 25.0) and (bmi < 29.9)):
                status = "비만"
            elif ((bmi >= 23.0) and (bmi < 24.9)):
                status = "과체중"
            elif ((bmi >= 18.5) and (bmi < 22.9)):
                status = "정상"
            elif (bmi < 18.4): #(bmi >= 11.1) and 
                status = "저체중"
            else:
                raise HTTPException(401, value_error)
            
            f_res = {
                "nickname": data['Nickname'],
                "bmi": bmi,
                "status": status
            }

            return f_res
    

@nutrient.get('/categories')
async def get_categories():   
    sql = "SELECT new카테 as 카테고리,  count(new카테) as 개수 FROM food.foodb GROUP BY new카테 ORDER BY new카테"
    res = execute_sql(sql)
    return res

@nutrient.get('/recomm2000')
async def get_recomm2000():
    sql = "SELECT * FROM food.recommeat"
    return execute_sql(sql)

@nutrient.get('/recomm/{age}/{gender}')
async def get_recommand(age, gender):
    def get_recomm(age, gender):
        if "_month" in age:
            if int(age.split("_month")[0]) < 12:
                age = age.split("_month")[0]+" 개월"
            else:
                raise HTTPException(400, month_error)

        else:
            if age.isdecimal():
                age = age+" 세"
            else:
                raise HTTPException(400, age_error)

        sql = 'SELECT * FROM food.'+gender+' WHERE 연령 = \"'+age+'\"'
        return execute_sql(sql)

    if gender == 'male' or gender == 'female':     
        return get_recomm(age, gender)
    else:
        raise(400, gender_error)
        

@nutrient.get('/cus24_barcode/{barcode}')
async def get_cus24_barcode(barcode: str):
    data = {"stdBrcd": barcode}
    res = requests.post('https://www.consumer.go.kr/user/ftc/consumer/goodsinfo/57/selectGoodsInfoDetailThngApi.do', data)
    print(json.loads(res.text))
    return json.loads(res.text)

@nutrient.get('/barcodecroll/{barcode}')
async def get_object_with_barcode(barcode:str):

    #제공된 바코드가 DB에 있는지 확인
    detail = execute_sql("SELECT 식품명, per_gram, 내용량_단위, 유통사, new카테, `에너지(kcal)` FROM foodb WHERE `barcode` = '%s'" % barcode)
    if len(detail) != 0:
        #있으면 데이터 리턴
        return detail[0]
    else:
        s_barcode = barcode
        url = 'http://www.allproductkorea.or.kr/products/info?q=%7B%22mainKeyword%22:%22'+barcode+'%22,%22subKeyword%22:%22%22%7D&page=1&size=10'
        response = requests.get(url)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            div = soup.select_one('div.sub_content')
            datas = div.select('div > div:nth-child(3) > div.spl_list > ul > li')
            barcode = div.select('div > div:nth-child(3) > div.spl_list > ul > li:nth-child(n+1) > a > span.spl_info > p.spl_pt > em')
            f_cate = str(re.sub('<.+?>', '', str(div.select('div > div:nth-child(3) > div.spl_list > ul > li:nth-child(n+1) > a > span.spl_info > p.spl_pm')), 0).strip()).split("&gt")
            f_big_cate = f_cate[0].replace('[','')
            if not "식품" in f_big_cate:
                raise HTTPException(400, "식품이 아니거나 검색결과가 없습니다.")
            f_medium_cate = f_cate[1].replace(';','')
            f_small_cate = f_cate[3].replace(';','').replace(']','')
            title = div.select('div > div:nth-child(3) > div.spl_list > ul > li:nth-child(n+1) > a > span.spl_info > p.spl_pt > strong')
            #print(barcode)
            #print(title)
            resdata = {}
            #print(datas)
            #소비자 24 식품명용
            fd_n_url = "https://www.consumer.go.kr/user/ftc/consumer/goodsinfo/57/selectGoodsInfoDetailThngApi.do"
            fd_n_res = requests.post(fd_n_url, data={"stdBrcd": barcode}).json()
            fd_n_name = fd_n_res['npname']
            fd_c_name = "company"
            
            try: 
                fd_c_name = fd_n_res['munufact']
            except KeyError:
                fd_c_name = fd_n_res['entrpsNm']

            for k in range(len(datas)):
                #print(datas[k]['data-prd-no'])
                #print("k"+str(k))

                url = 'http://www.allproductkorea.or.kr/products/info/korcham/'+datas[k]['data-prd-no']
                response = requests.get(url)
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                div = soup.select_one('div.background')
                datasa = div.select('div > div.popup.pop-warp > div.pop-body > table > tbody > tr:nth-child(n+2) > td')
                div2 = soup.select_one('div.sub_content2')
                rdata = []
                try:
                    bizno = div2.select('div > div.pdv_korchamDetail > div.pdv_wrap_korcham > table > tbody > tr:nth-child(4) > td > div > button')[0]['data-biz-no']
                    r_res = json.loads(requests.get("http://www.allproductkorea.or.kr/platform/nicednb/companies/biz-no/%s/credit-information" % bizno).text)
                    front = "`유통사`"
                    back = "'{0}'".format(r_res['cmpNm'])
                    s_company = r_res['cmpNm']
                except IndexError:
                    s_company = "None"
                    front = "`유통사`"
                    back = "'None'"
                except json.JSONDecodeError:
                    s_company = fd_c_name
                    front = "`유통사`"
                    back = f"'{fd_c_name}'"

                weightstr = str(re.sub(r'[^0-9]', '', str(div2.select('div > div.pdv_korchamDetail > div.pdv_wrap_korcham > table > tbody > tr:nth-child(8) > td')),0).strip())
                if weightstr == '':
                    data = {"stdBrcd": barcode}
                    res = json.loads(requests.post('https://www.consumer.go.kr/user/ftc/consumer/goodsinfo/57/selectGoodsInfoDetailThngApi.do', data).text)
                    weight = int(res['totwtValue'])
                    print(weight)
                else:
                    weight = int(weightstr)
                
                
                
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()] = {}
                for j in range(len(datasa)):
                    data = re.sub('<.+?>', '', str(datasa[j]), 0).strip()
                    rdata.append(data)
                    #print(rdata)      
                    nums = []

                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()] = {}
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'] = {}


                for i in range(int(len(rdata)/3)):
                    resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]] = {}
                    resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]]['내용량'] = rdata[(i*3+2)-1]
                    resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]]['1일 영양성분 기준치에 대한 비율'] = rdata[(i*3+3)-1]
                    #num = [rdata[(i*3+1)-1],rdata[(i*3+2)-1],rdata[(i*3+3)-1]]
                    #print("i"+str(i))
                    #print(rdata[(i*3+1)-1])
                    #print(rdata[(i*3+2)-1])
                    #print(rdata[(i*3+3)-1])
                    #print(int(len(rdata)/3))
                    #print(str(i)+"/"+str(int(len(rdata)/3)))
                    #print(resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()])  

                print(f"t_weight : {weight}")

                title1 = list(resdata.keys())[0]
                print(f"title1 : {title1}")
                kancode = datas[0]['data-prd-no'] 
                glist = []
                if "g" in title1:
                    title1l = title1.split(" ")
                    print("this?")
                    for de in title1l:
                        #print(de)
                        #print(de.find('g'))
                        if de.find('g') != -1:
                            dein = de.find('g')
                            #print(de)
                            if de[dein-2:dein-1].isdecimal():
                                height = re.sub(r'[^0-9]', '', de[:dein])
                                if len(glist) == 0:
                                    glist.append(height)
                                else:
                                    if "(" in de[:dein]:
                                        lcs = title1.find('(')
                                        rcs = title1.find(')')
                                        dea = title1[lcs:rcs]
                                        if "X" in dea or "x" in dea:
                                            if "X" in dea:
                                                amount = re.sub(r'[^0-9]', '', title1.split("X")[1])
                                                glist.append(height)
                                                
                                            if "x" in dea:
                                                amount = re.sub(r'[^0-9]', '', title1.split("x")[1])
                                                glist.append(height)                                            
                                                

                                

                    try:
                        if len(glist) != 1:
                            back = back + ",{0},{1},'{2}'".format(glist[0], glist[1], "g")
                            front = front + ",`총내용량(g)`,`per_gram`,`내용량_단위`"
                        else:
                            back = back + ",{0},{0},'{1}'".format(glist[0],"g")
                            front = front + ",`총내용량(g)`,`per_gram`,`내용량_단위`"
                    except IndexError:
                        front = front + ",`총내용량(g)`,`per_gram`,`내용량_단위`"
                        back = back + ",{0},{0},'{1}'".format(weight,"g")  

                    print("under")                      
                    

                    b_food_num = str(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'food_db'")[0]['no'])
                    n_food_num = int(b_food_num)+1
                    b_num = str(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'custom_food'")[0]['no'])
                    b_num_len = "0"*(6-(len(str(int(b_num)+1))))
                    n_num = "C{0}{1}-ZZ-AVG".format(b_num_len, int(b_num)+1)
                    n_code ="C{0}{1}".format(b_num_len, int(b_num)+1)
                    try:
                        n_index = title1.find(" %sg" % glist[0])
                    except IndexError:
                        n_index = title1.find(" %s g" % weight)
                    #print(" %sg" % glist[0])
                    name = fd_n_name#title1[:n_index]
                    #print(str(re.sub('<.+?>', '', str(title[k]), 0).strip()))
                    #print(name)
                    dlen = len(execute_sql("SELECT 식품명 FROM foodb WHERE 식품명 LIKE \"%{0}%\"".format(name)))
                    bar = len(execute_sql("SELECT barcode FROM foodb WHERE barcode = {0}".format(s_barcode)))
                    #print("dlen"+str(dlen))
                    kcal = "`에너지(kcal)`"
                    tancu = "`탄수화물(g)`"
                    sugar = "`총당류(g)`"
                    danbag = "`단백질(g)`"
                    jibang = "`지방(g)`"
                    pohwajibang = "`총 포화 지방산(g)`"
                    colestrol = "`콜레스테롤(mg)`"
                    nat = "`나트륨(mg)`"
                    trans = "`트랜스 지방산(g)`"
                    #print(height,height_type)
                    #print(f_big_cate, f_small_cate)
                    if f_medium_cate == "라면류":
                        front = front + ",`new카테`"
                        back = back + ",'면류'"
                        cate_n = "면류"
                    
                    elif f_medium_cate == "편의식품":
                        front = front + ",`new카테`"
                        back = back + ",'즉석/편의식품'"
                        cate_n = "즉석/편의식품"

                    elif f_medium_cate == "비스킷" or f_medium_cate == "사탕류":
                        front = front + ",`new카테`"
                        back = back + ",'과자류'"
                        cate_n = "과자류"  

                    elif f_medium_cate == "어육제품류":       
                        front = front + ",`new카테`"
                        back = back + ",'신선식품'"
                        cate_n = "신선식품"

                    else:
                        front = front + ",`new카테`"
                        back = back + f",'{f_medium_cate}'"
                        cate_n = f_medium_cate

                    print(f_medium_cate)           



                    front = front + ",`barcode`,`data_adder`,`SAMPLE_ID`,`NO`,`식품코드`, `DB군`,`식품대분류`,`식품상세분류`, `식품명`"
                    back = back + ",{0},'{1}','{2}',{3},'{4}','{5}','{6}','{7}','{8}'".format(s_barcode, "barcode", n_num, n_food_num, n_code, f_big_cate, f_medium_cate, f_small_cate, fd_n_name) #식품명 과거 str(re.sub('<.+?>', '', str(title[k]), 0).strip())
                    fd_kcal = 0
                    print(f"bar : {bar}")
                    if bar == 0:
                        for nute in list(resdata[title1]['영양소']):
                            if nute == "열량":
                                #kcal
                                data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                num = data[0]
                                type = data[1]
                                if front == "":
                                    front = kcal
                                else:
                                    front = front + ", " + kcal

                                if back == "":
                                    back = num
                                else:
                                    back = back + ", " + num

                                    fd_kcal = num

                            try:
                                if nute == "탄수화물":
                                    #tancu
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]
                                    if front == "":
                                        front = tancu
                                    else:
                                        front = front + ", " + tancu 

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:           
                                if nute == "당류":
                                    #sugar
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]    

                                    if front == "":
                                        front = sugar
                                    else:
                                        front = front + ", " + sugar

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:              
                                if nute == "단백질":
                                    #danbag
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = danbag
                                    else:
                                        front = front + ", " + danbag
                                            
                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:       
                                if nute == "지방":
                                    #jibang
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = jibang
                                    else:
                                        front = front + ", " + jibang

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:
                                if nute == "콜레스테롤":
                                    #colestrol
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    print(data)
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = colestrol
                                    else:
                                        front = front + ", " + colestrol

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:
                                if nute == "나트륨":
                                    #nat
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = nat
                                    else:
                                        front = front + ", " + nat

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:               
                                if nute == "포화지방":
                                    #pohwajibang
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = pohwajibang
                                    else:
                                        front = front + ", " + pohwajibang

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:          
                                if nute == "트랜스지방":
                                    #trans
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = trans
                                    else:
                                        front = front + ", " + trans

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                        sql = "INSERT INTO foodb ({0}) VALUES ({1})".format(front, back)
                        #print(sql)
                        res = execute_sql(sql)
                        execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'custom_food'".format(int(b_num)+1))
                        execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'food_db'".format(n_food_num))
                        #print(res)
                        try:                            
                            if len(glist) != 1:
                                p_res = {
                                    "식품명": name,
                                    "per_gram": glist[1],
                                    "내용량_단위": "g",
                                    "유통사": s_company,
                                    "new카테": cate_n,
                                    "에너지(kcal)": fd_kcal
                                }
                            else:
                                p_res = {
                                    "식품명": name,
                                    "per_gram": glist[0],
                                    "내용량_단위": "g",
                                    "유통사": s_company,
                                    "new카테": cate_n,
                                    "에너지(kcal)": fd_kcal
                                }
                        except IndexError:
                            p_res = {
                                "식품명": name,
                                "per_gram": weight,
                                "내용량_단위": "g",
                                "유통사": s_company,
                                "new카테": cate_n,
                                "에너지(kcal)": fd_kcal
                            }

                        return p_res
                else:
                    try:
                        if len(glist) != 1:
                            back = back + ",{0},{1},'{2}'".format(glist[0], glist[1], "g")
                            front = front + ",`총내용량(g)`,`per_gram`,`내용량_단위`"
                        else:
                            back = back + ",{0},{0},'{1}'".format(glist[0],"g")
                            front = front + ",`총내용량(g)`,`per_gram`,`내용량_단위`"
                    except IndexError:
                        front = front + ",`총내용량(g)`,`per_gram`,`내용량_단위`"
                        back = back + ",{0},{0},'{1}'".format(weight,"g")  

                    print("under")                      
                    

                    b_food_num = str(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'food_db'")[0]['no'])
                    n_food_num = int(b_food_num)+1
                    b_num = str(execute_sql("SELECT `no` FROM food_no WHERE `fetch` = 'custom_food'")[0]['no'])
                    b_num_len = "0"*(6-(len(str(int(b_num)+1))))
                    n_num = "C{0}{1}-ZZ-AVG".format(b_num_len, int(b_num)+1)
                    n_code ="C{0}{1}".format(b_num_len, int(b_num)+1)
                    try:
                        n_index = title1.find(" %sg" % glist[0])
                    except IndexError:
                        n_index = title1.find(" %s g" % weight)
                    #print(" %sg" % glist[0])
                    name = title1[:n_index]
                    #print(str(re.sub('<.+?>', '', str(title[k]), 0).strip()))
                    #print(name)
                    dlen = len(execute_sql("SELECT 식품명 FROM foodb WHERE 식품명 LIKE \"%{0}%\"".format(name)))
                    bar = len(execute_sql("SELECT barcode FROM foodb WHERE barcode = {0}".format(s_barcode)))
                    #print("dlen"+str(dlen))
                    kcal = "`에너지(kcal)`"
                    tancu = "`탄수화물(g)`"
                    sugar = "`총당류(g)`"
                    danbag = "`단백질(g)`"
                    jibang = "`지방(g)`"
                    pohwajibang = "`총 포화 지방산(g)`"
                    colestrol = "`콜레스테롤(mg)`"
                    nat = "`나트륨(mg)`"
                    trans = "`트랜스 지방산(g)`"
                    #print(height,height_type)
                    #print(f_big_cate, f_small_cate)
                    if f_medium_cate == "라면류":
                        front = front + ",`new카테`"
                        back = back + ",'면류'"
                        cate_n = "면류"
                    
                    elif f_medium_cate == "편의식품":
                        front = front + ",`new카테`"
                        back = back + ",'즉석/편의식품'"
                        cate_n = "즉석/편의식품"

                    elif f_medium_cate == "비스킷" or f_medium_cate == "사탕류":
                        front = front + ",`new카테`"
                        back = back + ",'과자류'"
                        cate_n = "과자류"  

                    elif f_medium_cate == "어육제품류":       
                        front = front + ",`new카테`"
                        back = back + ",'신선식품'"
                        cate_n = "신선식품"

                    else:
                        front = front + ",`new카테`"
                        back = back + f",'{f_medium_cate}'"
                        cate_n = f_medium_cate

                    print(f_medium_cate)           



                    front = front + ",`barcode`,`data_adder`,`SAMPLE_ID`,`NO`,`식품코드`, `DB군`,`식품대분류`,`식품상세분류`, `식품명`"
                    back = back + ",{0},'{1}','{2}',{3},'{4}','{5}','{6}','{7}','{8}'".format(s_barcode, "barcode", n_num, n_food_num, n_code, f_big_cate, f_medium_cate, f_small_cate, str(re.sub('<.+?>', '', str(title[k]), 0).strip()))
                    fd_kcal = 0
                    if bar == 0:
                        for nute in list(resdata[title1]['영양소']):
                            if nute == "열량":
                                #kcal
                                data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                num = data[0]
                                type = data[1]
                                if front == "":
                                    front = kcal
                                else:
                                    front = front + ", " + kcal

                                if back == "":
                                    back = num
                                else:
                                    back = back + ", " + num

                                

                                fd_kcal = num


                                

                            try:
                                if nute == "탄수화물":
                                    #tancu
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]
                                    if front == "":
                                        front = tancu
                                    else:
                                        front = front + ", " + tancu 

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:           
                                if nute == "당류":
                                    #sugar
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]    

                                    if front == "":
                                        front = sugar
                                    else:
                                        front = front + ", " + sugar

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:              
                                if nute == "단백질":
                                    #danbag
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = danbag
                                    else:
                                        front = front + ", " + danbag
                                            
                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:       
                                if nute == "지방":
                                    #jibang
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = jibang
                                    else:
                                        front = front + ", " + jibang

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:
                                if nute == "콜레스테롤":
                                    #colestrol
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    print(data)
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = colestrol
                                    else:
                                        front = front + ", " + colestrol

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:
                                if nute == "나트륨":
                                    #nat
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = nat
                                    else:
                                        front = front + ", " + nat

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:               
                                if nute == "포화지방":
                                    #pohwajibang
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = pohwajibang
                                    else:
                                        front = front + ", " + pohwajibang

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")

                            try:          
                                if nute == "트랜스지방":
                                    #trans
                                    data = resdata[title1]['영양소'][nute]['내용량'].split(" ")
                                    num = data[0]
                                    type = data[1]

                                    if front == "":
                                        front = trans
                                    else:
                                        front = front + ", " + trans

                                    if back == "":
                                        back = num
                                    else:
                                        back = back + ", " + num
                            except IndexError:
                                print(nute+" 데이터 불완성 스킵")


                            
                        if (fd_kcal == 0):
                            raise HTTPException(400, "열량 데이터가 없습니다.")
                        sql = "INSERT INTO foodb ({0}) VALUES ({1})".format(front, back)
                        #print(sql)
                        res = execute_sql(sql)
                        execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'custom_food'".format(int(b_num)+1))
                        execute_sql("UPDATE food_no SET no = {0} WHERE `fetch` = 'food_db'".format(n_food_num))
                        #print(res)
                        try:                            
                            if len(glist) != 1:
                                p_res = {
                                    "식품명": name,
                                    "per_gram": glist[1],
                                    "내용량_단위": "g",
                                    "유통사": s_company,
                                    "new카테": cate_n,
                                    "에너지(kcal)": fd_kcal
                                }
                            else:
                                p_res = {
                                    "식품명": name,
                                    "per_gram": glist[0],
                                    "내용량_단위": "g",
                                    "유통사": s_company,
                                    "new카테": cate_n,
                                    "에너지(kcal)": fd_kcal
                                }
                        except IndexError:
                            p_res = {
                                "식품명": name,
                                "per_gram": weight,
                                "내용량_단위": "g",
                                "유통사": s_company,
                                "new카테": cate_n,
                                "에너지(kcal)": fd_kcal
                            }

                        return p_res                                





                

        else : 
            print(response.status_code)

@nutrient.post('/yungyargcroll')
async def test(code: test):
    code = code.barcode
    url = 'http://www.allproductkorea.or.kr/products/info/korcham/101893020'
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.select_one('div.background')
        data = div.select('div > div.popup.pop-warp > div.pop-body > table > tbody > tr:nth-child(n+2) > td')
        print(data)
        #return data

    else : 
        print(response.status_code)

    #body > div.sub_content2 > div > div.pdv_korchamDetail > div.pdv_wrap_korcham > table > tbody > tr:nth-child(1) > td
    #res = json.loads(requests.get(requrl).text)



@nutrient.post('/get_barcode')
async def get_barcode(barcode: get_barcode, authorized: bool = Depends(verify_user_token)):#
    if authorized:
        try:
            code = barcode.barcode
        except AttributeError:
            code = barcode


        if len(code) != 13:
            raise HTTPException(400, invaild_barcode_length)
        else:
            for credit in sikyakcredit:
                requrl = "http://openapi.foodsafetykorea.go.kr/api/"+credit+"/C005/json/1/5/BAR_CD="+code
                res = requests.get(requrl).text
                try:
                    res = json.loads(res)['C005']
                    res = res['row'][0]
                    rejson = {}
                    rejson['제품명'] = res['PRDLST_NM']
                    rejson['식품 유형'] = res['PRDLST_DCNM']
                    rejson['제조사'] = res['BSSH_NM']
                    return rejson
                except json.decoder.JSONDecodeError:
                    error = "error"
                except KeyError:
                    requrl = 'https://retaildb.or.kr/service/product_info/search/'+code
                    res = json.loads(requests.get(requrl).text)
                    rejson = {}
                    rejson['제품명'] = res['baseItems'][0]['value']
                    rejson['식품 유형'] = res["clsTotalNm"].split('>')[2]
                    rejson['제조사'] = res['companies'][0]['name']

                    return rejson
            
            raise HTTPException(500, "all credentials using")

@nutrient.post('/products/detail')
async def product_detail(product:productDetail):
    url = 'http://www.allproductkorea.or.kr/products/info/korcham/'+product.Kancode
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.select_one('div.background')
    datasa = div.select('div > div.popup.pop-warp > div.pop-body > table > tbody > tr:nth-child(n+2) > td')
    
    info = soup.select_one('div.sub_content2')
    barcodes = info.select('div > div.pdv_korchamDetail > div.pdv_wrap_korcham > table > tbody > tr:nth-child(1) > td')[0]
    title = info.select('div > div.pdv_korchamDetail > div.pdv_wrap_korcham > table > tbody > tr:nth-child(3) > td')[0]
    image = info.select('div > div.pdv_korchamDetail > div.pdv_img_box > div.pdv_img > img')[0]['src']
    brand = info.select('div > div.pdv_korchamDetail > div.pdv_wrap_korcham > table > tbody > tr:nth-child(5) > td')[0]
    weight = info.select('div > div.pdv_korchamDetail > div.pdv_wrap_korcham > table > tbody > tr:nth-child(8) > td')[0]
    gusung = info.select('div > div.pdv_korchamDetail > div.pdv_wrap_korcham > table > tbody > tr:nth-child(7) > td')[0]
    rdata = []
    resdata = {}          
    for j in range(len(datasa)):
        data = re.sub('<.+?>', '', str(datasa[j]), 0).strip()
        rdata.append(data)
                    
        resdata[re.sub('<.+?>', '', str(title), 0).strip()] = {}
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['영양소'] = {}
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['Kancode'] = product.Kancode
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['유통바코드'] = re.sub('<.+?>', '', str(barcodes), 0).strip()
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['이미지'] = image
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['브랜드'] = re.sub('<.+?>', '', str(brand), 0).strip()
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['총중량'] = re.sub('<.+?>', '', str(weight), 0).strip()
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['구성정보'] = re.sub('<.+?>', '', str(gusung), 0).strip()

    for i in range(int(len(rdata)/3)):
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['영양소'][rdata[(i*3+1)-1]] = {}
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['영양소'][rdata[(i*3+1)-1]]['내용량'] = rdata[(i*3+2)-1]
        resdata[re.sub('<.+?>', '', str(title), 0).strip()]['영양소'][rdata[(i*3+1)-1]]['1일 영양성분 기준치에 대한 비율'] = rdata[(i*3+3)-1]
                    #num = [rdata[(i*3+1)-1],rdata[(i*3+2)-1],rdata[(i*3+3)-1]]
                    #print("i"+str(i))
                    #print(rdata[(i*3+1)-1])
                    #print(rdata[(i*3+2)-1])
                    #print(rdata[(i*3+3)-1])
                    #print(int(len(rdata)/3))
                    #print(str(i)+"/"+str(int(len(rdata)/3)))
                    #print(resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]) 
    if str(resdata) == "{\'datas\': {}}":
        raise HTTPException(404, no_data)
                
    return resdata

@nutrient.post('/get_nutrition')
async def get_nutrition(object: get_nutritions):#, authorized: bool = Depends(verify_user_token)
    #if authorized:
        name = object.name
        name = name.replace(" ", "_")
        name = parse.quote(name)
        url = 'http://www.allproductkorea.or.kr/products/info?q=%7B%22mainKeyword%22:%22'+name+'%22,%22subKeyword%22:%22%22%7D&page=1&size=1000'
        response = requests.get(url)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            div = soup.select_one('div.sub_content')
            datas = div.select('div > div:nth-child(3) > div.spl_list > ul > li')
            barcode = div.select('div > div:nth-child(3) > div.spl_list > ul > li:nth-child(n+1) > a > span.spl_info > p.spl_pt > em')
            title = div.select('div > div:nth-child(3) > div.spl_list > ul > li:nth-child(n+1) > a > span.spl_info > p.spl_pt > strong')
            #print(barcode)
            #print(title)
            resdata = {}
            resdata = {}
            for k in range(len(datas)-1):
                #print(datas[k]['data-prd-no'])
                #print("k"+str(k))

                url = 'http://www.allproductkorea.or.kr/products/info/korcham/'+datas[k]['data-prd-no']
                response = requests.get(url)
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                div = soup.select_one('div.background')
                datasa = div.select('div > div.popup.pop-warp > div.pop-body > table > tbody > tr:nth-child(n+2) > td')
                rdata = []
                
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()] = {}
                for j in range(len(datasa)):
                    data = re.sub('<.+?>', '', str(datasa[j]), 0).strip()
                    rdata.append(data)
                    #print(rdata)      
                    nums = []
                
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()] = {}
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'] = {}
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['Kan Code'] = datas[k]['data-prd-no']
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['유통바코드'] = re.sub('<.+?>', '', str(barcode[k]), 0).strip()

                for i in range(int(len(rdata)/3)):
                    resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]] = {}
                    resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]]['내용량'] = rdata[(i*3+2)-1]
                    resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]]['1일 영양성분 기준치에 대한 비율'] = rdata[(i*3+3)-1]
                    #num = [rdata[(i*3+1)-1],rdata[(i*3+2)-1],rdata[(i*3+3)-1]]
                    #print("i"+str(i))
                    #print(rdata[(i*3+1)-1])
                    #print(rdata[(i*3+2)-1])
                    #print(rdata[(i*3+3)-1])
                    #print(int(len(rdata)/3))
                    #print(str(i)+"/"+str(int(len(rdata)/3)))
                    #print(resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]) 
            if str(resdata) == "{\'datas\': {}}":
                raise HTTPException(404, no_data)
            
            return resdata

        else : 
            print(response.status_code)

"""
        name = object.name
        name = name.replace(" ", "_")
        
        if name == "하리보_골드베렌":
            name = "하리보_골드베어"

        if name == "자일리톨F" or name == "자일리톨·에프":
            name = "자일리톨껌"

        for credit in sikyakcredit:
            requrl = "http://openapi.foodsafetykorea.go.kr/api/"+credit+"/I2790/json/1/30/DESC_KOR="+name
            res = requests.get(requrl).text
            try:
                res = json.loads(res)['I2790']
                rejson = {}
                rejson['total'] = res['total_count']
                rejson = {}
                
                datas = list(res['row'])
                for data in datas:
                    rjson = {}
                    rjson['제품명'] = data['DESC_KOR']
                    rjson['제조사명'] = data['MAKER_NAME']
                    rjson['내용량'] = data['SERVING_SIZE']
                    rjson['영양소'] = {}
                    rjson['영양소']['열량'] = data['NUTR_CONT1']
                    rjson['영양소']['탄수화물'] = data['NUTR_CONT2']
                    rjson['영양소']['단백질'] = data['NUTR_CONT3']
                    rjson['영양소']['지방'] = data['NUTR_CONT4']
                    rjson['영양소']['당류'] = data['NUTR_CONT5']
                    rjson['영양소']['나트륨'] = data['NUTR_CONT6']
                    rjson['영양소']['콜레스테롤'] = data['NUTR_CONT7']
                    rjson['영양소']['포화지방산'] = data['NUTR_CONT8']
                    rjson['영양소']['트랜스지방'] = data['NUTR_CONT9']

                    rejson[data['NUM']] = rjson

                return rejson

            except json.decoder.JSONDecodeError:
                error = "error"
            except KeyError:
                #raise HTTPException(400, sikyak_no_data)
                requrl = "http://apis.data.go.kr/B553748/CertImgListService/getCertImgListService?ServiceKey=hjhN07O1Z6nHQyKERpgzcxy1qvqv1q3o6wBCt1InDax%2FLIvGUy%2FH44BSLfJM8VI180loMC%2FODqJ9fXMf%2BEpuUA%3D%3D&returnType=json&prdlstNm="+name
                res = json.loads(requests.get(requrl).text)
                if res['header']['resultCode'] != "OK" or len(list(res['body']['items'])) == 0:
                    raise HTTPException(404, sikyak_no_data)
                
                data = list(res['body']['items'])

                return data
"""
                
                
                


@nutrient.post('/barcode_onetouch')
async def barcode_onetouch(barcode:barcode):
    #if authorized:
        try:
            code = barcode.barcode
        except AttributeError:
            code = barcode


        if len(code) != 13:
            raise HTTPException(400, invaild_barcode_length)
        else:
            for credit in sikyakcredit:
                requrl = "http://openapi.foodsafetykorea.go.kr/api/"+credit+"/C005/json/1/5/BAR_CD="+code
                res = requests.get(requrl).text
                try:
                    res = json.loads(res)['C005']
                    resa = res['row'][0]
                    name = resa['PRDLST_NM']
                    name = name.replace(" ", "_")
                    requrl = "http://openapi.foodsafetykorea.go.kr/api/"+credit+"/I2790/json/1/30/DESC_KOR="+name
                    res = requests.get(requrl).text
                    try:
                        res = json.loads(res)['I2790']
                        rejson = {}
                        rejson['total'] = res['total_count']
                        rejson = {}
                        
                        datas = list(res['row'])
                        for data in datas:
                            rjson = {}
                            rjson['제품명'] = data['DESC_KOR']
                            rjson['제조사명'] = data['MAKER_NAME']
                            rjson['내용량'] = data['SERVING_SIZE']
                            rjson['영양소'] = {}
                            rjson['영양소']['열량'] = data['NUTR_CONT1']
                            rjson['영양소']['탄수화물'] = data['NUTR_CONT2']
                            rjson['영양소']['단백질'] = data['NUTR_CONT3']
                            rjson['영양소']['지방'] = data['NUTR_CONT4']
                            rjson['영양소']['당류'] = data['NUTR_CONT5']
                            rjson['영양소']['나트륨'] = data['NUTR_CONT6']
                            rjson['영양소']['콜레스테롤'] = data['NUTR_CONT7']
                            rjson['영양소']['포화지방산'] = data['NUTR_CONT8']
                            rjson['영양소']['트랜스지방'] = data['NUTR_CONT9']

                            rejson[data['NUM']] = rjson

                        return rejson

                    except json.decoder.JSONDecodeError:
                        error = "error"
                    except KeyError:
                        requrl = 'https://retaildb.or.kr/service/product_info/search/'+code
                        res = json.loads(requests.get(requrl).text)
                        rejson = {}
                        rejson['제품명'] = res['baseItems'][0]['value']
                        rejson['식품 유형'] = res["clsTotalNm"].split('>')[2]
                        rejson['제조사'] = res['companies'][0]['name']

                        name = rejson['제품명']
                        name = name.replace(" ", "_")
                        print(name)
                        if "아이스쿨" in name:
                            name = "아이스쿨"

                        requrl = "http://openapi.foodsafetykorea.go.kr/api/"+credit+"/I2790/json/1/30/DESC_KOR="+name
                        res = requests.get(requrl).text
                        try:
                            res = json.loads(res)['I2790']
                            rejson = {}
                            rejson['total'] = res['total_count']
                            rejson = {}
                            
                            datas = list(res['row'])
                            for data in datas:
                                print(data['FOOD_CD'])
                                rjson = {}
                                rjson['제품명'] = data['DESC_KOR']
                                rjson['제조사명'] = data['MAKER_NAME']
                                rjson['내용량'] = data['SERVING_SIZE']
                                rjson['영양소'] = {}
                                rjson['영양소']['열량'] = data['NUTR_CONT1']
                                rjson['영양소']['탄수화물'] = data['NUTR_CONT2']
                                rjson['영양소']['단백질'] = data['NUTR_CONT3']
                                rjson['영양소']['지방'] = data['NUTR_CONT4']
                                rjson['영양소']['당류'] = data['NUTR_CONT5']
                                rjson['영양소']['나트륨'] = data['NUTR_CONT6']
                                rjson['영양소']['콜레스테롤'] = data['NUTR_CONT7']
                                rjson['영양소']['포화지방산'] = data['NUTR_CONT8']
                                rjson['영양소']['트랜스지방'] = data['NUTR_CONT9']

                                rejson[data['NUM']] = rjson

                            return rejson
                        
                        except json.decoder.JSONDecodeError:
                            error = "error"
                        except KeyError:
                            raise HTTPException(404, sikyak_no_data)
                except json.decoder.JSONDecodeError:
                    error = "error"
                except KeyError:
                    requrl = 'https://retaildb.or.kr/service/product_info/search/'+code
                    res = json.loads(requests.get(requrl).text)
                    rejson = {}
                    rejson['제품명'] = res['baseItems'][0]['value']
                    rejson['식품 유형'] = res["clsTotalNm"].split('>')[2]
                    rejson['제조사'] = res['companies'][0]['name']

                    name = rejson['제품명']
                    name = name.replace(" ", "_")
                    print(name)
                    if "아이스쿨" in name:
                        name = "아이스쿨"

                    requrl = "http://openapi.foodsafetykorea.go.kr/api/"+credit+"/I2790/json/1/30/DESC_KOR="+name
                    res = requests.get(requrl).text
                    try:
                        res = json.loads(res)['I2790']
                        rejson = {}
                        rejson['total'] = res['total_count']
                        rejson = {}
                        
                        datas = list(res['row'])
                        for data in datas:
                            rjson = {}
                            rjson['제품명'] = data['DESC_KOR']
                            rjson['제조사명'] = data['MAKER_NAME']
                            rjson['내용량'] = data['SERVING_SIZE']
                            rjson['영양소'] = {}
                            rjson['영양소']['열량'] = data['NUTR_CONT1']
                            rjson['영양소']['탄수화물'] = data['NUTR_CONT2']
                            rjson['영양소']['단백질'] = data['NUTR_CONT3']
                            rjson['영양소']['지방'] = data['NUTR_CONT4']
                            rjson['영양소']['당류'] = data['NUTR_CONT5']
                            rjson['영양소']['나트륨'] = data['NUTR_CONT6']
                            rjson['영양소']['콜레스테롤'] = data['NUTR_CONT7']
                            rjson['영양소']['포화지방산'] = data['NUTR_CONT8']
                            rjson['영양소']['트랜스지방'] = data['NUTR_CONT9']

                            rejson[data['NUM']] = rjson

                        return rejson
                    
                    except json.decoder.JSONDecodeError:
                        error = "error"
                    except KeyError:
                        return rejson
            raise HTTPException(500, "all credentials using")    
