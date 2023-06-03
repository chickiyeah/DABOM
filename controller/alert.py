from fastapi import APIRouter, HTTPException, Depends, Request
from controller.onemsgdb import execute_pri_sql
from firebase_admin import auth

alert = APIRouter(prefix="/api/alert", tags=['friends'])

unauthorized = {'code':'ER013','message':'UNAUTHORIZED'}
unauthorized_revoked = {'code':'ER014','message':'UNAUTHORIZED (REVOKED TOKEN)'}
unauthorized_invaild = {'code':'ER015','message':'UNAUTHORIZED (TOKEN INVALID)'}
unauthorized_userdisabled = {'code':'ER016','message':'UNAUTHORIZED (TOKENS FROM DISABLED USERS)'}

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

Invalid_Token = {"code":"ER998", "message":"INVALID TOKEN"}
User_NotFound = {"code":"ER011", "message":"USER_NOT_FOUND"}

@alert.get('/u_amount')
async def get_unread_amount(Authorized: bool = Depends(verify_token)):
    if Authorized:
        uid = Authorized[1]

        unread_amount = execute_pri_sql(f"SELECT count(id) as `amount` FROM food.alert WHERE `read` = 'False' AND `target_id` = '{uid}'")
        return unread_amount[0]
    
@alert.get('/alerts')
async def get_alerts(page:int, Authorized: bool = Depends(verify_token)):
    if Authorized:
        uid = Authorized[1]

        curpage = (page - 1) * 10

        alerts = execute_pri_sql(f"SELECT * FROM food.alert WHERE `target_id` = '{uid}' LIMIT 10 OFFSET {curpage}")
        return alerts
