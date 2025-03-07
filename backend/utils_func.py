from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_milvus import BM25BuiltInFunction, Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from backend.example_prompt import CHAT_JUDGMENT
from backend.model import my_llm, get_vectors, MyEmbeddings

embeddings=MyEmbeddings('local')
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
    res=chain.invoke({"query": user_query}).content
    return res

def insert_qa(question,answer,source='null'):
    document = Document(
        page_content=question,
        metadata={"source": source,'question':question,'answer':answer},
    )
    vectorstore_qa.add_documents(documents=[document])

def search_qa(query,threshold=0.7):
    results = vectorstore_qa.similarity_search_with_score(
        query,
        k=2,
    )
    if results:
        try:
            res, score =results[0][0],results[0][1]
            if score>threshold:
                return {"question":res.metadata['question'],"answer":res.metadata['answer']}
        except:
            return
    return

def insert_knowledge(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore_knowledge.add_documents(documents=splits)

def search_knowledge(query,threshold=0.7):
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



if __name__ == "__main__":
    # insert_knowledge("./data/test.pdf")
    print(rag_service('频段占用度判决门限是什么'))
    # insert_qa("频谱划分规定的网站去哪里查看？",
    #           "https://wap.miit.gov.cn/gyhxxhb/jgsj/cyzcyfgs/bmgz/wxdl/art/2023/art_1e98823e689f42ca9ed14dcb6feec07a.html")
