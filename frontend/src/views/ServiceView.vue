<template>
  <el-container class="service-container">
    <el-header height="60px" class="header">
      <div class="header-left">
        <h2>服务数据分析</h2>
      </div>
      <div class="header-right">
        <el-tag type="info" size="small" effect="plain"> 数据看板 </el-tag>
      </div>
    </el-header>
    <el-main class="main-content">
      <!-- 页面简介 -->
      <div class="intro-section">
        <h3 class="section-title">养老服务使用分析</h3>
        <p class="section-desc">
          全面展示各类养老服务的使用情况、社区分布、满意度评价及变化趋势
        </p>
      </div>

      <!-- 主要内容区域 - 左右布局 -->
      <div class="content-wrapper">
        <!-- 左侧列 -->
        <div class="left-column">
          <!-- 服务使用频次 -->
          <el-card class="data-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <span class="title-text">服务使用频次</span>
              </div>
            </template>
            <div id="serviceFrequencyChart" class="chart-box"></div>
          </el-card>

          <!-- 服务满意度 -->
          <el-card class="data-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <span class="title-text">服务满意度评分</span>
              </div>
            </template>
            <div id="serviceSatisfactionChart" class="chart-box"></div>
          </el-card>
        </div>

        <!-- 右侧列 -->
        <div class="right-column">
          <!-- 按社区分析服务使用频次 -->
          <el-card class="data-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <span class="title-text">社区服务分布</span>
              </div>
            </template>
            <div id="serviceByCommunityChart" class="chart-box-large"></div>
          </el-card>

          <!-- 服务使用趋势 -->
          <el-card class="data-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <span class="title-text">服务使用趋势</span>
              </div>
            </template>
            <div id="serviceTrendChart" class="chart-box-large"></div>
          </el-card>
        </div>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import axios from "@/utils/http";
import * as echarts from "echarts";
import { onMounted, ref } from "vue";

// 类型定义
interface ServiceFrequency {
  types: string[];
  counts: number[];
}

interface ServiceByCommunity {
  communities: string[];
  datasets: {
    name: string;
    values: number[];
  }[];
}

interface ServiceSatisfaction {
  types: string[];
  scores: number[];
}

interface ServiceTrend {
  dates: string[];
  datasets: {
    name: string;
    values: number[];
  }[];
}

// 响应式数据
const serviceFrequency = ref<ServiceFrequency>({ types: [], counts: [] });
const serviceByCommunity = ref<ServiceByCommunity>({
  communities: [],
  datasets: [],
});
const serviceSatisfaction = ref<ServiceSatisfaction>({ types: [], scores: [] });
const serviceTrend = ref<ServiceTrend>({ dates: [], datasets: [] });

// 图表实例
let serviceFrequencyChart: echarts.ECharts | null = null;
let serviceByCommunityChart: echarts.ECharts | null = null;
let serviceSatisfactionChart: echarts.ECharts | null = null;
let serviceTrendChart: echarts.ECharts | null = null;

// 加载数据
const loadData = async () => {
  try {
    // 加载服务使用频次
    const frequencyRes = await axios.get("/api/service/frequency");
    serviceFrequency.value = frequencyRes.data;

    // 加载按社区分析的服务使用频次
    const communityRes = await axios.get("/api/service/frequency/community");
    serviceByCommunity.value = communityRes.data;

    // 加载服务满意度
    const satisfactionRes = await axios.get("/api/service/satisfaction");
    serviceSatisfaction.value = satisfactionRes.data;

    // 加载服务使用趋势
    const trendRes = await axios.get("/api/service/trend");
    serviceTrend.value = trendRes.data;

    // 初始化图表
    initCharts();
  } catch (error) {
    console.error("加载数据失败:", error);
  }
};

