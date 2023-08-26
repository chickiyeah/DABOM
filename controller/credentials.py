from fastapi import APIRouter, HTTPException, Depends, Request, Cookie, Response
from firebase import Firebase
from typing import Optional
from firebase_admin import auth
import json
import requests
from datetime import datetime, timezone, timedelta
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import time
import os
import platform
import subprocess
import ctypes
import sys

unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}
User_NotFound = {"code":"ER011", "message":"USER_NOT_FOUND"} 

firebaseConfig = {
    "apiKey": "AIzaSyC58Oh7Lyb7EoB0FWZQ-qMqfqLtiTJIIFw",
    "authDomain": "dabom-ca6fe.firebaseapp.com",
    "projectId": "dabom-ca6fe",
    "storageBucket": "dabom-ca6fe.appspot.com",
    "messagingSenderId": "607249280151",
    "appId": "1:607249280151:web:abcff56e0b43b1abb00dd2",
    "databaseURL":"https://dabom-ca6fe-default-rtdb.firebaseio.com/"
}

Auth = Firebase(firebaseConfig).auth()

class NTP:

    time = datetime.now(timezone.utc)
 
    @classmethod
    def getNTPtime(cls, host ='time.windows.com', utc_std=9):                
        # NTP query (48 bypte)
        query = '\x1b' + 47 * '\0'       
        # Unix standard time, 1970 00:00:00
        # NTP standart time, 1900 00:00:00
        # difference time 70 years (sec) 
        STD1970 = 2208988800       
         
        try:
            # crate socket(IPv4, UDP)
            sock = socket(AF_INET, SOCK_DGRAM)      
            # send NTP query
            sock.sendto(query.encode(), (host, 123))            
            # receive from NTP     
            sock.settimeout(1)
            recv, addr = sock.recvfrom(1024)
            
            if recv and len(recv)==48:
                # struct : python byte <-> C struct
                # !:Big endian, I:unsigned int(4byte) = 48byte
                # [10]: tuple[10] index, unpack returned a tuple type
                ts = struct.unpack('!12I', recv)[10]          
                ts -= STD1970            
            else:
                raise NameError('recv error')
             
        except Exception as e:            
            sock.close()
            utc = datetime.now(timezone.utc)   
            NTP.time = utc.astimezone(timezone(timedelta(hours=utc_std)))      
            os.system('date ' + time.strftime('%m%d%H%M%Y.%S',time.timezone(timedelta(hours=utc_std))))    
            #print(e)
            return False
        else:
            # from timestamp to datetime
            utc = datetime.fromtimestamp(ts, tz=timezone.utc)            
            # convert utc to local time
            #NTP.time = utc.astimezone()
            # convert utc to other utc time
            NTP.time = utc.astimezone(timezone(timedelta(hours=utc_std)))
            os.system('date ' + time.strftime('%m%d%H%M%Y.%S',time.timezone(timedelta(hours=utc_std))))
             
        return True

def verify_token(response: Response, req: Request, access_token: Optional[str] = Cookie(None), refresh_token: Optional[str] = Cookie(None)): 
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
                    
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        user = auth.verify_id_token(access_token, check_revoked=True)

        uid = user['user_id']
        return True, uid

    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        raise HTTPException(status_code=401, detail=unauthorized_revoked)
    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        raise HTTPException(status_code=401, detail=unauthorized_userdisabled)
    except auth.InvalidIdTokenError:
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
                
        # Token is invalid
        if refresh_token == None:
            raise HTTPException(status_code=400, detail=unauthorized_invaild)

        try:
            currentuser = Auth.refresh(refresh_token)

            response.set_cookie(key="access_token", value=currentuser['idToken'], httponly=True)
            response.set_cookie(key="refresh_token", value=currentuser['refreshToken'], httponly=True)
            response.set_cookie(key="userId", value=currentuser['userId'], httponly=True)
            user = auth.verify_id_token(currentuser['idToken'], check_revoked=True)
            
            uid = user['user_id']
            return True, uid
        

        except requests.HTTPError as e:
            error = json.loads(e.args[1])['error']['message']
            if error == "TOKEN_EXPIRED":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            if error == "INVALID_REFRESH_TOKEN":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
            
            print("Auto_Login_Error "+error)
        
    except auth.UserNotFoundError:
        raise HTTPException(status_code=401, detail=User_NotFound)
    except KeyError:
        raise HTTPException(status_code=400, detail=unauthorized)
    except ValueError:
        raise HTTPException(status_code=422)
    
def verify_admin_token(req: Request): 
    try:
        token = req.headers["Authorization"]  
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        admin_token = "Bearer cncztSAt9m4JYA9"
        if str(token) == admin_token:
            return True, "admin"
        else:
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
    

def verify_email_token(access_token: str, refresh_token: str):
    try:
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        user = auth.verify_id_token(access_token, check_revoked=True)
        print(user)
        # Token is valid and not revoked.
        return True, user['email_verified']
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        raise HTTPException(status_code=401, detail=unauthorized_revoked)
    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        raise HTTPException(status_code=401, detail=unauthorized_userdisabled)
    except auth.InvalidIdTokenError:
        # Token is invalid
        if refresh_token == None:
            raise HTTPException(status_code=401, detail=unauthorized_invaild)

        try:
            currentuser = Auth.refresh(refresh_token)
            user = auth.verify_id_token(currentuser['idToken'], check_revoked=True)
            return True, user['email_verified']
        except requests.HTTPError as e:
            error = json.loads(e.args[1])['error']['message']
            if error == "TOKEN_EXPIRED":
                raise HTTPException(status_code=401, detail=unauthorized_invaild)
        
    except auth.UserNotFoundError:
        raise HTTPException(status_code=401, detail=User_NotFound)
    except KeyError:
        raise HTTPException(status_code=400, detail=unauthorized)