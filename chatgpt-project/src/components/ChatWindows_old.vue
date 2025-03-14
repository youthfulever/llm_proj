<template>
    <div class="chat-app">
      <!-- 左侧对话列表 -->
      <div class="sidebar">
        <button class="new-conversation" @click="newConversation">➕ 新建对话</button>
        <ul>
          <li v-for="conversation in conversations" :key="conversation.id"
            :class="{ active: conversation.id === currentConversationId }" @click="selectConversation(conversation.id)">
            {{ conversation.title || "未命名对话" }}
          </li>
        </ul>
      </div>
  
      <!-- 右侧聊天窗口 -->
      <div class="chat-container">
        <div class="chat-window">
          <div class="messages" ref="messagesContainer">
            <div v-for="(message, index) in messages" :key="index" class="message"
              :class="{ 'user-message': message.sender === 'user', 'bot-message': message.sender === 'bot' }">
              <span v-if="message.sender === 'bot'" v-html="renderMath(message.text)"></span>
              <span v-else>{{ message.text }}</span>
            </div>
          </div>
          <div class="input-container">
            <input type="text" v-model="inputMessage" @keyup.enter="sendMessage" placeholder="输入你的问题..." />
            <button @click="sendMessage">发送</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  <script>
  
  import axios from "axios";
  import katex from "katex";
  import "katex/dist/katex.min.css";
  
  export default {
    data() {
      return {
        // messages: [],
        // inputMessage: "",
        messages: [],  // 当前对话消息
        inputMessage: "",
        conversations: [], // 存储所有对话 [{ id, title, messages }]
        currentConversationId: null, // 记录当前对话ID
      };
    },
    mounted() {
      this.loadConversations(); // 页面加载时获取历史对话
    },
    methods: {
      renderMath(text) {
        try {
          return katex.renderToString(text, {
            throwOnError: false,
            displayMode: true,
          });
        } catch (error) {
          console.error("KaTeX 解析失败:", error);
          return text; // 如果解析失败，直接返回文本
        }
      },
      // 加载历史对话
      loadConversations() {
        const savedConversations = JSON.parse(localStorage.getItem("conversations")) || [];
        this.conversations = savedConversations;
        if (this.conversations.length > 0) {
          this.selectConversation(this.conversations[0].id); // 默认选择第一个对话
        }
      },
      // 选择一个历史对话
      selectConversation(conversationId) {
        const conversation = this.conversations.find(c => c.id === conversationId);
        if (conversation) {
          this.currentConversationId = conversationId;
          this.messages = conversation.messages;
        }
      },
      // 发送消息
      async sendMessage() {
        if (this.inputMessage.trim() !== "") {
          const userText = this.inputMessage;
          this.messages.push({ text: userText, sender: "user" });
          this.inputMessage = ""; // 清空输入框
          this.$nextTick(() => this.scrollToBottom());
          // 如果当前对话的名字还是 "新对话"，则用第一条消息的前8个字作为标题
          let conversation = this.conversations.find(c => c.id === this.currentConversationId);
          if (conversation && conversation.title === "新对话") {
            conversation.title = userText.substring(0, 8); // 截取前8个字
          }
          await this.fetchResponse(userText);
          this.saveConversations(); // 保存对话记录
        }
      },
      async fetchResponse(userText) {
        this.messages.push({ text: "思考中...", sender: "bot" });  // 提前占位
        try {
          const response = await axios.post(
            "http://127.0.0.1:8000/chat",
            {
              model: "gpt-3.5-turbo",
              messages: [{ role: "user", content: userText }],
              max_tokens: 150,
            },
            {
              headers: {
                "Content-Type": "application/json",
                // Authorization: `Bearer YOUR_API_KEY`,
              },
            }
          );
          this.messages.pop(); // 移除"思考中..."
          let botReply = response.data['response'];
          this.messages.push({ text: botReply, sender: "bot" });
          // this.messages.push({ text: response.data['response'], sender: "bot" });
  
          // const botReply = response.data.choices[0].message.content.trim();
          // this.messages.push({ text: botReply, sender: "bot" });
          // this.$nextTick(() => this.scrollToBottom());
        } catch (error) {
          this.messages.pop(); // 移除"思考中..."
          this.messages.push({ text: "请求失败，请检查API Key", sender: "bot" });
          console.error("请求失败", error);
          // console.error("请求失败", error);
          // this.messages.push({ text: "请求失败，请检查API Key", sender: "bot" });
        }
        this.$nextTick(() => this.scrollToBottom());
      },
      // 新建对话
      newConversation() {
        const newId = Date.now().toString(); // 生成唯一 ID
        this.currentConversationId = newId;
        this.messages = [];
  
        this.conversations.unshift({ id: newId, title: "新对话", messages: [] });
        this.saveConversations();
      },
      // 保存对话到 localStorage
      saveConversations() {
        const index = this.conversations.findIndex(c => c.id === this.currentConversationId);
        if (index !== -1) {
          this.conversations[index].messages = this.messages;
        } else {
          this.conversations.push({ id: this.currentConversationId, title: "未命名对话", messages: this.messages });
        }
        localStorage.setItem("conversations", JSON.stringify(this.conversations));
      },
      scrollToBottom() {
        this.$nextTick(() => {
          const container = this.$refs.messagesContainer;
          if (container) {
            container.scrollTop = container.scrollHeight;
          }
        });
      },
      // scrollToBottom() {
      //   this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
      // },
    },
  };
  </script>
  
  <style scoped>
  /* 让整个应用占满视口 */
  .chat-app {
    display: flex;
    width: 100vw;
    /* 视口宽度 */
    height: 100vh;
    /* 视口高度 */
    overflow: hidden;
  }
  
  /* 左侧对话列表 */
  .sidebar {
    width: 250px;
    background: linear-gradient(to bottom, rgba(173, 223, 173, 0.8), rgba(249, 237, 190, 0.8));
    padding: 15px;
    border-right: 1px solid rgba(200, 200, 200, 0.5);
    /* 柔和的分割线 */
    display: flex;
    flex-direction: column;
  }
  
  
  
  /* 侧边栏中的对话列表 */
  .sidebar ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .sidebar li {
    padding: 12px;
    cursor: pointer;
    border-radius: 8px;
    transition: background 0.3s;
  }
  
  .sidebar li.active {
    background: #667eea;
    color: white;
  }
  
  .sidebar li:hover {
    background: #ddd;
  }
  
  /* 新建对话按钮 */
  .new-conversation {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 12px;
    cursor: pointer;
    margin-bottom: 10px;
    font-size: 14px;
    transition: 0.3s;
  }
  
  .new-conversation:hover {
    background: #564bb5;
  }
  
  /* 右侧聊天窗口区域 */
  .chat-container {
    flex-grow: 1;
    /* 让聊天窗口填充剩余空间 */
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(to right, rgba(167, 227, 226, 0.7), rgba(195, 162, 225, 0.7));
    height: 100vh;
    /* 确保与 .chat-app 高度一致 */
  
  }
  
  
  /* 聊天窗口 */
  .chat-window {
    width: 100%;
    max-width: 800px;
    height: 70vh;
    display: flex;
    flex-direction: column;
    border-radius: 12px;
    /* backdrop-filter: blur(20px) saturate(180%) brightness(90%); */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.8);
    /* 玻璃质感边框 */
    overflow: hidden;
  
  }
  
  
  /* 消息区域 */
  .messages {
    flex: 1;
    padding: 10px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
    background: #f9f9f9;
  }
  
  /* 消息样式 */
  .message {
    max-width: 80%;
    padding: 10px 15px;
    border-radius: 18px;
    font-size: 14px;
    line-height: 1.4;
    word-wrap: break-word;
  }
  
  /* 用户消息 */
  .user-message {
    align-self: flex-end;
    background: #667eea;
    color: white;
  }
  
  /* 机器人消息 */
  .bot-message {
    align-self: flex-start;
    background: #e5e5ea;
    color: black;
  }
  
  /* 输入框 & 发送按钮 */
  .input-container {
    display: flex;
    padding: 10px;
    background: #fff;
    border-top: 1px solid #ddd;
  }
  
  .input-container input {
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 20px;
    background: #f1f1f1;
    outline: none;
    font-size: 14px;
    transition: 0.3s;
  }
  
  .input-container input:focus {
    background: #e1e1e1;
  }
  
  .input-container button {
    margin-left: 10px;
    padding: 10px 15px;
    border: none;
    background: #667eea;
    color: white;
    border-radius: 20px;
    cursor: pointer;
    transition: 0.3s;
  }
  
  .input-container button:hover {
    background: #564bb5;
  }
  .katex {
    font-size: 1.2em;
  }
  </style>