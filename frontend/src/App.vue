<template>
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="240px" class="sidebar">
      <div class="sidebar-header">
        <h3>养老服务数据分析系统</h3>
        <p>智能预测与资源管理</p>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        unique-opened
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/health">
          <el-icon><Document /></el-icon>
          <span>健康分析</span>
        </el-menu-item>
        <el-menu-item index="/service">
          <el-icon><Setting /></el-icon>
          <span>服务分析</span>
        </el-menu-item>
        <el-menu-item index="/prediction">
          <el-icon><TrendCharts /></el-icon>
          <span>需求预测</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI聊天</span>
        </el-menu-item>
        <el-menu-item index="/admin">
          <el-icon><Tools /></el-icon>
          <span>系统管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import {
  DataAnalysis,
  Document,
  HomeFilled,
  Setting,
  Tools,
  TrendCharts,
} from "@element-plus/icons-vue";
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const activeMenu = computed(() => {
  return route.path;
});
</script>

<style>
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
}

/* 全局美化滚动条 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  transition: background 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

::-webkit-scrollbar-corner {
  background: #f1f1f1;
}
</style>

<style scoped>
.app-container {
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  overflow: hidden;
}

.sidebar {
  background-color: #fff;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.el-main {
  flex: 1;
  padding: 0px;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #eaeef1;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #0066cc;
}

.sidebar-header p {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.sidebar-menu {
  /* margin-top: 20px; */
  border-right: none;
}

.el-menu-item {
  height: 56px;
  line-height: 56px;
  margin: 0 12px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.el-menu-item.is-active {
  background-color: #e8f3ff !important;
  color: #0066cc !important;
}

.el-menu-item:hover {
  background-color: #f5f7fa !important;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
