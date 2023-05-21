import json
from typing import Union
import pandas as pd

import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from fastapi_utils.tasks import repeat_every
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime
from dbClass import dbClass


app = FastAPI()

cse191db = dbClass()

origins = [
    "https://cse191.ucsd.edu"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)


def setHeaders(response: Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Origin,X-Requested-With,Content-Type,Authorization,Accept'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response.headers['Service'] = 'CSE191-G04-API'


class DeviceInfo(BaseModel):
    group_id: str
    mac: str

class DeviceLog(BaseModel):
    gn: str
    espmac: str
    devices: list

@app.get('/', response_class=PlainTextResponse)
def home():
    return 'Group04 API\n'


@app.get('/health')
def process_health(response: Response):
    setHeaders(response)
    return {"resp": "OK"}

@app.on_event("startup")
@repeat_every(seconds=60*60)
def process_set_timeouts():
    if (cse191db.postWeather()):
        print("Successfully posted weather")
    else:
        print("Error posting weather")

# run the app
if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8004, reload=True)
