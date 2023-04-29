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

from bs4 import BeautifulSoup

nutrient = APIRouter(prefix="/api/nutrient",tags=["음식 영양소"])

unauthorized = {'code':'ER001','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER002','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER003','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER004','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

invaild_barcode_length = {'code':'ER005','message':'INVAILD BARCODE LENGTH'}

no_data = {'code':'ER006','message':'NO DATA FOUND'}
sikyak_no_data = {'code':'ER006-S','message':'NO DATA FOUND'}
siktak_all_using = {'code':'ER007','message':'ALL CREDENTIALS IS USING'} #식약처 인증키 모두 사용중



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
age_error = {"CODE":"ER001","DETAIL":"AGE MUST BE INTEGER"}
gender_error = {"CODE":"ER002","DETAIL":"GENDER MUST BE male OR female"}
month_error = {"CODE":"ER003","DETAIL":"MONTH RANGE MUST BE FROM 0 TO 11"}


@nutrient.get('/calculate/kcal')
async def calculate_kcal(pal: calculate,authorized: bool = Depends(verify_user_token)):
    pal = pal.pal
    if authorized:
        uid = authorized[1]
        sql = "SELECT height, weight, gender, age FROM user WHERE ID = '%s'" % uid
        user = execute_sql(sql)[0]
        if user['height'] != "" and user['weight'] != "" and (user['gender'] == "male" or user['gender'] == "female"):
            if user['gender'] == "male":
                base = ((10*int(user['weight'])+6.25*int(user['height'])-5*int(user['age']))+5)
                base1 = 66.47 + 13.75*float(user['weight']) + 5*float(user['height']) - 6.76 * int(user['age'])
                return str(int(float(base) * pal))+" kcal"
            else:
                base = ((10*int(user['weight'])+6.25*int(user['height'])-5*int(user['age']))-161)
                base1 = 665.1 + 9.56*(float(user['weight'])) + 1.85 * float(user['height']) - 4.68 * int(user['age'])
                return str(int(float(base) * pal))+" kcal"
            
        else:
            return "2000 kcal"
        
@nutrient.get('/calculate/bmi')
async def calculate_bmi(authorized: bool = Depends(verify_user_token)):
    if authorized:
        uid = authorized[1]
        sql = "SELECT Nickname, height, weight FROM user WHERE ID = '%s'" % uid
        data = execute_sql(sql)[0]
        if data['height'] == "" or data['weight'] == "":
            raise HTTPException(400, "Invalid Data")
        else:
            height = float(data['height']) * 0.01
            bmi = float(data['weight'])/(height*height)

            bmi = math.floor(bmi * 10)/10
            
            if bmi > 25.0:
                status = "비만"
            elif ((bmi > 23.0) and (bmi < 24.9)):
                status = "과체중"
            elif ((bmi > 18.5) and (bmi < 22.9)):
                status = "정상"
            elif bmi <= 18.5:
                status = "저체중"
            else:
                raise HTTPException(401, "Invalid Value")

            return "{2} 님의 BMI는 {0} 이고, {1} 입니다.".format(bmi, status, data['Nickname'])
    

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
        


@nutrient.get('/barcodecroll/{barcode}')
async def teset(barcode:str):
    url = 'http://www.allproductkorea.or.kr/products/info?q=%7B%22mainKeyword%22:%22'+barcode+'%22,%22subKeyword%22:%22%22%7D&page=1&size=10'
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.select_one('div.sub_content')
        datas = div.select('div > div:nth-child(3) > div.spl_list > ul > li')
        barcode = div.select('div > div:nth-child(3) > div.spl_list > ul > li:nth-child(n+1) > a > span.spl_info > p.spl_pt > em')
        title = div.select('div > div:nth-child(3) > div.spl_list > ul > li:nth-child(n+1) > a > span.spl_info > p.spl_pt > strong')
        print(barcode)
        print(title)
        resdata = {}
        resdata = {}
        print(datas)
        for k in range(len(datas)):
            print(datas[k]['data-prd-no'])
            print("k"+str(k))

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
                print(rdata)      
                nums = []
            
            resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()] = {}
            resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'] = {}

            for i in range(int(len(rdata)/3)):
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]] = {}
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]]['내용량'] = rdata[(i*3+2)-1]
                resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()]['영양소'][rdata[(i*3+1)-1]]['1일 영양성분 기준치에 대한 비율'] = rdata[(i*3+3)-1]
                #num = [rdata[(i*3+1)-1],rdata[(i*3+2)-1],rdata[(i*3+3)-1]]
                print("i"+str(i))
                print(rdata[(i*3+1)-1])
                print(rdata[(i*3+2)-1])
                print(rdata[(i*3+3)-1])
                print(int(len(rdata)/3))
                print(str(i)+"/"+str(int(len(rdata)/3)))
                print(resdata[re.sub('<.+?>', '', str(title[k]), 0).strip()])  

            return resdata

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
            
            raise HTTPException(500, siktak_all_using)

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
            raise HTTPException(500, siktak_all_using)    
