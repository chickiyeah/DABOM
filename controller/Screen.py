from fastapi import APIRouter, Request

from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates # html 템플레이트 로더
templates = Jinja2Templates(directory="FrontSide/templates")

ScreenRoute = APIRouter(prefix="",tags=["Screens"])

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

@ScreenRoute.get("/friend/request/{request_id}/{request_nickname}/{target_id}/{target_nickname}/{verify_id}")
async def friend_accept_reject(request: Request):
    return "."

@ScreenRoute.get("/friend")
async def friend(request: Request):
    return templates.TemplateResponse("friend.html", {"request":request})