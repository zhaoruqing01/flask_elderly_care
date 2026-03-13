<template>
  <el-container class="admin-container">
    <el-header height="60px" class="header">
      <div class="header-left">
        <h2>系统管理</h2>
      </div>
    </el-header>
    <el-main>
      <!-- 系统信息 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>系统信息</span>
          </div>
        </template>
        <div class="system-info">
          <div class="info-item">
            <span class="info-label">系统版本:</span>
            <span class="info-value">v1.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">开发框架:</span>
            <span class="info-value">Flask + Vue3</span>
          </div>
          <div class="info-item">
            <span class="info-label">数据存储:</span>
            <span class="info-value">SQLite</span>
          </div>
          <div class="info-item">
            <span class="info-label">预测模型:</span>
            <span class="info-value">集成学习模型</span>
          </div>
        </div>
      </el-card>

      <!-- 数据管理 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>数据管理</span>
          </div>
        </template>
        <div class="data-management">
          <el-button type="primary" @click="generateData">
            <el-icon><Refresh /></el-icon>
            生成模拟数据
          </el-button>
          <el-button
            type="warning"
            @click="cleanData"
            style="margin-left: 10px"
          >
            <el-icon><Tools /></el-icon>
            清洗数据
          </el-button>
          <el-button
            type="success"
            @click="trainModel"
            style="margin-left: 10px"
          >
            <el-icon><Cpu /></el-icon>
            训练预测模型
          </el-button>
        </div>
      </el-card>

      <!-- 数据质量 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>数据质量</span>
            <el-button size="small" type="primary" @click="loadDataQuality">
              刷新
            </el-button>
          </div>
        </template>
        <el-table :data="dataQuality" style="width: 100%" show-overflow-tooltip>
          <el-table-column prop="name" label="数据类型" />
          <el-table-column prop="count" label="记录数" />
          <el-table-column prop="missing" label="缺失值" />
          <el-table-column prop="quality" label="质量状态">
            <template #default="scope">
              <el-tag
                :type="
                  scope.row.quality === '良好'
                    ? 'success'
                    : scope.row.quality === '一般'
                      ? 'warning'
                      : 'danger'
                "
              >
                {{ scope.row.quality }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 操作日志 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>操作日志</span>
          </div>
        </template>
        <el-table :data="logs" style="width: 100%" show-overflow-tooltip>
          <el-table-column prop="time" label="时间" />
          <el-table-column prop="action" label="操作" />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag
                :type="scope.row.status === '成功' ? 'success' : 'danger'"
              >
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="消息" />
        </el-table>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { Cpu, Refresh, Tools } from "@element-plus/icons-vue";
import axios from "axios";
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";

// 响应式数据
const dataQuality = ref([]);
const logs = ref([]);

// 生成数据
const generateData = async () => {
  if (!confirm("确定要重新生成模拟数据吗？这将清空现有数据！")) return;

  try {
    const response = await axios.post("/api/generate");
    if (response.data.error) {
      ElMessage.error("生成失败：" + response.data.error);
    } else {
      ElMessage.success(response.data.message);
      // 添加日志
      logs.value.unshift({
        time: new Date().toLocaleString(),
        action: "生成数据",
        status: "成功",
        message: response.data.message,
      });
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
    // 添加日志
    logs.value.unshift({
      time: new Date().toLocaleString(),
      action: "生成数据",
      status: "失败",
      message: "请求失败：" + error,
    });
  }
};

// 清洗数据
const cleanData = async () => {
  if (!confirm("确定要清洗数据吗？")) return;

  try {
    const response = await axios.post("/api/clean");
    if (response.data.error) {
      ElMessage.error("清洗失败：" + response.data.error);
    } else {
      ElMessage.success(
        `清洗完成！健康记录：删除 ${response.data.health.removed_count} 条异常记录，填充 ${response.data.health.filled_count} 条缺失值；服务记录：删除 ${response.data.service.removed_count} 条异常记录`,
      );
      // 添加日志
      logs.value.unshift({
        time: new Date().toLocaleString(),
        action: "清洗数据",
        status: "成功",
        message: `清洗完成！健康记录：删除 ${response.data.health.removed_count} 条异常记录，填充 ${response.data.health.filled_count} 条缺失值；服务记录：删除 ${response.data.service.removed_count} 条异常记录`,
      });
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
    // 添加日志
    logs.value.unshift({
      time: new Date().toLocaleString(),
      action: "清洗数据",
      status: "失败",
      message: "请求失败：" + error,
    });
  }
};

// 训练模型
const trainModel = async () => {
  if (!confirm("确定要训练模型吗？")) return;

  try {
    const response = await axios.post("/api/train");
    if (response.data.error) {
      ElMessage.error("训练失败：" + response.data.error);
      // 添加日志
      logs.value.unshift({
        time: new Date().toLocaleString(),
        action: "训练模型",
        status: "失败",
        message: "训练失败：" + response.data.error,
      });
    } else {
      ElMessage.success(
        `模型训练完成！R² 评分: ${response.data.r2_score}，MAE: ${response.data.mae}，RMSE: ${response.data.rmse}`,
      );
      // 添加日志
      logs.value.unshift({
        time: new Date().toLocaleString(),
        action: "训练模型",
        status: "成功",
        message: `模型训练完成！R² 评分: ${response.data.r2_score}，MAE: ${response.data.mae}，RMSE: ${response.data.rmse}`,
      });
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
    // 添加日志
    logs.value.unshift({
      time: new Date().toLocaleString(),
      action: "训练模型",
      status: "失败",
      message: "请求失败：" + error,
    });
  }
};

// 加载数据质量
const loadDataQuality = async () => {
  try {
    const response = await axios.get("/api/data-quality");
    if (response.data.error) {
      ElMessage.error("加载失败：" + response.data.error);
    } else {
      dataQuality.value = response.data.data;
      ElMessage.success("数据质量刷新完成");
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
  }
};

// 加载操作日志
const loadLogs = async () => {
  try {
    const response = await axios.get("/api/logs");
    if (response.data.error) {
      ElMessage.error("加载失败：" + response.data.error);
    } else {
      logs.value = response.data.data;
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
  }
};

// 页面加载时初始化
onMounted(() => {
  loadDataQuality();
  loadLogs();
});
</script>

<style scoped>
.admin-container {
  height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.header-left h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #0066cc;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.system-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f9fafb;
  border-radius: 6px;
}

.info-label {
  color: #666;
  font-weight: 500;
}

.info-value {
  color: #333;
  font-weight: 600;
}

.data-management {
  margin-top: 20px;
}
</style>
