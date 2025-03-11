'''
接口文件
启动命令：uvicorn main:app --reload
'''

from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.websockets import WebSocket

from backend.utils_func import get_conn_cursor, insert_knowledge
from backend.workflow.graph_engine import WorkFlow
from fastapi import File, UploadFile

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，可以根据需要指定特定的origin
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头部
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

class Message(BaseModel):
    mes: str

@app.post("/chat")
async def chat(message: Message = Body(...)):
    work_flow = WorkFlow()
    input_data = {'messages': message.mes}
    # 频谱划分规定
    response = work_flow.run(input_data)
    return {"response": response['judgement_chat']['messages']}

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 等待接收客户端消息
            data = await websocket.receive_text()

            # 假设传入的消息可以直接作为Message模型解析
            message = Message(mes=data)

            work_flow = WorkFlow()
            input_data = {'messages': message.mes}
            response = work_flow.run(input_data)

            # 发送响应给客户端
            await websocket.send_json({"response": response['judgement_chat']['messages']})
    except WebSocketDisconnect:
        print("Client disconnected")

# 新增登录验证的请求模型
class LoginRequest(BaseModel):
    username: str
    password: str

# 新增登录验证接口
@app.post("/login")
async def login(login_request: LoginRequest = Body(...)):
    c=get_conn_cursor()
    c.execute("SELECT * FROM users WHERE username =? AND password =?", (login_request.username, login_request.password))
    user = c.fetchone()
    if user:
        return {"message": "登录成功", "success": True}
    else:
        return {"message": "用户名或密码错误", "success": False}

# 新增导入 PDF 文件的接口
@app.post("/import_pdf")
async def import_pdf(pdf_file: UploadFile = File(...)):
    try:
        # 保存文件到本地临时位置
        with open(f'./data/{pdf_file.filename}', "wb") as f:
            contents = await pdf_file.read()
            f.write(contents)
        # 调用 insert_knowledge 函数
        insert_knowledge(f'./data/{pdf_file.filename}')
        return {"message": "文件上传并处理成功"}
    except Exception as e:
        print(f"文件上传出错: {e}")
        return {"message": "文件上传出错，请稍后重试"}

if __name__ == '__main__':
    import uvicorn
    # 注意：在生产环境中不要使用reload=True选项
    uvicorn.run(app, host="0.0.0.0", port=8000,  workers=1)