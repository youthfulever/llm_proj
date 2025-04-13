from abc import ABC, abstractmethod

from langchain_community.vectorstores import Milvus

from backend.utils_func import judgment_chat, search_qa, rag_service, judgment_hallucination, query_rewrite


class BaseNode(ABC):
    node_id:str
    node_name:str

    @abstractmethod
    def run(self,state: dict):
        pass

def chatNode_run(state: dict):
    # step1:闲聊判断
    judgment_chat_res = judgment_chat(state['messages'][-1].content)
    if judgment_chat_res == '闲聊':
        state['messages'] = '请不要闲聊，这是频谱知识助手！'
        return state
    # step2:问答库匹配
    search_qa_res = search_qa(state['messages'][-1].content, threshold=0.7)
    # 匹配到qa
    if search_qa_res:
        state['messages'] = search_qa_res['answer']
        state['question'] = search_qa_res['question']
        return state
    # step3:RAG回答
    rag_res = rag_service(state['messages'][-1].content)
    state['messages'] = rag_res['answer']
    return state

class ChatNode(BaseNode):
    def __init__(self, node_id, node_name):
        self.node_id = node_id
        self.node_name = node_name

    def run(self,state: dict):
        state=chatNode_run(state)
        return state

class FineRAGNode(BaseNode):
    def __init__(self, node_id, node_name):
        self.node_id = node_id
        self.node_name = node_name

    def run(self,state: dict):
        # step1:闲聊判断
        query=state['messages'][-1].content
        temp_state=state
        judgment_chat_res=judgment_chat(query)
        if judgment_chat_res=='闲聊':
            state['messages']='请不要闲聊，这是频谱知识助手！'
            return state
        # step2:问答库匹配
        search_qa_res=search_qa(query, threshold=0.7)
        # 匹配到qa
        if search_qa_res:
            state['messages']=search_qa_res['answer']
            state['question']=search_qa_res['question']
            return state
        # step3:RAG回答
        rag_res = rag_service(query)
        state['messages'] = rag_res['answer']

        if judgment_hallucination(query,state['messages'])=='是':
            query=query_rewrite(query)
            temp_state['messages'][-1].content = query
            state = chatNode_run(temp_state)
        return state

