import uuid
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from backend.workflow.node import ChatNode


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


class WorkFlow:

    def __init__(self,):

        self.edges = None

        # init langgraph state graph
        self.graph_builder = StateGraph(State)
        self.graph = None
        self.graph_config = {'configurable': {'thread_id': '1'}, 'recursion_limit': 50}

        self.build_nodes()
        self.build_edges()
        self.graph = self.graph_builder.compile()

    def build_edges(self):
        self.graph_builder.add_edge(START, self.chat_node.node_name)
        self.graph_builder.add_edge(self.chat_node.node_name, END)

    def build_nodes(self):
        self.chat_node=ChatNode(uuid.uuid4(),'judgement_chat')
        self.graph_builder.add_node(self.chat_node.node_name,self.chat_node.run)



    def run(self,input_data):
        for event in self.graph.stream(input_data, config=self.graph_config):
            # print(event)
            return event
        # for msg, metadata in self.graph.stream(input_data, stream_mode="messages",config=self.graph_config):
        #     print(msg)


if __name__ == '__main__':
    work_flow=WorkFlow()
    input_data={'messages':'频谱划分规定'}
    # input_data={'messages':'频段占用度判决门限是什么'}
    # 频谱划分规定
    response=work_flow.run(input_data)
    print(response['judgement_chat']['messages'])

