from collections import Counter
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Response, Cookie
from starlette.responses import RedirectResponse
from pydantic import BaseModel
import os
from pymysql import IntegrityError
import requests
import datetime
import re
import smtplib
from email.message import EmailMessage
from controller.database import execute_sql
import platform
import os
import time
import sys
import ctypes
from email import utils

from firebase_admin import exceptions

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from controller.credentials import verify_token, verify_admin_token

s = smtplib.SMTP("smtp.gmail.com", 587)
s.ehlo()
s.starttls()
s.login("noreply.dabom", "sxhmurnajtenjtbr")

try:   
    import firebase_admin
    from firebase_admin import auth
    from firebase_admin import credentials
    from firebase_admin import storage
    from firebase_admin import _auth_utils
    from firebase import Firebase

    firebaseConfig = {
        "apiKey": "AIzaSyC58Oh7Lyb7EoB0FWZQ-qMqfqLtiTJIIFw",
        "authDomain": "dabom-ca6fe.firebaseapp.com",
        "projectId": "dabom-ca6fe",
        "storageBucket": "dabom-ca6fe.appspot.com",
        "messagingSenderId": "607249280151",
        "appId": "1:607249280151:web:abcff56e0b43b1abb00dd2",
        "databaseURL":"https://dabom-ca6fe-default-rtdb.firebaseio.com/"
    }

        #파이어베이스 서비스 세팅
    cred = credentials.Certificate('./cert/serviceAccountKey.json')
    default_app = firebase_admin.initialize_app(cred,{"databaseURL":"https://deli-english-web-default-rtdb.firebaseio.com"})

    Auth = Firebase(firebaseConfig).auth()
    Storage = Firebase(firebaseConfig).storage()
except ModuleNotFoundError:

    os.system('pip install firebase')
    os.system('pip install sseclient')
    os.system('pip install firebase_admin')
    os.system('pip install gcloud')
    os.system('pip install python_jwt')
    os.system('pip install requests_toolbelt')


    import firebase_admin
    from firebase_admin import auth
    from firebase_admin import credentials
    from firebase_admin import storage
    from firebase import Firebase




    firebaseConfig = {
        "apiKey": "AIzaSyC58Oh7Lyb7EoB0FWZQ-qMqfqLtiTJIIFw",
        "authDomain": "dabom-ca6fe.firebaseapp.com",
        "projectId": "dabom-ca6fe",
        "storageBucket": "dabom-ca6fe.appspot.com",
        "messagingSenderId": "607249280151",
        "appId": "1:607249280151:web:abcff56e0b43b1abb00dd2",
        "databaseURL":"https://dabom-ca6fe-default-rtdb.firebaseio.com/"
    }

        #파이어베이스 서비스 세팅
    cred = credentials.Certificate('./cert/serviceAccountKey.json')
    #default_app = firebase_admin.initialize_app(cred,{"databaseURL":"https://deli-english-web-default-rtdb.firebaseio.com"})

    Auth = Firebase(firebaseConfig).auth()
    Storage = Firebase(firebaseConfig).storage()

userapi = APIRouter(prefix="/api/user", tags=["user"])

"응답 정의 구역"
Missing_Email = {"code":"ER003", "message":"MISSING EMAIL"}
Missing_Password = {"code":"ER004", "message":"MISSING PASSWORD"}
Password_is_Too_Short = {"code":"ER005", "message":"PASSWORD IS TOO SHORT"}
Too_Many_Duplicate_Characters = {"code":"ER006", "message":"TOO MANY DUPLICATE CHARACTERS"}
Missing_Nickname = {"code":"ER007", "message":"MISSING NICKNAME"}

Invaild_Email = {"code":"ER008", "message":"INVAILD_EMAIL"}
Invaild_Password = {"code":"ER009", "message":"INVAILD_PASSWORD"}
Email_Exists = {"code":"ER010", "message":"EMAIL_EXISTS"}

User_NotFound = {"code":"ER011", "message":"USER_NOT_FOUND"}

Email_Not_Verified = {"code":"ER012", "message":"EMAIL_NOT_VERIFIED"}

unauthorized = {'code':'ER013','message':'UNAUTHORIZED (Authorzation Header Not Found)'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

Nickname_cantuse = {'code':'ER017','message':'Nickname Cant Contain "removed"'}

email_provider_error = {'code':'ER018','message':'Unable to sign up using this email provider'}

login_ip_diffrent = {'code':'ER019','message':'Unable to renew the access token. The IP is different.'}

gender_choose_error = {'code':'ER020', 'message':'Gender Must be male or female or private.'}
age_type_error = {'code':'ER021', 'message':'Age must be Integer'}
height_type_error = {'code':'ER022', 'message':'Height must be Integer'}
weight_type_error = {'code':'ER023', 'message':'Weight must be Integer'}

birthday_error = {'code':'ER024', 'message':'Birthday must be contain two /'}

Token_Revoke = {"code":"ER999", "message":"TOKEN REVOKED"}
Invalid_Token = {"code":"ER998", "message":"INVALID TOKEN"}
User_Disabled = {"code":"ER997", "message":"USER DISABLED"}

login_responses = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "examples": {
                    "Missing password": {
                        "summary": "비밀번호가 입력되지 않았습니다.",
                        "value": {"detail":Missing_Password}
                    },
                    "Missing email": {  
                        "summary": "이메일이 입력되지 않았습니다.",
                        "value": {"detail":Missing_Email}
                    },
                    "invaild email": {
                        "summary": "아이디의 입력값이 이메일이 아니거나, 이메일이 유효하지 않습니다.",
                        "value": {"detail":Invaild_Email}
                    },
                    "invaild password": {
                        "summary": "비밀번호가 일치하지 않습니다.",
                        "value": {"detail":Invaild_Password}
                    },
                    "User Disabled": {
                        "summary": "사용자가 비활성화 되었습니다.",
                        "value": {"detail":User_Disabled}
                    },
                    "Email Not Verified": {
                        "summary": "이메일 인증이 완료되지 않았습니다.",
                        "value": {"detail":Email_Not_Verified}
                    }
                }
            }
        }
    }
}

