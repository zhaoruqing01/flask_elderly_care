<template>
  <el-container class="health-container">
    <el-header height="60px" class="header">
      <div class="header-left">
        <h2>健康分析</h2>
      </div>
      <div class="header-right">
        <el-button size="small" type="primary" @click="openHealthOverview">
          健康概览
        </el-button>
        <el-button size="small" type="success" @click="openHealthRecommendations" style="margin-left: 10px">
          健康建议
        </el-button>
      </div>
    </el-header>
    <el-main>
      <!-- 健康状态分布 -->
      <el-card style="margin-bottom: 20px" @click="openHealthDistributionDetail">
        <template #header>
          <div class="card-header">
            <span>健康状态分布</span>
            <el-button size="small" type="primary" @click.stop="openHealthDistributionDetail">
              查看详情
            </el-button>
          </div>
        </template>
        <div id="healthDistributionChart" class="chart-container"></div>
      </el-card>

      <!-- 按年龄段分析健康状态 -->
      <el-card style="margin-bottom: 20px" @click="openHealthByAgeDetail">
        <template #header>
          <div class="card-header">
            <span>按年龄段分析健康状态</span>
            <el-button size="small" type="primary" @click.stop="openHealthByAgeDetail">
              查看详情
            </el-button>
          </div>
        </template>
        <div id="healthByAgeChart" class="chart-container"></div>
      </el-card>

      <!-- 健康状态趋势 -->
      <el-card @click="openHealthTrendDetail">
        <template #header>
          <div class="card-header">
            <span>健康状态趋势</span>
            <el-button size="small" type="primary" @click.stop="openHealthTrendDetail">
              查看详情
            </el-button>
          </div>
        </template>
        <div id="healthTrendChart" class="chart-container"></div>
      </el-card>
    </el-main>

    <!-- 弹窗组件 -->
    <!-- 健康概览弹窗 -->
    <el-dialog
      v-model="dialogVisible.overview"
      title="健康概览"
      width="700px"
    >
      <div class="dialog-content">
        <h3>健康状况总览</h3>
        <el-table :data="healthOverviewData" style="width: 100%">
          <el-table-column prop="indicator" label="指标" width="150" />
          <el-table-column prop="value" label="数值" width="100" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="change" label="变化" width="100" />
          <el-table-column prop="description" label="说明" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="healthOverviewChart"></div>
      </div>
    </el-dialog>

    <!-- 健康状态分布详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.distribution"
      title="健康状态分布详情"
      width="700px"
    >
      <div class="dialog-content">
        <h3>健康状态详细分布</h3>
        <el-table :data="healthDistributionDetailData" style="width: 100%">
          <el-table-column prop="status" label="健康状态" width="120" />
          <el-table-column prop="count" label="人数" width="100" />
          <el-table-column prop="percentage" label="占比" width="100" />
          <el-table-column prop="male_count" label="男性" width="80" />
          <el-table-column prop="female_count" label="女性" width="80" />
          <el-table-column prop="avg_age" label="平均年龄" width="100" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="healthDistributionDetailChart"></div>
      </div>
    </el-dialog>

    <!-- 按年龄段分析详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.byAge"
      title="按年龄段分析详情"
      width="700px"
    >
      <div class="dialog-content">
        <h3>各年龄段健康状态分析</h3>
        <el-table :data="healthByAgeDetailData" style="width: 100%">
          <el-table-column prop="age_group" label="年龄段" width="120" />
          <el-table-column prop="good_count" label="良好" width="80" />
          <el-table-column prop="critical_count" label="临界" width="80" />
          <el-table-column prop="high_risk_count" label="高危" width="80" />
          <el-table-column prop="total" label="总计" width="80" />
          <el-table-column prop="high_risk_rate" label="高危率" width="100" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="healthByAgeDetailChart"></div>
      </div>
    </el-dialog>

    <!-- 健康状态趋势详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.trend"
      title="健康状态趋势详情"
      width="700px"
    >
      <div class="dialog-content">
        <h3>健康状态变化趋势</h3>
        <el-table :data="healthTrendDetailData" style="width: 100%">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="good_count" label="良好" width="80" />
          <el-table-column prop="critical_count" label="临界" width="80" />
          <el-table-column prop="high_risk_count" label="高危" width="80" />
          <el-table-column prop="high_risk_rate" label="高危率" width="100" />
          <el-table-column prop="change" label="变化" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="healthTrendDetailChart"></div>
      </div>
    </el-dialog>

    <!-- 健康建议弹窗 -->
    <el-dialog
      v-model="dialogVisible.recommendations"
      title="健康建议"
      width="700px"
    >
      <div class="dialog-content">
        <h3>健康照护建议</h3>
        <el-table :data="healthRecommendationsData" style="width: 100%">
          <el-table-column prop="category" label="类别" width="120" />
          <el-table-column prop="title" label="标题" width="180" />
          <el-table-column prop="content" label="建议内容" />
          <el-table-column prop="target" label="适用人群" width="120" />
        </el-table>
      </div>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import axios from "axios";
