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

    # 查询所有对话记录，按 conversation_id 和 talk_id 排序
    cursor.execute("SELECT conversation_id, talk_id, sender_message, robot_message, conversation_name FROM conversations ORDER BY conversation_id, talk_id")
    rows = cursor.fetchall()
    conn.close()

    # 处理数据，转换为前端需要的格式
    conversations = {}

    for row in rows:
        conversation_id = row["conversation_id"]

        # 如果 conversations 中还没有这个对话，初始化数据结构
        if conversation_id not in conversations:
            conversations[conversation_id] = {
                "sender_message": [],
                "robert_message": [],
                "talk_id": [],
                "conversation_name": row["conversation_name"]
            }

        # 按 talk_id 顺序添加消息
        conversations[conversation_id]["sender_message"].append(row["sender_message"])
        conversations[conversation_id]["robert_message"].append(row["robot_message"])
        conversations[conversation_id]["talk_id"].append(row["talk_id"])

    return conversations


class History_Message(BaseModel):
    conversation_id: str
    conversation_name: str
    talk_id: list[int]
    sender_message: list[str]
    robert_message: list[str]
@app.post("/update_conversation")
async def update_conversation(history_message: History_Message = Body(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    conversation_id = history_message.conversation_id
    conversation_name = history_message.conversation_name
    talk_ids = history_message.talk_id
    sender_messages = history_message.sender_message
    robert_messages = history_message.robert_message

    print(f"更新对话 {conversation_id}: {sender_messages} -> {robert_messages}")

    # **检查对话是否已存在**
    cursor.execute("SELECT talk_id FROM conversations WHERE conversation_id = ?", (conversation_id,))
    existing_talk_ids = {row["talk_id"] for row in cursor.fetchall()}  # 已存的 talk_id 集合

    new_data = []
    update_data = []

    for i in range(len(talk_ids)):
        talk_id = talk_ids[i]
        sender_message = sender_messages[i]
        robert_message = robert_messages[i]

        if talk_id in existing_talk_ids:
            # **更新已有的消息**
            update_data.append((sender_message, robert_message, conversation_name, conversation_id, talk_id))
        else:
            # **插入新的消息**
            new_data.append((conversation_id, conversation_name, talk_id, sender_message, robert_message))

    # **执行更新**
    if update_data:
        cursor.executemany('''
            UPDATE conversations 
            SET sender_message = ?, robot_message = ?, conversation_name = ?
            WHERE conversation_id = ? AND talk_id = ?
        ''', update_data)

    # **执行插入**
    if new_data:
        cursor.executemany('''
            INSERT INTO conversations (conversation_id, conversation_name, talk_id, sender_message, robot_message)
            VALUES (?, ?, ?, ?, ?)
        ''', new_data)

    conn.commit()
    conn.close()
    return {"message": "对话已同步"}


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