register_responses = {
    201: {
        "description": "가입 성공",
        "content": {
            "application/json": {
                "examples": {
                    "Success": { 
                        "summary": "회원가입 성공",
                        "value": {"detail": "User Register Successfully"}
                    }
                }
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "examples": {
                    "Missing email": {  
                        "summary": "이메일이 입력되지 않았습니다.",
                        "value": {"detail":Missing_Email}
                    },
                    "Missing password": {
                        "summary": "비밀번호가 입력되지 않았습니다.",
                        "value": {"detail":Missing_Password}
                    },
                    "invaild email": {
                        "summary": "아이디의 입력값이 이메일이 아니거나, 이메일이 유효하지 않습니다.",
                        "value": {"detail":Invaild_Email}
                    },
                    "Password is Too Short": {
                        "summary": "비밀번호가 너무 짧습니다. 비밀번호는 6자 이상이어야 합니다.",
                        "value": {"detail":Password_is_Too_Short}
                    },
                    "Too Many Duplicate Characters": {
                        "summary": "비밀번호에 연속적으로 중복된 문자가 너무 많습니다. (최대 중복 4글자)",
                        "value": {"detail":Too_Many_Duplicate_Characters}
                    },
                    "Missing nickname": {
                        "summary": "닉네임이 입력되지 않았습니다.",
                        "value": {"detail":Missing_Nickname}
                    },
                    "EMail Exists": {
                        "summary": "이미 가입되어있는 이메일입니다.",
                        "value": {"detail":Email_Exists}
                    }
                }
            }
        }
    }
}

token_verify_responses = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "examples": {
                    "Token Revoked": {
                        "summary": "토근이 취소되었습니다. (재 로그인 필요)",
                        "value": {"detail":Token_Revoke}
                    },
                    "Invaild Token": {  
                        "summary": "토큰이 유효하지 않습니다.",
                        "value": {"detail":Invalid_Token}
                    },
                    "User Disabled": {  
                        "summary": "해당 유저는 비활성화 되어있습니다.",
                        "value": {"detail":User_Disabled}
                    }
                }
            }
        }
    }
}

token_revoke_responses = {
    200: {
        "description": "Token Revoked",
        "content": {
            "application/json": {
                "examples": {
                    "Added Successfully": {
                        "summary": "Revoke Successfully",
                        "value": {                                                        
                            "detail": "Tokens revoked at: timestamp"
                        }
                    }
                }
            }
        }
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "examples": {
                    "User Not Found": {
                        "summary": "해당 유저는 존재하지 않습니다.",
                        "value": {"detail":User_NotFound}
                    },
                    "Invalid Token": {
                        "summary": "토큰이 유효하지 않 습니다.",
                        "value": {"detail":Invalid_Token}
                    }
                }
            }
        }
    }
}

class UserLogindata(BaseModel):
    email: str
    password: str
    g_cap: str

class UserRegisterdata(BaseModel):
    email: str
    password: str
    nickname: str
    gender: str
    birthday: str
    height: Optional[str]
    weight: Optional[str]
    profile_image: Optional[str] = "../assets/images/default-profile.png"

class LoginResponse(BaseModel):
    ID: str
    Nickname: str
    email: str
    access_token: str
    refresh_token: str
    expires_in: int
    Created_At: str

class RegisterResponse(BaseModel):
    detail: str

class verify_token_res(BaseModel):
    uid: str
    email: str
    nick: str

class token_revoke(BaseModel):
    uid: str

class token_revoke_res(BaseModel):
    detail: str

class UserResetPWdata(BaseModel):
    email: str

class EmailVerify(BaseModel):
    email: str

class EmailSend(BaseModel):
    title: str
    content: str
    email: str

class UserLogoutdata(BaseModel):
    access_token: str

class UserFindiddata(BaseModel):
    nickname: str

class refresh_token(BaseModel):
    refresh_token: str

class setinfomsg(BaseModel):
    msg: str


@userapi.post('/setinfomsg')
async def setinfomesg(data:setinfomsg ,authorized: bool = Depends(verify_token)):
    if authorized:
        msg = data.msg
        sql = "UPDATE infomsg SET message = %s WHERE ID = %s"
        res = execute_sql(sql, (msg, authorized[1]))
        if res == 0:
            sql = "INSERT INTO infomsg VALUES (%s, %s)"
            try:
                res = execute_sql(sql,(authorized[1], msg))
                return "data created"
            except IntegrityError as e:
                if e.args[0] == 1062:
                    return "same data"
        else:
            return "data updated"

@userapi.post('/edit_profile')
async def edit_user_profile(request: Request, authorized: bool = Depends(verify_token), userId: Optional[str] = Cookie(None)):
    if authorized:
        h_data = await request.json()
        print(h_data)
        g_capt = h_data['g_captcha']
        g_cap = {
            'secret': '6Lft9g8oAAAAAANE3oNaTKLgyCK6ksG4kfpGhg4Q',
            'response' : g_capt
        }
        res = requests.post('https://www.google.com/recaptcha/api/siteverify', data=g_cap)
        g_cap_res = res.json()
        if g_cap_res['success'] == False:
            raise HTTPException(403, "캡차 인증에 실패했습니다.")
        
        print(g_cap_res)
        execute_sql("UPDATE `user` SET `Nickname` = %s, `gender` = %s, `birthday` = %s, `height` = %s, `weight` = %s, `profile_image` = %s WHERE `ID` = %s", (h_data['Nickname'], h_data['gender'], h_data['birthday'], h_data['height'], h_data['weight'], h_data['profile_image'], userId))
        execute_sql("UPDATE `infomsg` SET `message` = %s WHERE `ID` = %s", (h_data['imsg'], userId))

        return True

@userapi.get('/cookie/me')
async def reading(userId: Optional[str] = Cookie(None)): 
    user = execute_sql("SELECT * FROM `user` WHERE `ID` = %s", (userId))
        
    imsg = execute_sql("SELECT * FROM infomsg WHERE `ID` = %s", (userId))
    user[0]['imsg'] = imsg[0]['message']
        
    return user[0]

@userapi.get('/email/user_id')
async def email(email:str):
    res = auth.get_user_by_email(email).uid
    return res

@userapi.get('/logout')
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="userId")
    
    return True