// 初始化图表
const initCharts = () => {
  // 服务使用频次图表
  if (serviceFrequencyChart) {
    serviceFrequencyChart.dispose();
  }
  serviceFrequencyChart = echarts.init(
    document.getElementById("serviceFrequencyChart"),
  );
  serviceFrequencyChart.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    xAxis: {
      type: "category",
      data: serviceFrequency.value.types || [],
    },
    yAxis: {
      type: "value",
    },
    series: [
      {
        name: "使用次数",
        type: "bar",
        data: serviceFrequency.value.counts || [],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#83bff6" },
            { offset: 0.5, color: "#188df0" },
            { offset: 1, color: "#188df0" },
          ]),
        },
      },
    ],
  });

  // 按社区分析服务使用频次图表
  if (serviceByCommunityChart) {
    serviceByCommunityChart.dispose();
  }
  serviceByCommunityChart = echarts.init(
    document.getElementById("serviceByCommunityChart"),
  );
  serviceByCommunityChart.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    legend: {
      data:
        serviceByCommunity.value.datasets?.map((item: any) => item.name) || [],
    },
    xAxis: {
      type: "category",
      data: serviceByCommunity.value.communities || [],
    },
    yAxis: {
      type: "value",
    },
    series:
      serviceByCommunity.value.datasets?.map((item: any) => ({
        name: item.name,
        type: "bar",
        data: item.data,
      })) || [],
  });

  // 服务满意度图表
  if (serviceSatisfactionChart) {
    serviceSatisfactionChart.dispose();
  }
  serviceSatisfactionChart = echarts.init(
    document.getElementById("serviceSatisfactionChart"),
  );
  serviceSatisfactionChart.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    xAxis: {
      type: "category",
      data: serviceSatisfaction.value.types || [],
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 5,
    },
    series: [
      {
        name: "满意度",
        type: "bar",
        data: serviceSatisfaction.value.scores || [],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#87e0fd" },
            { offset: 0.5, color: "#53cbf1" },
            { offset: 1, color: "#0096c7" },
          ]),
        },
      },
    ],
  });

  // 服务使用趋势图表
  if (serviceTrendChart) {
    serviceTrendChart.dispose();
  }
  serviceTrendChart = echarts.init(
    document.getElementById("serviceTrendChart"),
  );
  serviceTrendChart.setOption({
    tooltip: {
      trigger: "axis",
    },
    legend: {
      data: serviceTrend.value.datasets?.map((item: any) => item.name) || [],
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: serviceTrend.value.dates || [],
    },
    yAxis: {
      type: "value",
    },
    series:
      serviceTrend.value.datasets?.map((item: any) => ({
        name: item.name,
        type: "line",
        data: item.data,
      })) || [],
  });

  // 响应式调整
  window.addEventListener("resize", () => {
    serviceFrequencyChart?.resize();
    serviceByCommunityChart?.resize();
    serviceSatisfactionChart?.resize();
    serviceTrendChart?.resize();
  });
};

// 页面加载时初始化
onMounted(() => {
  loadData();
});
</script>

<style scoped>
.service-container {
  height: 100vh;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #ffffff;
  padding: 0 24px;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #303133;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.main-content {
  padding: 20px 24px;
  overflow-y: auto;
}

/* 简介区域 */
.intro-section {
  margin-bottom: 20px;
  padding: 16px 20px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.section-title {
  margin: 0 0 6px 0;
  color: #303133;
  font-size: 1.05rem;
  font-weight: 600;
}

.section-desc {
  margin: 0;
  color: #909399;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 内容包装器 - 左右布局 */
.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 16px;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 数据卡片 */
.data-card {
  background-color: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.data-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  border-color: #dcdfe6;
}

.card-title {
  display: flex;
  align-items: center;
}

.title-text {
  font-size: 1rem;
  font-weight: 600;
  color: #303133;
}

.chart-box {
  height: 260px;
  width: 100%;
}

.chart-box-large {
  height: 300px;
  width: 100%;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }

  .left-column,
  .right-column {
    gap: 16px;
  }
}

@media (min-width: 1201px) and (max-width: 1600px) {
  .content-wrapper {
    grid-template-columns: 1fr 1.3fr;
  }
}

@media (min-width: 1601px) {
  .content-wrapper {
    grid-template-columns: 1fr 1.5fr;
  }
}
</style>
