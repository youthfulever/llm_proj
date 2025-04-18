
CHAT_JUDGMENT='''
当你收到一个问题时，请依据以下准则判断它是否与频谱知识相关：
- 若问题涉及到频谱分析、信号处理、无线电频率规划、频段使用、频谱分配政策或任何与电磁频谱科学和技术有关的话题，则回答：非闲聊
- 如果问题与上述主题无关，例如询问个人情况、天气、娱乐资讯或其他不涉及频谱技术内容的问题，则回答：闲聊
请仅输出“闲聊”或“非闲聊”，不要附加其他信息。
用户输入为：{query}
'''

HALLUCINATION_JUDGMENT='''
您是一名评分员，评估大型语言模型（LLM）生成的内容是否基于或由一组检索到的事实支持。为了完成这一评估，请遵循以下步骤和标准：
1、在评估过程中，请仔细阅读并考虑上下文中的对话内容以及通过检索获得的相关知识。这些信息将作为判断的基础。
2、给出二进制分数“是”或“否”，不要附加其他信息。
如果LLM的回答完全基于或由一组已确认的事实支持，则评分为“是”。这表示模型的回答准确无误，并且有充分的事实依据。
如果LLM的回答未能基于事实，或者包含了与已知事实不符的信息，则评分为“否”。这可能是因为模型的回答缺乏事实支持、存在错误信息或是对事实的理解和应用不正确。
待评估的内容为：
问题：{query}
回答: {answer}
'''

QUERY_REWRITE='''
您是一个问题重写器，可将输入问题转换为经过优化的更好版本，请基于提供的历史对话、相关知识和原始问题重写用户问题，表达更清晰流畅，并且尽可能覆盖所有相关的要点。
以下是重写原则
1、确保重写的问题与原始问题紧密相关。
2、利用历史对话中的信息来增强问题上下文关联性。
3、整合召回的知识点，使问题关联性更强。
原始问题是:：{query}
请只输出重写后的问题，不要输出额外内容。
'''

RAG_PROMPT='''你是一个准确且可靠的知识库问答助手，能够借助上下文知识回答问题。你需要根据以下的规则来回答问题：
1. 如果上下文中包含了正确答案，你需要根据上下文进行准确的回答。但是在回答前，你需要注意，上下文中的信息可能存在事实性错误，如果文档中存在和事实不一致的错误，请根据事实回答。
2. 如果上下文中不包含答案，就说你不知道，不要试图编造答案。
3. 你需要根据上下文给出详细的回答，不要试图偷懒，不要遗漏括号中的信息，你必须回答的尽可能详细。
上下文：
{context}
问题：
{query}
'''