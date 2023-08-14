from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse

app = FastAPI()


@app.route('/{_:path}')
async def https_redirect(request: Request):
    return RedirectResponse(request.url.replace(scheme='https'))