import * as echarts from "echarts";
import { onMounted, ref } from "vue";

// 类型定义
interface HealthDistribution {
  values: number[];
}

interface HealthByAge {
  age_groups: string[];
  datasets: {
    name: string;
    values: number[];
  }[];
}

interface HealthTrend {
  dates: string[];
  datasets: {
    name: string;
    values: number[];
  }[];
}

// 响应式数据
const healthDistribution = ref<HealthDistribution>({ values: [] });
const healthByAge = ref<HealthByAge>({ age_groups: [], datasets: [] });
const healthTrend = ref<HealthTrend>({ dates: [], datasets: [] });

// 弹窗状态
const dialogVisible = ref({
  overview: false,
  distribution: false,
  byAge: false,
  trend: false,
  recommendations: false
});

// 详情数据
const healthOverviewData = ref([
  { indicator: "总人数", value: 400, unit: "人", change: "↑ 2%", description: "本月老人总数" },
  { indicator: "健康良好", value: 280, unit: "人", change: "↑ 1%", description: "健康状态良好的老人" },
  { indicator: "临界状态", value: 80, unit: "人", change: "→ 0%", description: "健康状态临界的老人" },
  { indicator: "高危状态", value: 40, unit: "人", change: "↓ 3%", description: "健康状态高危的老人" },
  { indicator: "平均年龄", value: 75, unit: "岁", change: "↑ 0.5%", description: "所有老人的平均年龄" },
  { indicator: "男性比例", value: 45, unit: "%", change: "→ 0%", description: "男性老人占比" },
  { indicator: "女性比例", value: 55, unit: "%", change: "→ 0%", description: "女性老人占比" }
]);

const healthDistributionDetailData = ref([
  { status: "良好", count: 280, percentage: "70%", male_count: 126, female_count: 154, avg_age: 72 },
  { status: "临界", count: 80, percentage: "20%", male_count: 36, female_count: 44, avg_age: 78 },
  { status: "高危", count: 40, percentage: "10%", male_count: 18, female_count: 22, avg_age: 82 }
]);

const healthByAgeDetailData = ref([
  { age_group: "60-69岁", good_count: 90, critical_count: 25, high_risk_count: 5, total: 120, high_risk_rate: "4.2%" },
  { age_group: "70-79岁", good_count: 120, critical_count: 25, high_risk_count: 5, total: 150, high_risk_rate: "3.3%" },
  { age_group: "80-89岁", good_count: 60, critical_count: 25, high_risk_count: 5, total: 90, high_risk_rate: "5.6%" },
  { age_group: "90岁以上", good_count: 10, critical_count: 5, high_risk_count: 25, total: 40, high_risk_rate: "62.5%" }
]);

const healthTrendDetailData = ref([
  { date: "2024-01", good_count: 270, critical_count: 85, high_risk_count: 45, high_risk_rate: "11.3%", change: "↑ 0.5%" },
  { date: "2024-02", good_count: 275, critical_count: 82, high_risk_count: 43, high_risk_rate: "10.8%", change: "↓ 0.5%" },
  { date: "2024-03", good_count: 280, critical_count: 80, high_risk_count: 40, high_risk_rate: "10.0%", change: "↓ 0.8%" },
  { date: "2024-04", good_count: 285, critical_count: 78, high_risk_count: 37, high_risk_rate: "9.3%", change: "↓ 0.7%" },
  { date: "2024-05", good_count: 290, critical_count: 75, high_risk_count: 35, high_risk_rate: "8.8%", change: "↓ 0.5%" }
]);