@userapi.get('/cookie/autologin')
async def f_verify_token(response: Response, access_token: str, refresh_token:str):
    try:
        """if platform.system() == "Linux":
            os.system("sudo ntpdate time.google.com")

        if platform.system() == "Windows":
            def is_admin():
                try:
                    return ctypes.windll.shell32.IsUserAnAdmin()
                except:
                    return False

            if is_admin():
                # 관리자 권한으로 실행 중일 때 수행할 작업
                os.system("w32tm /resync")
                pass
            else:
                # 현재 프로그램 인스턴스를 관리자 권한으로 다시 실행
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)"""

        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        user = auth.verify_id_token(access_token, check_revoked=True)
        print(user)
        # Token is valid and not revoked.
        return True, user['email_verified'], user
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        raise HTTPException(status_code=401, detail=unauthorized_revoked)
    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        raise HTTPException(status_code=401, detail=unauthorized_userdisabled)
    except auth.InvalidIdTokenError:
        # Token is invalid
        if refresh_token == None:
            return RedirectResponse(url= "/login")

        try:
            if platform.system() == "Linux":
                os.system("sudo ntpdate time.google.com")

            if platform.system() == "Windows":
                def is_admin():
                    try:
                        return ctypes.windll.shell32.IsUserAnAdmin()
                    except:
                        return False

                if is_admin():
                    # 관리자 권한으로 실행 중일 때 수행할 작업
                    os.system("w32tm /resync")
                    pass
                else:
                    # 현재 프로그램 인스턴스를 관리자 권한으로 다시 실행
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

            currentuser = Auth.refresh(refresh_token)

            response.set_cookie(key="access_token", value=currentuser['idToken'], httponly=True)
            response.set_cookie(key="refresh_token", value=currentuser['refreshToken'], httponly=True)
            response.set_cookie(key="userId", value=currentuser['userId'], httponly=True)
            user = auth.verify_id_token(currentuser['idToken'], check_revoked=True)

            return True, user['email_verified'], user
        except requests.HTTPError as e:
            error = json.loads(e.args[1])['error']['message']
            print("Auto_Login_Error "+error)
            if error == "TOKEN_EXPIRED":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            if error == "INVALID_REFRESH_TOKEN":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            if error == "USER_NOT_FOUND":
                raise HTTPException(status_code=401, detail=User_NotFound)
            
            print("Auto_Login_Error "+error)
        
    except auth.UserNotFoundError:
        return HTTPException(status_code=401, detail=User_NotFound)
    except KeyError:
        raise HTTPException(status_code=400, detail=unauthorized)
    except ValueError:
        raise HTTPException(status_code=422)

@userapi.get('/cookie/verify')
async def f_verify_token(response: Response, access_token: Optional[str] = Cookie(None), refresh_token: Optional[str] = Cookie(None)):
    if (access_token == None or refresh_token == None):
        raise HTTPException(401,unauthorized_invaild)
    
    try:
        """if platform.system() == "Linux":
            os.system("sudo ntpdate time.google.com")

        if platform.system() == "Windows":
            def is_admin():
                try:
                    return ctypes.windll.shell32.IsUserAnAdmin()
                except:
                    return False

            if is_admin():
                # 관리자 권한으로 실행 중일 때 수행할 작업
                os.system("w32tm /resync")
                pass
            else:
                # 현재 프로그램 인스턴스를 관리자 권한으로 다시 실행
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)"""
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        user = auth.verify_id_token(access_token, check_revoked=True)
        print(user)
        # Token is valid and not revoked.
        return True, user['email_verified'], user
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        raise HTTPException(status_code=401, detail=unauthorized_revoked)
    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        raise HTTPException(status_code=401, detail=unauthorized_userdisabled)
    except auth.InvalidIdTokenError:
        # Token is invalid
        if refresh_token == None:
            return RedirectResponse(url= "/login")

        try:
            if platform.system() == "Linux":
                os.system("sudo ntpdate time.google.com")

            if platform.system() == "Windows":
                def is_admin():
                    try:
                        return ctypes.windll.shell32.IsUserAnAdmin()
                    except:
                        return False

                if is_admin():
                    # 관리자 권한으로 실행 중일 때 수행할 작업
                    os.system("w32tm /resync")
                    pass
                else:
                    # 현재 프로그램 인스턴스를 관리자 권한으로 다시 실행
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            
            currentuser = Auth.refresh(refresh_token)

            response.set_cookie(key="access_token", value=currentuser['idToken'], httponly=True)
            response.set_cookie(key="refresh_token", value=currentuser['refreshToken'], httponly=True)
            response.set_cookie(key="userId", value=currentuser['userId'], httponly=True)
            user = auth.verify_id_token(currentuser['idToken'], check_revoked=True)
            return True, user['email_verified'], user
        except requests.HTTPError as e:
            error = json.loads(e.args[1])['error']['message']
            if error == "TOKEN_EXPIRED":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            if error == "INVALID_REFRESH_TOKEN":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            print("Verify_Error "+error)
        
    except auth.UserNotFoundError:
        raise HTTPException(status_code=401, detail=User_NotFound)
    except KeyError:
        raise HTTPException(status_code=400, detail=unauthorized)
    except ValueError:
       raise HTTPException(422)
    
@userapi.get('/cookie/get_info')
async def f_verify_token(response: Response, access_token: Optional[str] = Cookie(None), refresh_token: Optional[str] = Cookie(None)):
    try:
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        currentuser = auth.verify_id_token(access_token, check_revoked=True)
        #print(currentuser)
        # Token is valid and not revoked.
        user = execute_sql("SELECT `Nickname`, `profile_image`, `ID` FROM `user` WHERE `ID` = %s", (currentuser['user_id']))

        return user
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        raise HTTPException(status_code=401, detail=unauthorized_revoked)
    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        raise HTTPException(status_code=401, detail=unauthorized_userdisabled)
    except auth.InvalidIdTokenError:
        # Token is invalid
        if refresh_token == None:
            return RedirectResponse(url= "/login")

        try:
            if platform.system() == "Linux":
                os.system("sudo ntpdate time.google.com")

            if platform.system() == "Windows":
                def is_admin():
                    try:
                        return ctypes.windll.shell32.IsUserAnAdmin()
                    except:
                        return False

                if is_admin():
                    # 관리자 권한으로 실행 중일 때 수행할 작업
                    os.system("w32tm /resync")
                    pass
                else:
                # 현재 프로그램 인스턴스를 관리자 권한으로 다시 실행
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

            currentuser = Auth.refresh(refresh_token)

            response.set_cookie(key="access_token", value=currentuser['idToken'], httponly=True)
            response.set_cookie(key="refresh_token", value=currentuser['refreshToken'], httponly=True)
            response.set_cookie(key="userId", value=currentuser['userId'], httponly=True)
            user = execute_sql("SELECT `Nickname`, `profile_image`, `ID` FROM `user` WHERE `ID` = %s", (currentuser['userId']))

            return user
        except requests.HTTPError as e:
            error = json.loads(e.args[1])['error']['message']
            if error == "TOKEN_EXPIRED":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            if error == "INVALID_REFRESH_TOKEN":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            print("Verify_Error "+error)
        
    except auth.UserNotFoundError:
        raise HTTPException(status_code=401, detail=User_NotFound)
    except KeyError:
        raise HTTPException(status_code=400, detail=unauthorized)
    except ValueError:
        raise HTTPException(status_code=422)

