from fastapi import FastAPI, Response
import sys

from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from controller.database import __init__
from controller.onemsgdb import __init1__
from fastapi.responses import PlainTextResponse, FileResponse

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

@app.get('/favicon.ico')
async def favicon():
    return FileResponse(path="/assets/images/favico.ico", headers={"Content-Disposition": "attachment; filename=" + "favicon.ico"})

@app.get('/sitemap.xml')
async def get_sitemap():
    my_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""

    # Fetch your urls from database or somewhere else
    # Then add to the urls array
    urls = []
    suburl = ['','login', 'posts', 'chat', 'findaccount']
    for sub in suburl:
        urls.append(f"""<url>
              <loc>http://dabom.kro.kr/{sub}</loc>
              <lastmod>2023-05-25T08:16:41+00:00</lastmod>
              <changefreq>weekly</changefreq>
              <priority>0.8</priority>
          </url>""")

    my_sitemap += "\n".join(urls)
    my_sitemap += """</urlset>"""

    return Response(content=my_sitemap, media_type="application/xml")

app.include_router(nutrientapi.nutrient)
app.include_router(userapi.userapi)
app.include_router(diary.diaryapi)
app.include_router(friends.friendapi)
app.include_router(food.foodapi)
app.include_router(group.groupapi)
app.include_router(websocket.chat)
app.include_router(Screen.ScreenRoute)
app.mount("/assets", StaticFiles(directory="FrontSide/assets"))