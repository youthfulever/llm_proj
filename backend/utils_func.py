import sqlite3
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_milvus import BM25BuiltInFunction, Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from backend.example_prompt import CHAT_JUDGMENT, HALLUCINATION_JUDGMENT, QUERY_REWRITE
from backend.model import my_llm, get_vectors, MyEmbeddings
from fastapi import Body
from pydantic import BaseModel

# 封装数据库初始化函数
def init_db():
    conn = sqlite3.connect('./db/users.db')
    c = conn.cursor()
    # 创建用户表（如果不存在）
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  password TEXT NOT NULL)''')
    conn.commit()
    # 插入初始用户（如果需要）
    c.execute("SELECT COUNT(*) FROM users WHERE username = 'zhangsan'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password) VALUES ('zhangsan', '123456')")
        conn.commit()
    conn.close()
    print("✅ 用户数据库初始化完成！")
    # return conn


# 初始化聊天数据库
def init_chat_db():
    # 连接数据库
    conn = sqlite3.connect("./db/chat.db")
    cursor = conn.cursor()

    # 创建 conversations 表，新增 talk_id 字段
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT NOT NULL,
            conversation_name TEXT NOT NULL,
            talk_id INTEGER NOT NULL,
            sender_message TEXT NOT NULL,
            robot_message TEXT NOT NULL,
            PRIMARY KEY (conversation_id, talk_id)  -- 组合主键，确保同一会话的 talk_id 唯一
        )
    ''')

    # 检查是否已经有数据，避免重复插入
    cursor.execute("SELECT COUNT(*) FROM conversations")
    count = cursor.fetchone()[0]

    if count == 0:
        # 插入一条默认的对话数据
        cursor.executemany('''
            INSERT INTO conversations (conversation_id, conversation_name, talk_id, sender_message, robot_message)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ("1710241234567", "示例对话", 0, "你好", "请不要闲聊"),
            ("1710241234567", "示例对话", 1, "你好啊", "请不要闲聊，这是频谱知识助手！"),
            ("1710241234600", "示例对话1", 0, "你好", "你好，我是一个 AI 助手"),
            ("1710241234600", "示例对话1", 1, "你能做什么？", "我可以回答你的问题！")
        ])
        print("✅ 初始对话数据已插入")

    # 提交 & 关闭数据库
    conn.commit()
    conn.close()
    print("✅ 数据库表 conversations 创建完成！")



def test1():
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
    print((conversations))
    return conversations


def get_conn_cursor():
    conn = sqlite3.connect('./db/users.db')
    c = conn.cursor()
    return c

# 获取数据库连接
def get_db_connection():
    conn = sqlite3.connect('./db/chat.db')
    conn.row_factory = sqlite3.Row
    return conn
# 调用数据库初始化函数
# conn = init_db()


embeddings = MyEmbeddings('local')
uri = "https://in03-c299f5d2a5e7139.serverless.gcp-us-west1.cloud.zilliz.com"
token = "5dfe30212b118e9115e661dd5207b2e9a2539d052e5b661402f52a75847fc5d7889c43588cdbd8287be77129ff66256bfe341a0c"

vectorstore_knowledge = Milvus(
    embedding_function=embeddings,
    collection_name='llm_knowledge',
    connection_args={"uri": uri, "token": token, "db_name": "llm"},
    index_params={"index_type": "FLAT", "metric_type": "COSINE"},
    consistency_level="Strong",
    drop_old=False,  # set to True if seeking to drop the collection with that name if it exists
    auto_id=True,
)
vectorstore_qa = Milvus(
    embedding_function=embeddings,
    collection_name='llm_qa',
    connection_args={"uri": uri, "token": token, "db_name": "llm"},
    index_params={"index_type": "FLAT", "metric_type": "COSINE"},
    consistency_level="Strong",
    drop_old=False,  # set to True if seeking to drop the collection with that name if it exists
    auto_id=True,
)

def judgment_chat(user_query):
    prompt = ChatPromptTemplate.from_template(CHAT_JUDGMENT)
    # 创建链
    chain = prompt | my_llm
    res = chain.invoke({"query": user_query}).content
    return res

def insert_qa(question, answer, source='null'):
    document = Document(
        page_content=question,
        metadata={"source": source, 'question': question, 'answer': answer},
    )
    vectorstore_qa.add_documents(documents=[document])

def search_qa(query, threshold=0.7):
    results = vectorstore_qa.similarity_search_with_score(
        query,
        k=2,
    )
    if results:
        try:
            res, score = results[0][0], results[0][1]
            if score > threshold:
                return {"question": res.metadata['question'], "answer": res.metadata['answer']}
        except:
            return
    return

def insert_knowledge(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore_knowledge.add_documents(documents=splits)

def search_knowledge(query, threshold=0.7):
    results = vectorstore_knowledge.similarity_search_with_score(
        query,
        k=2,
    )
    return results

def rag_service(query):
    retriever = vectorstore_knowledge.as_retriever()
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(my_llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    results = rag_chain.invoke({"input": query})

    return results

def judgment_hallucination(user_query,answer):
    prompt = ChatPromptTemplate.from_template(HALLUCINATION_JUDGMENT)
    # 创建链
    chain = prompt | my_llm
    res = chain.invoke({"query": user_query,"answer":answer}).content
    return res

def query_rewrite(user_query):
    prompt = ChatPromptTemplate.from_template(QUERY_REWRITE)
    # 创建链
    chain = prompt | my_llm
    res = chain.invoke({"query": user_query}).content
    return res



if __name__ == "__main__":
    # init_db()
    init_chat_db()
    test1()
    # insert_knowledge("./data/test.pdf")
    # print(rag_service('频段占用度判决门限是什么'))
    # insert_qa("频谱划分规定的网站去哪里查看？",
    #           "https://wap.miit.gov.cn/gyhxxhb/jgsj/cyzcyfgs/bmgz/wxdl/art/2023/art_1e98823e689f42ca9ed14dcb6feec07a.html")