@userapi.get("/get_user")
async def get_user(id:str, authorized:bool = Depends(verify_admin_token)):
    if authorized:
        user = execute_sql("SELECT `Nickname`, `profile_image`, `ID` FROM `user` WHERE `ID` = %s", (id))
        
        imsg = execute_sql("SELECT * FROM infomsg WHERE `ID` = %s", (id))
        user[0]['imsg'] = imsg[0]['message']
        
        return user

@userapi.get("/get_users")
async def get_users(id:str, authorized:bool = Depends(verify_admin_token)):
    if authorized:
        back = ""
        id = json.loads(id)
        print(id)
        for u in id:
            if ";" or "--" not in u:
                if back == "":
                    back = "`ID` = '"+ u + "'"
                else:
                    back = back + " OR `ID` = '"+ u + "'"
        f_users = []

        users = execute_sql("SELECT `Nickname`, `profile_image` FROM `user` WHERE %s", (back))

        return users 
    
@userapi.post("/revoke_token", response_model=token_revoke_res, responses=token_revoke_responses)
async def revoke_token(token: token_revoke):
    try:
        uid = token.access_token
    except AttributeError as e:
        uid = token

    try:
        auth.revoke_refresh_tokens(uid)
        user = auth.get_user(uid)
        revocation = user.tokens_valid_after_timestamp / 1000
        return {"detail": 'Tokens revoked at: {0}'.format(revocation)}
    except _auth_utils.InvalidIdTokenError:
        raise HTTPException(status_code=400, detail=Invalid_Token)
    except _auth_utils.UserNotFoundError:
        raise HTTPException(status_code=400, detail=User_NotFound)

@userapi.post('/unregister')
async def user_delete(authorized:bool = Depends(verify_token)):
    if authorized:
        user = authorized[2]
        id = user['user_id']
        email = user['firebase']['identities']['email'][0]
        sql = 'SELECT Nickname FROM user WHERE ID = %s'
        res = execute_sql(sql, (id))
        if len(res) == 0:
            raise HTTPException(400, User_NotFound)

        nickname = res[0]
        print(nickname)

        user_data = {
            "id": id,
        }

        sql = "UPDATE user SET ID = %s, email = %s, Nickname = %s WHERE ID = %s AND email = %s", ("removed-"+id, "removed-"+email, "removed-"+nickname['Nickname'], id, email)
        res = execute_sql(sql)

        print(sql)

        if res > 0: 
            auth.delete_user(id)
            return {"detail":"User deleted successfully"}
        
er040 = {"code":"ER040", "message":"너무 많은 시도가 있었습니다. 나중에 시도해주세요."}

@userapi.post('/login', responses=login_responses)
async def user_login(userdata: UserLogindata, request: Request, response: Response):
    email = userdata.email
    password = userdata.password
    g_capt = userdata.g_cap
    g_cap = {
            'secret': '6Lft9g8oAAAAAANE3oNaTKLgyCK6ksG4kfpGhg4Q',
            'response' : g_capt
        }
    res = requests.post('https://www.google.com/recaptcha/api/siteverify', data=g_cap)
    g_cap_res = res.json()
    if g_cap_res['success'] == False:
        raise HTTPException(403, "캡차 인증에 실패했습니다.")

    if(len(email) == 0):
        raise HTTPException(status_code=400, detail=Missing_Email)

    if(len(password) == 0):
        raise HTTPException(status_code=400, detail=Missing_Password)

    try:
        Auth.sign_in_with_email_and_password(email, password)
    except requests.exceptions.HTTPError as erra:
        #HTTP 에러가 발생한 경우
        #오류 가져오기 json.loads(str(erra).split("]")[1].split('"errors": [\n')[1])['message']
        res = json.loads(str(erra).split("]")[1].split('"errors": [\n')[1])['message']
        res = res.split(" : ")[0]

        if "INVALID_EMAIL" in res:
            raise HTTPException(status_code=400, detail=Invaild_Email)

        if "INVALID_PASSWORD" in res:
            raise HTTPException(status_code=400, detail=Invaild_Password)

        if "USER_DISABLED" in res:
            raise HTTPException(status_code=400, detail=User_Disabled)
        
        if "TOO_MANY_ATTEMPTS_TRY_LATER" in res:
            raise HTTPException(status_code=400, detail=er040)

    currentuser = Auth.current_user
    try:
        userjson= execute_sql("SELECT * FROM user WHERE ID = %s", currentuser['localId'])[0]
    except TypeError:
        raise HTTPException(400, Invaild_Email)
    except IndexError:
        raise HTTPException(400, Invaild_Email)
    
    userjson['access_token'] = currentuser['idToken']
    userjson['refresh_token'] = currentuser['refreshToken']
    userjson['expires_in'] = currentuser['expiresIn']

    verify = auth.get_user(currentuser['localId'])
    print(verify.email_verified)
    if verify.email_verified == False:
        try:
            res = auth.generate_email_verification_link(email, action_code_settings=None, app=None)
        except exceptions.InvalidArgumentError as exception:
            raise HTTPException(status_code=400, detail=er040)
        
        message = res.replace("lang=en", "lang=ko")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[다봄] 이메일을 인증하세요'
        msg['From'] = utils.formataddr(("다봄","noreply.dabom@gmail.com"))
        msg['To'] = email

        text = "이메일 인증"
        html = """\
        <html>
        <head></head>
        <body>
            <div>
                <xlink href="//fonts.googleapis.com/css?family=Google+Sans" rel="stylesheet" type="text/css"
                    <tr align="center" height="32" style="height: 32px;">
                        <td>
                            <table border="0" cellspacing="0" cellpadding="0"
                            style="padding-bottom: 20px; max-width: 516px; min-width: 220px; margin-left:auto; margin-right:auto; margin-top:6rem">
                                <tbody>
                                <tr>
                                <td>
                                    <div align="center" style="border-style: solid; border-width: thin; border-color:#dadce0; border-radius: 8px; padding: 40px 20px;">
                                        <img src='https://firebasestorage.googleapis.com/v0/b/dabom-ca6fe.appspot.com/o/dabomlogo.png?alt=media&token=8b895151-37d3-4bbe-ae65-efdd6adb6ff7' width="74" height="54" style="margin-bottom: 16px;" loading="lazy"/>
                                        <div style="font-family: 'Google Sans',Roboto,RobotoDraft,Helvetica,Arial,sans-serif;border-bottom: thin solid #dadce0; color: rgba(0,0,0,0.87); line-height: 32px; padding-bottom: 24px;text-align: center; word-break: break-word;><div style="font-size: 24px;">
                                            <a style="text-decoration: none; color: rgba(0,0,0,0.87);" rel="noreferrer noopener"target="_blank"></a> 계정 이메일 인증
                                        </div>
                                            <div style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 14px; color: rgba(0,0,0,0.87); line-height: 20px;padding-top: 20px; text-align: center;">    
                                                <p> 이메일 미인증 상태의 아이디의 로그인이 감지되어 이메일 인증 링크가 전송되었습니다.</p>
                                                <p> 아래 링크를 클릭하여 이메일 인증을 완료 하실수 있습니다. </p>
                                                <br>
                                                <a href='{0}'> 이메일 인증하기 </a>
                                                <br>
                                                <br>
                                                <strong>만약 본인이 요청하지 않은거라면 이 메일을 무시하세요.</strong>
                                                <br>
                                                <br>
                                                <p>※ 본 메일은 발신 전용 메일이며,</p>
                                                <p>자세한 문의사항은 다봄 <a href="https://dabom.channel.io/home"><strong>고객센터</strong></a>를 이용해 주시기 바랍니다.</p>
                                            </div>
                                        </div>
                                    </div>
                                </td></tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </div>
        </body>
        </html>
        """.format(message)
        
                        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        try:
            s.sendmail("noreply.dabom@gmail.com", email, msg.as_string())
        except smtplib.SMTPServerDisconnected:
            d = smtplib.SMTP("smtp.gmail.com", 587)
            d.ehlo()
            d.starttls()
            d.login("noreply.dabom", "sxhmurnajtenjtbr")
            d.sendmail("noreply.dabom@gmail.com", email, msg.as_string())
        except smtplib.SMTPSenderRefused: #sender refused to send message
            d = smtplib.SMTP("smtp.gmail.com", 587)
            d.ehlo()
            d.starttls()
            d.login("noreply.dabom", "sxhmurnajtenjtbr")
            d.sendmail("noreply.dabom@gmail.com", email, msg.as_string())     

        #msg.set_content("아래 링크를 클릭해서 이메일을 인증하세요.\n"+message)
        #s.sendmail(msg)
        raise HTTPException(status_code=400, detail=Email_Not_Verified)

    
    id = userjson['ID']
    login_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = request.client.host
    execute_sql("INSERT INTO loginlog VALUES (%s, %s, %s, %s)", (id, login_at, ip, userjson['Nickname']))
    response.set_cookie(key="access_token", value=currentuser['idToken'], httponly=True)
    response.set_cookie(key="refresh_token", value=currentuser['refreshToken'], httponly=True)
    response.set_cookie(key="userId", value=currentuser['localId'], httponly=True)
    return userjson