const healthRecommendationsData = ref([
  { category: "饮食", title: "合理膳食", content: "建议每日摄入多样化的食物，包括谷物、蔬菜、水果、蛋白质和奶制品，控制盐和油脂的摄入", target: "所有老人" },
  { category: "运动", title: "适量运动", content: "建议每天进行30分钟左右的轻度运动，如散步、太极拳等，增强体质", target: "健康良好老人" },
  { category: "监测", title: "定期体检", content: "建议每半年进行一次全面体检，及时发现和处理健康问题", target: "所有老人" },
  { category: "照护", title: "专人照护", content: "对于高危老人，建议安排专人照护，定期监测健康状况", target: "高危老人" },
  { category: "用药", title: "规范用药", content: "建议按照医嘱规范用药，不要自行增减药量", target: "有慢性疾病老人" },
  { category: "心理", title: "心理健康", content: "建议保持积极乐观的心态，多参加社交活动，避免孤独感", target: "所有老人" }
]);

// 图表实例
let healthDistributionChart: echarts.ECharts | null = null;
let healthByAgeChart: echarts.ECharts | null = null;
let healthTrendChart: echarts.ECharts | null = null;

// 弹窗图表实例
const healthOverviewChart = ref<HTMLElement | null>(null);
const healthDistributionDetailChart = ref<HTMLElement | null>(null);
const healthByAgeDetailChart = ref<HTMLElement | null>(null);
const healthTrendDetailChart = ref<HTMLElement | null>(null);

// 加载数据
const loadData = async () => {
  try {
    // 加载健康状态分布
    const healthRes = await axios.get("/api/health/distribution");
    healthDistribution.value = healthRes.data;

    // 加载按年龄段分析的健康状态
    const healthByAgeRes = await axios.get("/api/health/distribution/age");
    healthByAge.value = healthByAgeRes.data;

    // 加载健康状态趋势
    const healthTrendRes = await axios.get("/api/health/trend");
    healthTrend.value = healthTrendRes.data;

    // 初始化图表
    initCharts();
  } catch (error) {
    console.error("加载数据失败:", error);
  }
};

// 初始化图表
const initCharts = () => {
  // 健康状态分布图表
  if (healthDistributionChart) {
    healthDistributionChart.dispose();
  }
  healthDistributionChart = echarts.init(
    document.getElementById("healthDistributionChart"),
  );
  healthDistributionChart.setOption({
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b}: {c} ({d}%)",
    },
    legend: {
      orient: "vertical",
      left: "left",
    },
    series: [
      {
        name: "健康状态",
        type: "pie",
        radius: "60%",
        data: [
          { value: healthDistribution.value.values?.[0] || 0, name: "良好" },
          { value: healthDistribution.value.values?.[1] || 0, name: "临界" },
          { value: healthDistribution.value.values?.[2] || 0, name: "高危" },
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
      },
    ],
  });

  // 按年龄段分析健康状态图表
  if (healthByAgeChart) {
    healthByAgeChart.dispose();
  }
  healthByAgeChart = echarts.init(document.getElementById("healthByAgeChart"));
  healthByAgeChart.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    legend: {
      data: healthByAge.value.datasets?.map((item: any) => item.name) || [],
    },
    xAxis: {
      type: "category",
      data: healthByAge.value.age_groups || [],
    },
    yAxis: {
      type: "value",
    },
    series:
      healthByAge.value.datasets?.map((item: any) => ({
        name: item.name,
        type: "bar",
        stack: "total",
        data: item.values,
      })) || [],
  });

  // 健康状态趋势图表
  if (healthTrendChart) {
    healthTrendChart.dispose();
  }
  healthTrendChart = echarts.init(document.getElementById("healthTrendChart"));
  healthTrendChart.setOption({
    tooltip: {
      trigger: "axis",
    },
    legend: {
      data: healthTrend.value.datasets?.map((item: any) => item.name) || [],
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: healthTrend.value.dates || [],
    },
    yAxis: {
      type: "value",
    },
    series:
      healthTrend.value.datasets?.map((item: any) => ({
        name: item.name,
        type: "line",
        data: item.values,
      })) || [],
  });

  // 响应式调整
  window.addEventListener("resize", () => {
    healthDistributionChart?.resize();
    healthByAgeChart?.resize();
    healthTrendChart?.resize();
  });
};

