from fastapi import APIRouter, HTTPException, Depends, Request, Cookie, Response
from firebase import Firebase
from typing import Optional
from firebase_admin import auth
import json
import requests

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

def verify_token(response: Response, req: Request, access_token: Optional[str] = Cookie(None), refresh_token: Optional[str] = Cookie(None)): 
    try:
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