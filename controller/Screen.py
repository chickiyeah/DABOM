from fastapi import APIRouter, Request

from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates # html 템플레이트 로더
templates = Jinja2Templates(directory="FrontSide/templates")

ScreenRoute = APIRouter(prefix="",tags=["Screens"])

@ScreenRoute.get("/")
async def Screen(request: Request):
    return templates.TemplateResponse("index.html", {"request":request})

@ScreenRoute.get("/chat")
async def index(request: Request):
    return templates.TemplateResponse("chat.html", {"request":request})

@ScreenRoute.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request":request})

@ScreenRoute.get("/findaccount")
async def findaccount(request: Request):
    return templates.TemplateResponse("findaccount.html", {"request":request})

@ScreenRoute.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request":request})

@ScreenRoute.get("/posts")
async def posts(request: Request):
    return templates.TemplateResponse("posts.html", {"request":request})

@ScreenRoute.get("/diary_add")
async def diary_add(request: Request):
    return templates.TemplateResponse("diary_add.html", {"request":request})

@ScreenRoute.get("/diary_bar_scan")
async def diary_bar_scan(request: Request):
    return templates.TemplateResponse("diary_bar_scan.html", {"request":request})

@ScreenRoute.get("/diary_kcal")
async def diary_kcal(request: Request):
    return templates.TemplateResponse("diary_kcal.html", {"request":request})

@ScreenRoute.get("/diary_food_data_add")
async def diary_food_data_add(request: Request):
    return templates.TemplateResponse("diary_food_data_add.html", {"request":request})

@ScreenRoute.get("/diary_food_manualy_add")
async def diary_food_manualy_add(request: Request):
    return templates.TemplateResponse("diary_food_manualy_add.html", {"request":request})

@ScreenRoute.get("/diary_update")
async def diary_update(request: Request):
    return templates.TemplateResponse("diary_update.html", {"request": request})

@ScreenRoute.get("/groups")
async def groups(request: Request):
    return templates.TemplateResponse("group.html", {"request":request})

@ScreenRoute.get("/friend/request/{request_id}/{request_nickname}/{target_id}/{target_nickname}/{verify_id}")
async def friend_accept_reject(request: Request):
    return templates.TemplateResponse("email_friend_req.html", {"request":request})

@ScreenRoute.get("/friend")
async def friend(request: Request):
    return templates.TemplateResponse("friend.html", {"request":request})