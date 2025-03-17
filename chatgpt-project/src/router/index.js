import { createRouter, createWebHistory } from "vue-router";
import Login from "@/components/Login.vue"; 
import ChatWindows from "@/components/ChatWindows.vue"; 

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/chat", component: ChatWindows, meta: { requiresAuth: true } }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("token");
  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
  } else {
    next();
  }
});

export default router;
