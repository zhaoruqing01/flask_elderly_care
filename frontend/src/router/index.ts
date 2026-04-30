import type { RouteRecordRaw } from "vue-router";
import { createRouter, createWebHistory } from "vue-router";
import { hasRole, isAuthenticated } from "../utils/auth";

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/LoginView.vue"),
    meta: {
      title: "登录",
    },
  },
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

// 定义需要认证的路由白名单（除了这些路由外都需要登录）
const publicRoutes = ["/login"];

// 定义角色权限映射（可选：某些页面只允许特定角色访问）
const rolePermissions: Record<string, string[]> = {
  // 系统管理页面只允许 institution 角色访问
  "/admin": ["institution"],
};

const router = createRouter({
  history: createWebHistory(),
  routes,
});

/**
 * 全局前置路由守卫
 * 功能：
 * 1. 未登录用户不能访问需要认证的页面
 * 2. 已登录用户访问登录页时重定向到首页
 * 3. 根据用户角色限制访问特定页面
 */
router.beforeEach((to, from, next) => {
  const isLoggedIn = isAuthenticated();
  const isPublicRoute = publicRoutes.includes(to.path);

  // 1. 如果访问的是公开路由（如登录页）
  if (isPublicRoute) {
    // 已登录用户访问登录页，重定向到首页
    if (isLoggedIn) {
      next("/");
    } else {
      next();
    }
    return;
  }

  // 2. 如果访问的是需要认证的路由
  if (!isLoggedIn) {
    // 未登录，重定向到登录页，并记录目标路径以便登录后跳转
    next({
      path: "/login",
      query: { redirect: to.fullPath },
    });
    return;
  }

  // 3. 检查角色权限（如果配置了角色限制）
  const allowedRoles = rolePermissions[to.path];
  if (allowedRoles && allowedRoles.length > 0) {
    const userHasPermission = allowedRoles.some((role) => hasRole(role));
    if (!userHasPermission) {
      // 没有权限，重定向到首页或显示错误页面
      console.warn(
        `用户没有权限访问 ${to.path}，需要角色: ${allowedRoles.join(", ")}`,
      );
      next("/");
      return;
    }
  }

  // 4. 所有检查通过，允许访问
  next();
});

export default router;
