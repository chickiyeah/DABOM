from fastapi import FastAPI
import sys

from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from controller.database import __init__
from controller.onemsgdb import __init1__
from fastapi.responses import PlainTextResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
__init__()
__init1__()

from controller.nutrient import nutrientapi
from controller import userapi, diary, friends, food, group, websocket, Screen

@app.get('/robots.txt', response_class=PlainTextResponse)
def robots():
    data = """User-agent: *\nAllow: /"""
    return data

app.include_router(nutrientapi.nutrient)
app.include_router(userapi.userapi)
app.include_router(diary.diaryapi)
app.include_router(friends.friendapi)
app.include_router(food.foodapi)
app.include_router(group.groupapi)
app.include_router(websocket.chat)
app.include_router(Screen.ScreenRoute)
app.mount("/assets", StaticFiles(directory="FrontSide/assets"))