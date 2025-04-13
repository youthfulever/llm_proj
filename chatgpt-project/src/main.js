import { createApp } from "vue";
import App from "./App.vue";
import router from "./router"; // 引入 Vue Router

const app = createApp(App);
app.use(router); // 启用路由
app.mount("#app");
