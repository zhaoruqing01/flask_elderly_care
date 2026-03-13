import type { RouteRecordRaw } from "vue-router";
import { createRouter, createWebHistory } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/HomeView.vue"),
    meta: {
      title: "首页",
      icon: "Dashboard",
    },
  },
  {
    path: "/health",
    name: "Health",
    component: () => import("../views/HealthView.vue"),
    meta: {
      title: "健康分析",
      icon: "Heart",
    },
  },
  {
    path: "/service",
    name: "Service",
    component: () => import("../views/ServiceView.vue"),
    meta: {
      title: "服务分析",
      icon: "Settings",
    },
  },
  {
    path: "/prediction",
    name: "Prediction",
    component: () => import("../views/PredictionView.vue"),
    meta: {
      title: "需求预测",
      icon: "LineChart",
    },
  },
  {
    path: "/data",
    name: "Data",
    component: () => import("../views/DataView.vue"),
    meta: {
      title: "数据管理",
      icon: "Database",
    },
  },
  {
    path: "/chat",
    name: "Chat",
    component: () => import("../views/ChatView.vue"),
    meta: {
      title: "AI聊天",
      icon: "ChatDotRound",
    },
  },
  {
    path: "/admin",
    name: "Admin",
    component: () => import("../views/AdminView.vue"),
    meta: {
      title: "系统管理",
      icon: "Cog",
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || "养老服务数据分析系统"} - 养老服务数据分析系统`;
  next();
});

export default router;