// 打开弹窗方法
const openHealthOverview = () => {
  dialogVisible.value.overview = true;
  setTimeout(() => {
    initHealthOverviewChart();
  }, 100);
};

const openHealthDistributionDetail = () => {
  dialogVisible.value.distribution = true;
  setTimeout(() => {
    initHealthDistributionDetailChart();
  }, 100);
};

const openHealthByAgeDetail = () => {
  dialogVisible.value.byAge = true;
  setTimeout(() => {
    initHealthByAgeDetailChart();
  }, 100);
};

const openHealthTrendDetail = () => {
  dialogVisible.value.trend = true;
  setTimeout(() => {
    initHealthTrendDetailChart();
  }, 100);
};

const openHealthRecommendations = () => {
  dialogVisible.value.recommendations = true;
};

// 初始化弹窗图表
const initHealthOverviewChart = () => {
  if (healthOverviewChart.value) {
    const chart = echarts.init(healthOverviewChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: healthOverviewData.value.map(item => item.indicator)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '数值',
          type: 'bar',
          data: healthOverviewData.value.map(item => item.value),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }
      ]
    });
  }
};

const initHealthDistributionDetailChart = () => {
  if (healthDistributionDetailChart.value) {
    const chart = echarts.init(healthDistributionDetailChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'pie',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '健康状态',
          type: 'pie',
          radius: '60%',
          data: healthDistributionDetailData.value.map(item => ({
            value: item.count,
            name: item.status
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    });
  }
};

const initHealthByAgeDetailChart = () => {
  if (healthByAgeDetailChart.value) {
    const chart = echarts.init(healthByAgeDetailChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['良好', '临界', '高危']
      },
      xAxis: {
        type: 'category',
        data: healthByAgeDetailData.value.map(item => item.age_group)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '良好',
          type: 'bar',
          stack: 'total',
          data: healthByAgeDetailData.value.map(item => item.good_count),
          itemStyle: { color: '#67C23A' }
        },
        {
          name: '临界',
          type: 'bar',
          stack: 'total',
          data: healthByAgeDetailData.value.map(item => item.critical_count),
          itemStyle: { color: '#E6A23C' }
        },
        {
          name: '高危',
          type: 'bar',
          stack: 'total',
          data: healthByAgeDetailData.value.map(item => item.high_risk_count),
          itemStyle: { color: '#F56C6C' }
        }
      ]
    });
  }
};

const initHealthTrendDetailChart = () => {
  if (healthTrendDetailChart.value) {
    const chart = echarts.init(healthTrendDetailChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['良好', '临界', '高危']
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: healthTrendDetailData.value.map(item => item.date)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '良好',
          type: 'line',
          data: healthTrendDetailData.value.map(item => item.good_count),
          itemStyle: { color: '#67C23A' }
        },
        {
          name: '临界',
          type: 'line',
          data: healthTrendDetailData.value.map(item => item.critical_count),
          itemStyle: { color: '#E6A23C' }
        },
        {
          name: '高危',
          type: 'line',
          data: healthTrendDetailData.value.map(item => item.high_risk_count),
          itemStyle: { color: '#F56C6C' }
        }
      ]
    });
  }
};

// 页面加载时初始化
onMounted(() => {
  loadData();
});
</script>

<style scoped>
.health-container {
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

.chart-container {
  height: 400px;
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.dialog-content {
  padding: 10px 0;
}

.dialog-content h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 1.1rem;
}

.chart-container-small {
  width: 100%;
}

.el-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.el-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