er039 = {"code": "ER039", "message": "생일이 올바르지 않습니다."}

@userapi.post("/register", response_model=RegisterResponse, responses=register_responses, status_code=201)
async def user_create(userdata: UserRegisterdata):
    now = datetime.datetime.now()
    email = userdata.email
    password = userdata.password
    nickname = userdata.nickname
    gender = userdata.gender
    birthday = userdata.birthday
    height = userdata.height
    weight = userdata.weight
    image = userdata.profile_image
    #이메일이 공란이면
    if(len(email) == 0):
        raise HTTPException(status_code=400, detail=Missing_Email)

    #비번이 공란이면
    if(len(password) == 0):
        raise HTTPException(status_code=400, detail=Missing_Password)
    else:
        #비번이 6자리 이하이면
        if(len(password) <= 6):
            raise HTTPException(status_code=400, detail=Password_is_Too_Short)
        else:
            #비번에 4글자이상 중복되는 글자가 있으면
            if(re.search('(([a-zA-Z0-9])\\2{3,})', password)):
                raise HTTPException(status_code=400, detail=Too_Many_Duplicate_Characters)

    if gender != "male" and gender != "female" and gender != "private":
        raise HTTPException(400, gender_choose_error)
    
    if birthday.count("/") != 2:
        raise HTTPException(400, birthday_error)
    
    s_birthday = birthday.split("/")

    try:
        t_birthday = datetime.datetime(int(s_birthday[0]), int(s_birthday[1]), int(s_birthday[2]))
    except SyntaxError:
        raise HTTPException(400, er039)

    #닉네임이 공란이면
    if(len(nickname) == 0):
        raise HTTPException(status_code=400, detail=Missing_Nickname)
    
    if 'removed' in nickname:
        raise HTTPException(status_code=400, detail=Nickname_cantuse)
    
    if 'kakao' in email:
        raise HTTPException(status_code=400, detail=email_provider_error)

    try:
        #파이어베이스의 유저만드는거 사용
        a = Auth.create_user_with_email_and_password(email, password)
    except requests.exceptions.HTTPError as erra:
        #HTTP 에러가 발생한 경우
        #오류 가져오기 json.loads(str(erra).split("]")[1].split('"errors": [\n')[1])['message']
        res = json.loads(str(erra).split("]")[1].split('"errors": [\n')[1])['message']
        res = res.split(" : ")[0]
        if "INVALID_EMAIL" in res:
            raise HTTPException(status_code=400, detail=Invaild_Email)
        
        if "INVALID_PASSWORD" in res:
            raise HTTPException(status_code=400, detail=Invaild_Password)

        if "USER_DISABLED" in res:
            raise HTTPException(status_code=400, detail=User_Disabled)

        if "EMAIL_EXISTS" in res:
            raise HTTPException(status_code=400, detail=Email_Exists)
    
    age = int(datetime.datetime.now().strftime("%Y")) - int(birthday.split("/")[0])
    
    if not height.isdecimal() and not height == "":
        raise HTTPException(400, height_type_error)

    if not weight.isdecimal() and not weight == "":
        raise HTTPException(400, weight_type_error)
    

    if "/assets/images/default-profile.png" in image :
        image = "../assets/images/default-profile.png"
    
    


    #유저의 고유 아이디 (UniqueID)
    id = a['localId']

    res = auth.generate_email_verification_link(email, action_code_settings=None, app=None)
    message = res.replace("lang=en", "lang=ko")
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '[다봄] 계정 이메일 인증'
    msg['From'] = utils.formataddr(("다봄","noreply.dabom@gmail.com"))
    msg['To'] = email
    #message
    #msg.set_content("안녕하세요 다봄 입니다.\n\n해당 이메일로 다봄 사이트에 가입되어 이메일 인증이 필요합니다.\n아래 링크를 클릭해서 이메일 인증을 완료할 수 있습니다.\n\n"+message+"\n\n만약 본인이 가입하지 않은거라면 이 메일을 무시하세요.\n\n\n※ 본 메일은 발신 전용 메일이며, 자세한 문의사항은 다봄 고객센터를 이용해 주시기 바랍니다.")
    
    text = "회원가입"
    html = """\
<html>
  <head></head>
  <body>
    <div>
        <xlink href="//fonts.googleapis.com/css?family=Google+Sans" rel="stylesheet" type="text/css"
            <tr align="center" height="32" style="height: 32px;">
                <td>
                    <table border="0" cellspacing="0" cellpadding="0"
                    style="padding-bottom: 20px; max-width: 516px; min-width: 220px; margin-left:auto; margin-right:auto; margin-top:6rem">
                        <tbody>
                        <tr>
                        <td>
                            <div align="center" style="border-style: solid; border-width: thin; border-color:#dadce0; border-radius: 8px; padding: 40px 20px;">
                                <img src='https://firebasestorage.googleapis.com/v0/b/dabom-ca6fe.appspot.com/o/dabomlogo.png?alt=media&token=8b895151-37d3-4bbe-ae65-efdd6adb6ff7' width="74" height="54" style="margin-bottom: 16px;" loading="lazy"/>
                                <div style="font-family: 'Google Sans',Roboto,RobotoDraft,Helvetica,Arial,sans-serif;border-bottom: thin solid #dadce0; color: rgba(0,0,0,0.87); line-height: 32px; padding-bottom: 24px;text-align: center; word-break: break-word;><div style="font-size: 24px;">
                                    <a style="text-decoration: none; color: rgba(0,0,0,0.87);" rel="noreferrer noopener"target="_blank">누군가가</a> 해당 이메일을 사용하여 사이트에 가입했습니다.
                                </div>
                                    <div style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 14px; color: rgba(0,0,0,0.87); line-height: 20px;padding-top: 20px; text-align: center;">    
                                        <p>해당 이메일로 다봄 사이트에 가입이 되어 이메일 인증이 필요합니다.</p>
                                        <p> 아래 링크를 클릭하여 이메일 인증을 완료할 수 있습니다. </p>
                                        <a href='{0}'> 이메일 인증 완료하기 </a>
                                        <br/>
                                        <strong>만약 본인이 가입하지 않은거라면 이 메일을 무시하세요.</strong>
                                        <br/>                                        
                                        <p>※ 본 메일은 발신 전용 메일이며,</p>
                                        <p>자세한 문의사항은 다봄 <a href="https://dabom.channel.io/home"><strong>고객센터</strong></a>를 이용해 주시기 바랍니다.</p>
                                    </div>
                                </div>
                            </div>
                        </td></tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </div>
  </body>
</html>
""".format(message)
            # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    try:
        s.sendmail("noreply.dabom@gmail.com", email, msg.as_string())
    except smtplib.SMTPServerDisconnected:
        d = smtplib.SMTP("smtp.gmail.com", 587)
        d.ehlo()
        d.starttls()
        d.login("noreply.dabom", "sxhmurnajtenjtbr")
        d.sendmail("noreply.dabom@gmail.com", email, msg.as_string())
    except smtplib.SMTPSenderRefused: #sender refused to send message
        d = smtplib.SMTP("smtp.gmail.com", 587)
        d.ehlo()
        d.starttls()
        d.login("noreply.dabom", "sxhmurnajtenjtbr")
        d.sendmail("noreply.dabom@gmail.com", email, msg.as_string())       

    execute_sql("INSERT INTO infomsg (ID, message) VALUES (%s,'없음')", (id))
    sql = "INSERT INTO user VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, \"[]\", '[]', 'False',  '[]', %s, %s, '[]')"
    res = execute_sql(sql, (email, id, nickname, str(now.strftime("%Y-%m-%d %H:%M:%S")), gender, str(age), height, weight, str(t_birthday.strftime("%Y-%m-%d")), image))
    if res != 1:
        raise HTTPException(500, "ERROR ON CREATE DATA FOR NEW USER")
    
    return {"detail":"USER ADD SUCCESS"}

