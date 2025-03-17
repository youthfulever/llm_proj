<template>
  <div class="chat-app">
    <!-- 左上角用户头像 -->
    <div class="user-avatar" @click="goToLogin">
      <img src="@/assets/logo.png" alt="用户头像" />
      <span v-if="isAuthenticated">已登录</span>
      <span v-else>请登录</span>
    </div>
    <!-- 左侧对话列表 -->
    <div class="sidebar">
      <button class="new-conversation" @click="newConversation">➕ 新建对话</button>
      <ul>
        <li v-for="conversationId in Object.keys(conversations)" :key="conversationId"
          :class="{ active: conversationId === currentConversationId }" @click="selectConversation(conversationId)">
          {{ conversations[conversationId].conversation_name || "未命名对话" }}
        </li>
      </ul>
    </div>

    <!-- 右侧聊天窗口 -->
    <div class="chat-container">
      <div class="chat-window">
        <div class="messages" ref="messagesContainer">
          <div v-for="(message, index) in combinedMessages" :key="index" class="message"
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
      inputMessage: "",
      conversations: {}, // 存储所有对话 { conversation_id: { sender_message: [], robert_message: [], conversation_name: "未命名对话" } }
      currentConversationId: null,
    };
  },
  computed: {
    combinedMessages() {
      if (!this.currentConversationId || !this.conversations[this.currentConversationId]) return [];
      const conv = this.conversations[this.currentConversationId];
      let messages = [];
      conv.sender_message.forEach((msg, i) => {
        messages.push({ sender: "user", text: msg });
        if (conv.robert_message[i]) {
          messages.push({ sender: "bot", text: conv.robert_message[i] });
        }
      });
      return messages;
    },
    isAuthenticated() {
      return localStorage.getItem("token") !== null;
    }
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  mounted() {
    // localStorage.clearLocalStorage()
    this.loadConversations();
    if (Object.keys(this.conversations).length === 0) {
      this.newConversation();
    }
    //  监听用户关闭页面事件  
    window.addEventListener("beforeunload",this.handleBeforeUnload);
  },
  beforeUnmount() {
    window.removeEventListener("beforeunload",this.handleBeforeUnload);
  },

  methods: {
    goToLogin() {
      this.router.push("/login"); // 跳转到登录页面
    },
    handleBeforeUnload() {
      if(this.currentConversationId){
        this.syncConversation(this.currentConversationId);
      }
    },  
    renderMath(text) {
      try {
        return katex.renderToString(text, { throwOnError: false, displayMode: true });
      } catch (error) {
        console.error("KaTeX 解析失败:", error);
        return text;
      }
    },
    async loadConversations() {
      try{
        const response = await axios.get("http://127.0.0.1:8000/conversations");  
        const serverConversations = response.data;  
        console.log(serverConversations); 
        this.conversations = serverConversations;
        // serverConversations.forEach(conv => {
        //   this.conversations[conv.conversation_id] =  {
        //     sender_message:conv.sender_message,
        //     robert_message:conv.robert_message, 
        //     talk_id: Array.from({length: conv.sender_message.length}, (_, i) => i+1), 
        //     conversation_name: conv.conversation_name,
        //   };
        // });
        const keys = Object.keys(this.conversations)
        if (keys.length>0){
          this.selectConversation(keys[0])
        }else {
          this.newConversation();
        }
        this.saveConversations();
      }catch(error){
        console.error("请求失败", error);
      } 
    },
    async syncConversation(conversationId) {
      if (!this.conversations[conversationId]) return; 
      const conversation = this.conversations[conversationId]; 
      try{
        const response = await axios.post("http://127.0.0.1:8000/update_conversation ",{
          conversation_id: conversationId,
          conversation_name: conversation.conversation_name,
          talk_id: conversation.talk_id,  
          sender_message: conversation.sender_message,
          robert_message: conversation.robert_message,

             
        }, {
        headers: { "Content-Type": "application/json" }
      });
        console.log(response.data);
      }catch(error){  
        console.error("对话同步失败", error);
      } 

    },
    async selectConversation(conversationId) {
      if(this.currentConversationId){
        await this.syncConversation(this.currentConversationId);  
      }
      this.currentConversationId = conversationId;
    },
    async sendMessage() {
      if (this.inputMessage.trim() === "") return;
      const userText = this.inputMessage;
      this.inputMessage = "";

      if (!this.currentConversationId || !this.conversations[this.currentConversationId]) {
        this.newConversation();
      }

      let conversation = this.conversations[this.currentConversationId];
      conversation.sender_message.push(userText);
      conversation.talk_id.push(conversation.sender_message.length-1); 
      conversation.robert_message.push("思考中...");

      if (conversation.sender_message.length === 1) {
        conversation.conversation_name = userText.substring(0, 10);
      }
      
      this.saveConversations();
      
      try {
        const response = await axios.post("http://127.0.0.1:8000/chat", {
          model: "gpt-3.5-turbo",
          messages: [{ role: "user", content: userText }],
          max_tokens: 150,
        });
        conversation.robert_message.pop();
        conversation.robert_message.push(response.data['response']);
        this.saveConversations();
      } catch (error) {
        conversation.robert_message.pop();
        conversation.robert_message.push("请求失败，请检查API Key");
        this.saveConversations();
        console.error("请求失败", error);
      }
    },
    newConversation() {
      const newId = Date.now().toString();
      this.currentConversationId = newId;
      this.conversations[newId] = {
        sender_message: [],
        robert_message: [],
        talk_id: [],
        conversation_name: "未命名对话",
      };
      this.saveConversations();
    },
    saveConversations() {
      localStorage.setItem("conversations", JSON.stringify(this.conversations));
    },
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
/* 用户头像样式 */
.user-avatar {
  position: absolute;
  top: 10px;
  right: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  background: white;
  padding: 5px 10px;
  border-radius: 20px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
  transition: 0.3s;
}

.user-avatar:hover {
  background: #f0f0f0;
}

.user-avatar img {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 8px;
}

.user-avatar span {
  font-size: 14px;
  color: #333;
}
</style>