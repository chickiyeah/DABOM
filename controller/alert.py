from fastapi import APIRouter, HTTPException, Depends, Request, Cookie, Response, requests
from fastapi.responses import RedirectResponse
from controller.onemsgdb import execute_pri_sql
from firebase_admin import auth
from typing import Optional
from firebase import Firebase
from pydantic import BaseModel
import json
from urllib import parse

from controller.credentials import verify_token

alert = APIRouter(prefix="/api/alert", tags=['friends'])

unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

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

Invalid_Token = {"code":"ER998", "message":"INVALID TOKEN"}
User_NotFound = {"code":"ER011", "message":"USER_NOT_FOUND"}

@alert.get('/u_amount')
async def get_unread_amount(response: Response, access_token: Optional[str] = Cookie(None), refresh_token: Optional[str] = Cookie(None)):
    try:
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        user = auth.verify_id_token(access_token, check_revoked=True)
        print(user)
        
        uid = user['user_id']
        unread_amount = execute_pri_sql(f"SELECT count(id) as `amount` FROM food.alert WHERE `read` = 'False' AND `target_id` = '{uid}'")
        return unread_amount[0]
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
            currentuser = Auth.refresh(refresh_token)

            response.set_cookie(key="access_token", value=currentuser['idToken'], httponly=True)
            response.set_cookie(key="refresh_token", value=currentuser['refreshToken'], httponly=True)
            response.set_cookie(key="userId", value=currentuser['userId'], httponly=True)
            user = auth.verify_id_token(currentuser['idToken'], check_revoked=True)

            unread_amount = execute_pri_sql(f"SELECT count(id) as `amount` FROM food.alert WHERE `read` = 'False' AND `target_id` = '{uid}'")
            return unread_amount[0]
        except HTTPException as e:
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
    
@alert.get('/alerts')
async def get_alerts(response: Response, access_token: Optional[str] = Cookie(None), refresh_token: Optional[str] = Cookie(None)):
    try:
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        user = auth.verify_id_token(access_token, check_revoked=True)
        print(user)
        
        uid = user['user_id']
        alerts = execute_pri_sql(f"SELECT * FROM food.alert WHERE `target_id` = '{uid}' ORDER BY `read` ASC")
        return alerts

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
            currentuser = Auth.refresh(refresh_token)

            response.set_cookie(key="access_token", value=currentuser['idToken'], httponly=True)
            response.set_cookie(key="refresh_token", value=currentuser['refreshToken'], httponly=True)
            response.set_cookie(key="userId", value=currentuser['userId'], httponly=True)
            user = auth.verify_id_token(currentuser['idToken'], check_revoked=True)
            
            alerts = execute_pri_sql(f"SELECT * FROM food.alert WHERE `target_id` = '{uid}' ORDER BY `read` ASC")
            return alerts

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

class setread(BaseModel):
    url: str
    title: str
    msg: str
    pf_image:str

@alert.post("/setread")
async def setread(alert:setread, userId: Optional[str] = Cookie(None)):
    url = parse.unquote(alert.url)
    title = parse.unquote(alert.title)
    msg = parse.unquote(alert.msg)

    execute_pri_sql(f"UPDATE food.alert SET `read` = 'True' WHERE `target_id` = '{userId}' AND `title` = '{title}' AND `msg` = '{msg}' AND `url` = '{url}'")
    return "complete"