@userapi.post('/logout')
async def user_logout(userdata: UserLogoutdata):
    auth = await verify_token(userdata.access_token)
    if auth:
        print(auth)
        res = await revoke_token(list(auth)[1])
        return {"detail":"User Logout Successfully"}
    else:
        raise HTTPException(status_code=401, detail=unauthorized)

@userapi.post("/findid")
async def user_findid(birthday: str):
    
    if birthday.count("/") != 2:
        raise HTTPException(400, er039)
    
    s_birthday = birthday.split("/")

    try:
        t_birthday = datetime.datetime(int(s_birthday[0]), int(s_birthday[1]), int(s_birthday[2]))
    except SyntaxError:
        raise HTTPException(400, er039)

    sql = "SELECT * FROM user WHERE birthday = %s"
    users = execute_sql(sql, (str(t_birthday.strftime("%Y-%m-%d"))))

    resemails = {}
    resemails["data"] = []
    for email in users:
        originmail = email['email'].split("@")
        ldiff = originmail[0][0:round(len(originmail[0])/2)] +""+ str("*"*(len(originmail[0])-round(len(originmail[0])/2)))
        rdiff = originmail[1][0:round(len(originmail[0])/2)] +""+ str("*"*(len(originmail[1])-round(len(originmail[0])/2)))
        resemails["data"].append({"email":ldiff+"@"+rdiff})

    resemails["amount"] = len(resemails["data"])
    
    return resemails



