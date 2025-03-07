'''
接口文件
启动命令：uvicorn main:app --reload
'''

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/chat")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

