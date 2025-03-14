'''
接口文件
启动命令：uvicorn main:app --reload
'''

from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.websockets import WebSocket

from backend.utils_func import get_conn_cursor, get_db_connection
from backend.workflow.graph_engine import WorkFlow

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

# class Message(BaseModel):
#     mes: str
# @app.post("/chat")
# async def chat(message: Message = Body(...)):
#     work_flow = WorkFlow()
#     input_data = {'messages': message.mes}
#     # 频谱划分规定
#     response = work_flow.run(input_data)
#     return {"response": response['judgement_chat']['messages']}

class Message(BaseModel):
    model: str
    messages: list[dict[str, str]]
    max_tokens: int
@app.post("/chat")
async def chat(message: Message = Body(...)):
    work_flow = WorkFlow()
    input_data = {
        'model': message.model,
        'messages': message.messages[0]['content'],
        "max_tokens": message.max_tokens
        }
    # 频谱划分规定
    response = work_flow.run(input_data)
    return {"response": response['judgement_chat']['messages']}

@app.get("/conversations")
async def get_conversations():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查询所有对话记录
    cursor.execute("SELECT conversation_id, sender_message, robot_message, conversation_name FROM conversations")
    rows = cursor.fetchall()
    conn.close()

    # 处理数据，转换为前端需要的格式
    conversations = {}
    for row in rows:
        conversation_id = row["conversation_id"]
        sender_messages = row["sender_message"].split("||") if row["sender_message"] else []
        robot_messages = row["robot_message"].split("||") if row["robot_message"] else []
        talk_ids = list(range(len(sender_messages)))  # 生成 [0, 1, 2, ...] 的序列

        conversations[conversation_id] = {
            "sender_message": sender_messages,
            "robert_message": robot_messages,
            "talk_id": talk_ids,
            "conversation_name": row["conversation_name"]
        }

    return conversations

# @app.websocket("/chat")
# async def chat(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             # 等待接收客户端消息
#             data = await websocket.receive_text()

#             # 假设传入的消息可以直接作为Message模型解析
#             message = Message(mes=data)

#             work_flow = WorkFlow()
#             input_data = {'messages': message.mes}
#             response = work_flow.run(input_data)

#             # 发送响应给客户端
#             await websocket.send_json({"response": response['judgement_chat']['messages']})
#     except WebSocketDisconnect:
#         print("Client disconnected")

# # 新增登录验证的请求模型
# class LoginRequest(BaseModel):
#     username: str
#     password: str

# # 新增登录验证接口
# @app.post("/login")
# async def login(login_request: LoginRequest = Body(...)):
#     c=get_conn_cursor()
#     c.execute("SELECT * FROM users WHERE username =? AND password =?", (login_request.username, login_request.password))
#     user = c.fetchone()
#     if user:
#         return {"message": "登录成功", "success": True}
#     else:
#         return {"message": "用户名或密码错误", "success": False}

if __name__ == '__main__':
    import uvicorn
    # 注意：在生产环境中不要使用reload=True选项
    uvicorn.run(app, host="0.0.0.0", port=8000,  workers=1)