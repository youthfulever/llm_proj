<template>
    <div class="login-container">
      <div class="login-box">
        <h2>用户登录</h2>
        <form @submit.prevent="handleLogin">
          <div class="input-group">
            <label for="username">用户名</label>
            <input type="text" v-model="username" placeholder="请输入用户名" required />
          </div>
  
          <div class="input-group">
            <label for="password">密码</label>
            <input type="password" v-model="password" placeholder="请输入密码" required />
          </div>
  
          <button type="submit">登录</button>
          <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import { useRouter } from "vue-router";
  
  export default {
    data() {
      return {
        username: "",
        password: "",
        errorMessage: "",
      };
    },
    setup() {
      const router = useRouter();
      return { router };
    },
    methods: {
      async handleLogin() {
        this.errorMessage = "";
  
        try {
          const response = await axios.post("http://127.0.0.1:8000/login", {
            username: this.username,
            password: this.password,
          });
  
          if (response.data.success) {
            console.log("✅ 登录成功");
            localStorage.setItem("token", response.data.token); // 存储 token
            this.router.push("/chat"); // 跳转到聊天界面
          } else {
            this.errorMessage = "用户名或密码错误";
          }
        } catch (error) {
          this.errorMessage = "登录失败，请稍后再试";
          console.error("❌ 登录请求失败", error);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: linear-gradient(to right, #667eea, #764ba2);
  }
  
  .login-box {
    width: 350px;
    padding: 20px;
    background: white;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    text-align: center;
  }
  
  h2 {
    margin-bottom: 20px;
    color: #333;
  }
  
  .input-group {
    margin-bottom: 15px;
    text-align: left;
  }
  
  .input-group label {
    display: block;
    margin-bottom: 5px;
    color: #555;
  }
  
  .input-group input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  button {
    width: 100%;
    padding: 10px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 10px;
  }
  
  button:hover {
    background: #564bb5;
  }
  
  .error {
    margin-top: 10px;
    color: red;
  }
  </style>
  