@userapi.post("/resetpw")
async def user_reset_password(userdata: UserResetPWdata):
    email = userdata.email
    try:
        auth.get_user_by_email(email)
    except _auth_utils.UserNotFoundError:
        raise HTTPException(status_code=400, detail=User_NotFound)
    except ValueError:
        raise HTTPException(status_code=400, detail=Invaild_Email)
    
    rstlink = auth.generate_password_reset_link(email, action_code_settings=None, app=None)
    rstlink = rstlink.replace("lang=en", "lang=ko")

    rst = MIMEMultipart('alternative')
    rst['Subject'] = '[다봄] 계정 비밀번호 변경'
    rst['From'] = utils.formataddr(("다봄","noreply.dabom@gmail.com"))
    rst['To'] = email
    #rst.set_content("안녕하세요 다봄 입니다.\n\n회원님께서는 다봄 계정의 비밀번호 변경을 요청하셨습니다.\n링크를 누르면 새로운 비밀번호를 설정하실 수 있습니다.\n\n"+rstlink+"\n\n회원님이 요청하신 것이 아니라면 이 메일을 무시하세요.\n\n\n※ 본 메일은 발신 전용 메일이며, 자세한 문의사항은 다봄 고객센터를 이용해 주시기 바랍니다.")
    
    text = "비번초기화"
    html = """\
<html>
  <head></head>
  <body>
    <div>
        <xlink href="//fonts.googleapis.com/css?family=Google+Sans" rel="stylesheet" type="text/css"
            <tr align="center" height="32" style="height: 32px;">
                <td>
                    <table border="0" cellspacing="0" cellpadding="0"
                    style="padding-bottom: 20px; max-width: 516px; min-width: 220px; margin-left:auto; margin-right:auto; margin-top:6rem">
                        <tbody>
                        <tr>
                        <td>
                            <div align="center" style="border-style: solid; border-width: thin; border-color:#dadce0; border-radius: 8px; padding: 40px 20px;">
                                <img src='https://firebasestorage.googleapis.com/v0/b/dabom-ca6fe.appspot.com/o/dabomlogo.png?alt=media&token=8b895151-37d3-4bbe-ae65-efdd6adb6ff7' width="74" height="54" style="margin-bottom: 16px;" loading="lazy"/>
                                <div style="font-family: 'Google Sans',Roboto,RobotoDraft,Helvetica,Arial,sans-serif;border-bottom: thin solid #dadce0; color: rgba(0,0,0,0.87); line-height: 32px; padding-bottom: 24px;text-align: center; word-break: break-word;><div style="font-size: 24px;">
                                    <a style="text-decoration: none; color: rgba(0,0,0,0.87);" rel="noreferrer noopener"target="_blank"></a> 계정 비밀번호 초기화
                                </div>
                                    <div style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 14px; color: rgba(0,0,0,0.87); line-height: 20px;padding-top: 20px; text-align: center;">    
                                        <p> 비밀번호 초기화 요청이 접수되어 비밀번호 초기화 링크를 보내드립니다.</p>
                                        <p> 아래 링크를 클릭하여 비밀번호를 새로 설정하실 수 있습니다. </p>
                                        <br>
                                        <a href='{0}'> 비밀번호 재설정하기 </a>
                                        <br>
                                        <br>
                                        <strong>만약 본인이 요청하지 않은거라면 이 메일을 무시하세요.</strong>
                                        <br>
                                        <br>
                                        <p>회원님의 비밀번호는 암호화되어 저장되어 기존 비밀번호를 복구해 드릴수 없습니다.</p>
                                        <br>  
                                        <br>
                                        <br>
                                        <p>※ 본 메일은 발신 전용 메일이며,</p>
                                        <p>자세한 문의사항은 다봄 <a href="https://dabom.channel.io/home"><strong>고객센터</strong></a>를 이용해 주시기 바랍니다.</p>
                                    </div>
                                </div>
                            </div>
                        </td></tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </div>
  </body>
</html>
""".format(rstlink)
    
            # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
    rst.attach(part1)
    rst.attach(part2)

    try:
        s.sendmail("noreply.dabom@gmail.com", email, rst.as_string())
    except smtplib.SMTPServerDisconnected: # when server disconnect
        d = smtplib.SMTP("smtp.gmail.com", 587)
        d.ehlo()
        d.starttls()
        d.login("noreply.dabom", "sxhmurnajtenjtbr")
        d.sendmail("noreply.dabom@gmail.com", email, rst.as_string())
    except smtplib.SMTPSenderRefused: #sender refused to send message
        d = smtplib.SMTP("smtp.gmail.com", 587)
        d.ehlo()
        d.starttls()
        d.login("noreply.dabom", "sxhmurnajtenjtbr")
        d.sendmail("noreply.dabom@gmail.com", email, rst.as_string())

    return "password reset link sent"

@userapi.post("/verify_email")
async def user_verify(userdata: EmailVerify):
        email = userdata.email
        try:
            auth.get_user_by_email(email)
        except _auth_utils.UserNotFoundError:
            raise HTTPException(status_code=400, detail=User_NotFound)
        except ValueError:
            raise HTTPException(status_code=400, detail=Invaild_Email)
        
        vlink = auth.generate_email_verification_link(email, action_code_settings=None, app=None)

        ver = MIMEMultipart('alternative')
        ver['Subject'] = '[다봄] 계정 이메일 인증'
        ver['From'] = utils.formataddr(("다봄","noreply.dabom@gmail.com"))
        ver['To'] = email
        #ver.set_content("안녕하세요 다봄 입니다.\n\n해당 이메일로 다봄 사이트에 이메일 인증이 요청되었습니다.\n아래 링크를 클릭해서 이메일 인증을 완료할 수 있습니다.\n\n"+vlink+"\n\n만약 본인이 가입하지 않은거라면 이 메일을 무시하세요.\n\n\n※ 본 메일은 발신 전용 메일이며, 자세한 문의사항은 다봄 고객센터를 이용해 주시기 바랍니다.")

        text = "이메일 인증"
        html = """\
<html>
  <head></head>
  <body>
    <div>
        <xlink href="//fonts.googleapis.com/css?family=Google+Sans" rel="stylesheet" type="text/css"
            <tr align="center" height="32" style="height: 32px;">
                <td>
                    <table border="0" cellspacing="0" cellpadding="0"
                    style="padding-bottom: 20px; max-width: 516px; min-width: 220px; margin-left:auto; margin-right:auto; margin-top:6rem">
                        <tbody>
                        <tr>
                        <td>
                            <div align="center" style="border-style: solid; border-width: thin; border-color:#dadce0; border-radius: 8px; padding: 40px 20px;">
                                <img src='https://firebasestorage.googleapis.com/v0/b/dabom-ca6fe.appspot.com/o/dabomlogo.png?alt=media&token=8b895151-37d3-4bbe-ae65-efdd6adb6ff7' width="74" height="54" style="margin-bottom: 16px;" loading="lazy"/>
                                <div style="font-family: 'Google Sans',Roboto,RobotoDraft,Helvetica,Arial,sans-serif;border-bottom: thin solid #dadce0; color: rgba(0,0,0,0.87); line-height: 32px; padding-bottom: 24px;text-align: center; word-break: break-word;><div style="font-size: 24px;">
                                    <a style="text-decoration: none; color: rgba(0,0,0,0.87);" rel="noreferrer noopener"target="_blank"></a> 계정 이메일 인증
                                </div>
                                    <div style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 14px; color: rgba(0,0,0,0.87); line-height: 20px;padding-top: 20px; text-align: center;">    
                                        <p> 이메일 인증 요청이 접수되어 이메일 인증 링크를 보내드립니다.</p>
                                        <p> 아래 링크를 클릭하여 이메일 인증을 완료 하실수 있습니다. </p>
                                        <br>
                                        <a href='{0}'> 이메일 인증하기 </a>
                                        <br>
                                        <br>
                                        <strong>만약 본인이 요청하지 않은거라면 이 메일을 무시하세요.</strong>
                                        <br>  
                                        <br>
                                        <br>
                                        <p>※ 본 메일은 발신 전용 메일이며,</p>
                                        <p>자세한 문의사항은 다봄 <a href="https://dabom.channel.io/home"><strong>고객센터</strong></a>를 이용해 주시기 바랍니다.</p>
                                    </div>
                                </div>
                            </div>
                        </td></tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </div>
  </body>
</html>
""".format(vlink)

            # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
        ver.attach(part1)
        ver.attach(part2)

        try:
            s.sendmail("noreply.dabom@gmail.com", email, ver.as_string())
        except smtplib.SMTPServerDisconnected:
            d = smtplib.SMTP("smtp.gmail.com", 587)
            d.ehlo()
            d.starttls()
            d.login("noreply.dabom", "sxhmurnajtenjtbr")
            d.sendmail("noreply.dabom@gmail.com", email, ver.as_string())
        except smtplib.SMTPSenderRefused: #sender refused to send message
            d = smtplib.SMTP("smtp.gmail.com", 587)
            d.ehlo()
            d.starttls()
            d.login("noreply.dabom", "sxhmurnajtenjtbr")
            d.sendmail("noreply.dabom@gmail.com", email, ver.as_string())         
        
        return {"detail":"Email Verification Link Sent"}

