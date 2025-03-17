<template>
  <div class="login-container">
    <div class="login-box">
      <h2>Login Form</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <input type="text" v-model="username" placeholder="Username" required />
        </div>

        <div class="input-group">
          <input type="password" v-model="password" placeholder="Password" required />
        </div>

        <button type="submit">Login</button>

        <!-- <p class="forgot-password">Forgot password? <a href="#">Click Here</a></p>
        <p class="signup">Don't have an account? <a href="#">Sign up</a></p> -->

        <!-- 背景浮动光影 -->
        <div class="floating-box"></div>
        <div class="floating-box box-2"></div>
        <div class="floating-box box-3"></div>
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
          localStorage.setItem("token", response.data.token);
          this.router.push("/chat");
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
/* 🌈 背景渐变，稍微调整颜色，增强清晰度 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, rgba(117, 255, 216, 0.4), rgba(201, 255, 126, 0.4));
  overflow: hidden;
}

/* 🎨 玻璃质感 UI */
.login-box {
  position: relative;
  width: 350px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.5); /* 让玻璃感更明显 */
  backdrop-filter: blur(15px) saturate(200%); /* 提高模糊度 & 饱和度 */
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.5); /* 让边框更亮 */
  box-shadow: inset 0 0 50px rgba(255, 255, 255, 0.4), 
              0 10px 30px rgba(0, 0, 0, 0.4); /* 让玻璃更有立体感 */
  text-align: center;
  animation: fadeIn 1s ease-in-out;
}


/* 📌 标题优化 */
h2 {
  color: #222;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

/* ✨ 输入框优化 */
.input-group {
  margin-bottom: 15px;
  text-align: center;
}

.input-group input {
  width: 90%;
  padding: 12px;
  border: none;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.3);
  color: #333;
  font-size: 16px;
  outline: none;
  transition: 0.3s ease;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.input-group input:focus {
  background: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
}

/* 🚀 登录按钮优化 */
button {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.3);
  color: #333;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: 0.3s ease;
}

button:hover {
  background: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.7);
}

/* 📝 额外文本优化 */
.forgot-password,
.signup {
  margin-top: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.forgot-password a,
.signup a {
  color: #ffdde1;
  text-decoration: none;
}

.forgot-password a:hover,
.signup a:hover {
  text-decoration: underline;
}

/* ✨ 背景浮动光影 */
.floating-box {
  position: absolute;
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  animation: floatUp 6s infinite alternate ease-in-out;
}

.box-2 {
  width: 60px;
  height: 60px;
  left: -30px;
  top: 50px;
  animation-duration: 8s;
}

.box-3 {
  width: 100px;
  height: 100px;
  right: -50px;
  bottom: -50px;
  animation-duration: 10s;
}

/* 💡 浮动动画 */
@keyframes floatUp {
  from {
    transform: translateY(0px) scale(1);
    opacity: 0.7;
  }
  to {
    transform: translateY(-20px) scale(1.1);
    opacity: 1;
  }
}

/* 🎬 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
