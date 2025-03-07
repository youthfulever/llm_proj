from abc import ABC, abstractmethod

from langchain_community.vectorstores import Milvus

from backend.utils_func import judgment_chat, search_qa, rag_service


class BaseNode(ABC):
    node_id:str
    node_name:str

    @abstractmethod
    def run(self,state: dict):
        pass



class ChatNode(BaseNode):
    def __init__(self, node_id, node_name):
        self.node_id = node_id
        self.node_name = node_name

    def run(self,state: dict):
        # step1:闲聊判断
        judgment_chat_res=judgment_chat(state['messages'][-1].content)
        if judgment_chat_res=='闲聊':
            state['messages']='请不要闲聊，这是频谱知识助手！'
            return state
        # step2:问答库匹配
        search_qa_res=search_qa(state['messages'][-1].content, threshold=0.7)
        # 匹配到qa
        if search_qa_res:
            state['messages']=search_qa_res['answer']
            state['question']=search_qa_res['question']
            return state
        # step3:RAG回答
        rag_res = rag_service(state['messages'][-1].content)
        state['messages'] = rag_res['answer']
        return state



