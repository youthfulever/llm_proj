from typing import List
from pymilvus import MilvusClient
from langchain_openai import ChatOpenAI


# LangChain 使用 OpenAI 模型时的设置
api_key = "sk-WeilCDHWP9Qdj9PBBgjOFv3PZESfVc8FTGDIGz0T2IxgN3I7"
base_url = "https://api.moonshot.cn/v1"
model = "moonshot-v1-8k"

# 设置 OpenAI 客户端（可以按需要使用 Moonshot API 代理）
my_llm = ChatOpenAI(
    openai_api_key=api_key,
    model_name=model,
    temperature=0.3,
    request_timeout=60,
    base_url=base_url
)

# print(my_llm.invoke("你是谁"))
import requests
import json


class CommonOcr(object):
    def __init__(self, data, matryoshka_dim=1792):
        # 请登录后前往 “工作台-账号设置-开发者信息” 查看 x-ti-app-id
        # 示例代码中 x-ti-app-id 非真实数据
        self._app_id = 'c162b7c3b88eac3b1dd71b403852e164'
        # 请登录后前往 “工作台-账号设置-开发者信息” 查看 x-ti-secret-code
        # 示例代码中 x-ti-secret-code 非真实数据
        self._secret_code = '2022d99a31ec876fb2b371d941d7da5a'
        self.input = {
                      "input": data,
                      "matryoshka_dim": matryoshka_dim
                     }

    def recognize(self):
        # 通用文本向量
        url = 'https://api.textin.com/ai/service/v1/acge_embedding'
        head = {}
        try:
            head['x-ti-app-id'] = self._app_id
            head['x-ti-secret-code'] = self._secret_code
            result = requests.post(url, json=self.input, headers=head)
            return result.text
        except Exception as e:
            return e


def get_vectors(input_list: List[str]) :
    response = CommonOcr(input_list, matryoshka_dim=1792)
    result = response.recognize()
    print()
    if json.loads(result)['code']==200:
        return json.loads(result)['result']['embedding']
    print('embedding解析错误')


from typing import List

from langchain_core.embeddings import Embeddings


class MyEmbeddings(Embeddings):

    def __init__(self, model: str):
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        res=get_vectors(texts)
        return res

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        res = get_vectors([text])[0]
        return res

if __name__ == '__main__':
    embeddings = MyEmbeddings("test-model")
    print(embeddings.embed_documents(["Hello", "world"]))
    print(embeddings.embed_query("Hello"))





