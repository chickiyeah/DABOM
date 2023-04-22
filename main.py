from fastapi import FastAPI
import crypto
import sys
sys.modules['Cyrpto'] = crypto

from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from controller.database import __init__

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
__init__()

from controller.nutrient import nutrientapi

app.include_router(nutrientapi.nutrient)