from datetime import datetime

from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List
app = FastAPI()


class ResponseData(BaseModel):
    username: str

responses = []
is_started = False

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许任何来源的请求
    allow_methods=["*"],  # 允许任何HTTP方法
    allow_headers=["*"],  # 允许任何请求头
)

@app.get("/start")
async def start():
    global responses, is_started
    responses = []
    is_started = True
    return {"message": "开始抢答！"}

@app.get("/stop")
async def stop():
    global responses, is_started
    responses = []
    is_started = False
    return {"message": "停止抢答！"}


@app.post("/begin")
async def begin(response_data: ResponseData):
    global responses, is_started
    if not is_started:
        raise HTTPException(status_code=400, detail="主持人还未允许抢答！")
    for r in responses:
        if r["username"] == response_data.username:
            raise HTTPException(status_code=400, detail="你已经抢答过了！")
    response = {"username": response_data.username, "time": datetime.now()}
    responses.append(response)
    return {"message": "抢答已提交，请看大屏！"}

@app.get("/ranking")
async def ranking():
    global responses, is_started
    if not is_started:
        return JSONResponse(content=[], status_code=200)
    sorted_responses = sorted(responses, key=lambda r: r["time"])
    data = [{"username": r["username"], "time": r["time"].strftime("%H:%M:%S.%f")[:-3]} for r in sorted_responses]
    return JSONResponse(content=data, status_code=200)

@app.get("/")
async def root():
    return {"message": "服务器已启动！"}

if __name__ == '__main__':

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)