@userapi.post("/send_email")
async def admin_send_email(userdata: EmailSend, authorized: bool = Depends(verify_admin_token)):
    if authorized:
        email = userdata.email
        try:
            auth.get_user_by_email(email)
        except _auth_utils.UserNotFoundError:
            raise HTTPException(status_code=400, detail=User_NotFound)
        except ValueError:
            raise HTTPException(status_code=400, detail=Invaild_Email)
        
        message = EmailMessage()
        message['Subject'] = '[다봄] '+userdata.title
        message['From'] = utils.formataddr(("다봄","noreply.dabom@gmail.com"))
        message['To'] = email
        message.set_content(userdata.content+"\n\n\n※ 본 메일은 발신 전용 메일이며, 자세한 문의사항은 다봄 <a href='https://dabom.channel.io/home'><strong>고객센터</strong></a>를 이용해 주시기 바랍니다.")

        try:
            s.sendmail(message)
        except smtplib.SMTPServerDisconnected:
            d = smtplib.SMTP("smtp.gmail.com", 587)
            d.ehlo()
            d.starttls()
            d.login("noreply.dabom", "sxhmurnajtenjtbr")
            d.sendmail(message)
            return {"detail":"Email Sent"}
        except smtplib.SMTPSenderRefused: #sender refused to send message
            d = smtplib.SMTP("smtp.gmail.com", 587)
            d.ehlo()
            d.starttls()
            d.login("noreply.dabom", "sxhmurnajtenjtbr")
            d.sendmail(message) 
            return {"detail":"Email Sent"}
        
        return {"detail":"Email Sent"}
    else:
        raise HTTPException(status_code=401, detail=unauthorized)

@userapi.get('/eat_avg/{to_day}')
async def get_eat_avg(to_day:str, authorized: bool = Depends(verify_token)):
    if authorized:
        now = str((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))

        sql = "SELECT `foods`,`total_kcal` FROM `UserEat` WHERE `id` = %s AND `created_at` BETWEEN date(%s) AND date(%s) AND (deleted IS NULL OR deleted = 'false')"

        res = execute_sql(sql, (authorized[1], to_day, now))
        
        to_kcal = 0
        
        foods_l = []
        print(res)
        for data in res:
            foods = data["foods"].replace("[","").replace("]", "").split("}, ")
            for food in foods:
                
                if "}" not in food:
                    food = food + "}"

                
                
                food = food.replace("\'", "\"")
                print(food)
                food = json.loads(food)
                food_name = execute_sql("SELECT 식품명 FROM foodb WHERE SAMPLE_ID = %s", (food['code']))[0]['식품명']
                foods_l.append(food_name)

            to_kcal = to_kcal + int(data['total_kcal'])

        c_foods_l = sorted(Counter(foods_l).items(), key=lambda x: (-x[1], x[0]))

        p = execute_sql("SELECT `gender`, `age` FROM `user` WHERE `ID` = %s", (authorized[1]))[0]

        p_gender = p['gender']
        p_age = p['age']

        base_kcal = execute_sql("SELECT `kcal` FROM "+p_gender+" WHERE `연령` = %s", (str(p_age)+" 세"))
        
        if (len(base_kcal) != 0):
            base_kcal = base_kcal[0]['kcal']
        else:
            base_kcal = 0


        f_res = {
            "sort_foods": c_foods_l,
            "total_kcal": to_kcal,
            "p_gender": p_gender,
            "base_kcal": base_kcal
        }

        
        return f_res



    """@userapi.post("/verify_token", response_model=verify_token_res, responses=token_verify_responses)
async def verify_token(token: verify_token):

    try:
        usertoken = token.access_token
    except AttributeError as e:
        usertoken = token['access_token']

    try:
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        decoded_token = auth.verify_id_token(usertoken, check_revoked=True)
        # Token is valid and not revoked.
        nick = execute_sql(f"SELECT Nickname FROM user WHERE `ID` = '{decoded_token['uid']}'")[0]['Nickname']
        decoded_token['nick'] = nick
        return decoded_token
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        raise HTTPException(status_code=400, detail=Token_Revoke)
    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        raise HTTPException(status_code=400, detail=User_Disabled)
    except auth.InvalidIdTokenError:
        # Token is invalid
        raise HTTPException(status_code=400, detail=Invalid_Token)"""
    

"""@userapi.post("/refresh_token")
async def refresh_token(requset: Request, refresh_token: Optional[str] = Cookie(None)):
    client = requset.client.host
    if refresh_token == None:
        return RedirectResponse(url= "/login")

    try:
        currentuser = Auth.refresh(refresh_token)
    except requests.HTTPError as e:
        error = json.loads(e.args[1])['error']['message']
        if error == "TOKEN_EXPIRED":
            raise HTTPException(400, Invalid_Token)
        

    userjson = {}
    userjson['id'] = currentuser['userId']
    userjson['access_token'] = currentuser['idToken']
    userjson['refresh_token'] = currentuser['refreshToken']  

    sql = "SELECT Login_IP FROM loginlog WHERE ID = \"%s\"" % userjson['id']
    lastip = execute_sql(sql)[0]['Login_IP']

    if lastip == client:
        return userjson
    else:
        auth.revoke_refresh_tokens(userjson['id'])
        raise HTTPException(401, login_ip_diffrent)"""