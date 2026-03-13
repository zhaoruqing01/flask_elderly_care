<template>
  <el-container class="home-container">
    <el-header height="60px" class="header">
      <div class="header-left">
        <h2>养老服务数据分析系统</h2>
      </div>
      <div class="header-right">
        <el-tag type="primary">模拟数据</el-tag>
        <el-button size="small" @click="generateData" style="margin-left: 10px">
          <el-icon><Refresh /></el-icon>
          生成数据
        </el-button>
        <el-button
          size="small"
          type="primary"
          @click="cleanData"
          style="margin-left: 10px"
        >
          <el-icon><Tools /></el-icon>
          清洗数据
        </el-button>
        <el-button
          size="small"
          type="success"
          @click="trainModel"
          style="margin-left: 10px"
        >
          <el-icon><Cpu /></el-icon>
          训练模型
        </el-button>
      </div>
    </el-header>
    <el-main>
      <!-- 关键指标 -->
      <el-row :gutter="20" style="margin-bottom: 20px">
        <el-col :span="6">
          <el-card class="metric-card" @click="openSeniorDetail">
            <div class="metric-content">
              <div class="metric-label">老人总数</div>
              <div class="metric-value">{{ indicators.senior_count }}</div>
              <div class="metric-desc">人</div>
              <div class="metric-action">查看详情 <el-icon><ArrowRight /></el-icon></div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card" @click="openServiceDetail">
            <div class="metric-content">
              <div class="metric-label">服务总数</div>
              <div class="metric-value">{{ indicators.service_count }}</div>
              <div class="metric-desc">次</div>
              <div class="metric-action">查看详情 <el-icon><ArrowRight /></el-icon></div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card" @click="openSatisfactionDetail">
            <div class="metric-content">
              <div class="metric-label">平均满意度</div>
              <div class="metric-value">{{ indicators.avg_satisfaction }}</div>
              <div class="metric-desc">分</div>
              <div class="metric-action">查看详情 <el-icon><ArrowRight /></el-icon></div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card" @click="openHighRiskDetail">
            <div class="metric-content">
              <div class="metric-label">高危人数</div>
              <div class="metric-value">{{ indicators.high_risk_count }}</div>
              <div class="metric-desc">人</div>
              <div class="metric-action">查看详情 <el-icon><ArrowRight /></el-icon></div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card @click="openHealthDetail">
            <template #header>
              <div class="card-header">
                <span>健康状态分布</span>
                <el-button size="small" type="primary" @click.stop="openHealthDetail">
                  查看详情
                </el-button>
              </div>
            </template>
            <div id="healthDistributionChart" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card @click="openServiceFrequencyDetail">
            <template #header>
              <div class="card-header">
                <span>服务使用频次</span>
                <el-button size="small" type="primary" @click.stop="openServiceFrequencyDetail">
                  查看详情
                </el-button>
              </div>
            </template>
            <div id="serviceFrequencyChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>

    <!-- 弹窗组件 -->
    <!-- 老人总数详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.senior"
      title="老人总数详情"
      width="700px"
    >
      <div class="dialog-content">
        <h3>老人人口统计</h3>
        <el-table :data="seniorDetailData" style="width: 100%">
          <el-table-column prop="age_group" label="年龄组" width="120" />
          <el-table-column prop="count" label="人数" width="100" />
          <el-table-column prop="percentage" label="占比" width="100" />
          <el-table-column prop="male_count" label="男性" width="80" />
          <el-table-column prop="female_count" label="女性" width="80" />
          <el-table-column prop="note" label="备注" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="seniorAgeChart"></div>
      </div>
    </el-dialog>

    <!-- 服务总数详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.service"
      title="服务总数详情"
      width="700px"
    >
      <div class="dialog-content">
        <h3>服务类型统计</h3>
        <el-table :data="serviceDetailData" style="width: 100%">
          <el-table-column prop="type" label="服务类型" width="150" />
          <el-table-column prop="count" label="使用次数" width="100" />
          <el-table-column prop="percentage" label="占比" width="100" />
          <el-table-column prop="avg_duration" label="平均时长(分钟)" width="120" />
          <el-table-column prop="avg_satisfaction" label="平均满意度" width="120" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="serviceTypeChart"></div>
      </div>
    </el-dialog>

    <!-- 满意度详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.satisfaction"
      title="满意度详情"
      width="700px"
    >
      <div class="dialog-content">
        <h3>满意度分布</h3>
        <el-table :data="satisfactionDetailData" style="width: 100%">
          <el-table-column prop="score" label="评分" width="80" />
          <el-table-column prop="count" label="数量" width="100" />
          <el-table-column prop="percentage" label="占比" width="100" />
          <el-table-column prop="service_type" label="主要服务类型" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="satisfactionChart"></div>
      </div>
    </el-dialog>

    <!-- 高危人群详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.highRisk"
      title="高危人群详情"
      width="700px"
    >
      <div class="dialog-content">
        <h3>高危老人统计</h3>
        <el-table :data="highRiskDetailData" style="width: 100%">
          <el-table-column prop="risk_type" label="风险类型" width="150" />
          <el-table-column prop="count" label="人数" width="100" />
          <el-table-column prop="percentage" label="占比" width="100" />
          <el-table-column prop="avg_age" label="平均年龄" width="100" />
          <el-table-column prop="suggestion" label="建议" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="highRiskChart"></div>
      </div>
    </el-dialog>

    <!-- 健康状态详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.health"
      title="健康状态详情"
      width="700px"
    >
      <div class="dialog-content">
        <h3>健康状态详细分布</h3>
        <el-table :data="healthDetailData" style="width: 100%">
          <el-table-column prop="status" label="健康状态" width="120" />
          <el-table-column prop="count" label="人数" width="100" />
          <el-table-column prop="percentage" label="占比" width="100" />
          <el-table-column prop="avg_age" label="平均年龄" width="100" />
          <el-table-column prop="care_level" label="护理等级" width="100" />
        </el-table>
        <div class="chart-container-small" style="height: 300px; margin-top: 20px" ref="healthDetailChart"></div>
      </div>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { Cpu, Refresh, Tools, ArrowRight } from "@element-plus/icons-vue";
import axios from "axios";
import * as echarts from "echarts";
import { ElMessage } from "element-plus";
import { onMounted, ref, watch } from "vue";

// 类型定义
interface HealthDistribution {
  values: number[];
}

interface ServiceFrequency {
  types: string[];
  counts: number[];
}

// 响应式数据
const indicators = ref({
  senior_count: 0,
  service_count: 0,
  avg_satisfaction: 0,
  high_risk_count: 0,
});

const healthDistribution = ref<HealthDistribution>({ values: [] });
const serviceFrequency = ref<ServiceFrequency>({ types: [], counts: [] });

// 弹窗状态
const dialogVisible = ref({
  senior: false,
  service: false,
  satisfaction: false,
  highRisk: false,
  health: false
});

// 详情数据
const seniorDetailData = ref([
  { age_group: "60-69岁", count: 120, percentage: "30%", male_count: 55, female_count: 65, note: "低龄老人，健康状况良好" },
  { age_group: "70-79岁", count: 150, percentage: "37.5%", male_count: 70, female_count: 80, note: "中龄老人，需要一定关注" },
  { age_group: "80-89岁", count: 90, percentage: "22.5%", male_count: 40, female_count: 50, note: "高龄老人，需要较多照护" },
  { age_group: "90岁以上", count: 40, percentage: "10%", male_count: 15, female_count: 25, note: "超高龄老人，需要全面照护" }
]);

const serviceDetailData = ref([
  { type: "助餐服务", count: 350, percentage: "35%", avg_duration: 30, avg_satisfaction: 4.8 },
  { type: "助医服务", count: 250, percentage: "25%", avg_duration: 45, avg_satisfaction: 4.9 },
  { type: "助洁服务", count: 200, percentage: "20%", avg_duration: 60, avg_satisfaction: 4.7 },
  { type: "助行服务", count: 150, percentage: "15%", avg_duration: 30, avg_satisfaction: 4.6 },
  { type: "其他服务", count: 50, percentage: "5%", avg_duration: 40, avg_satisfaction: 4.5 }
]);

const satisfactionDetailData = ref([
  { score: 5, count: 650, percentage: "65%", service_type: "助医、助餐" },
  { score: 4, count: 250, percentage: "25%", service_type: "助洁、助行" },
  { score: 3, count: 80, percentage: "8%", service_type: "其他服务" },
  { score: 2, count: 15, percentage: "1.5%", service_type: "个别服务" },
  { score: 1, count: 5, percentage: "0.5%", service_type: "个别服务" }
]);

const highRiskDetailData = ref([
  { risk_type: "高血压", count: 45, percentage: "45%", avg_age: 78, suggestion: "定期监测血压，遵医嘱服药" },
  { risk_type: "糖尿病", count: 25, percentage: "25%", avg_age: 75, suggestion: "控制饮食，定期监测血糖" },
  { risk_type: "心脑血管疾病", count: 15, percentage: "15%", avg_age: 80, suggestion: "定期体检，避免剧烈运动" },
  { risk_type: "跌倒风险", count: 10, percentage: "10%", avg_age: 82, suggestion: "改善居住环境，增加辅助设施" },
  { risk_type: "其他疾病", count: 5, percentage: "5%", avg_age: 76, suggestion: "根据具体病情制定照护方案" }
]);

const healthDetailData = ref([
  { status: "良好", count: 280, percentage: "70%", avg_age: 72, care_level: "自理" },
  { status: "临界", count: 80, percentage: "20%", avg_age: 78, care_level: "半自理" },
  { status: "高危", count: 40, percentage: "10%", avg_age: 82, care_level: "完全护理" }
]);

// 图表实例
let healthChart: echarts.ECharts | null = null;
let serviceChart: echarts.ECharts | null = null;

// 弹窗图表实例
const seniorAgeChart = ref<HTMLElement | null>(null);
const serviceTypeChart = ref<HTMLElement | null>(null);
const satisfactionChart = ref<HTMLElement | null>(null);
const highRiskChart = ref<HTMLElement | null>(null);
const healthDetailChart = ref<HTMLElement | null>(null);

// 加载数据
const loadData = async () => {
  try {
    // 加载关键指标
    const indicatorsRes = await axios.get("/api/key/indicators");
    indicators.value = indicatorsRes.data;
    console.log("关键指标数据:", indicators.value);

    // 加载健康状态分布
    const healthRes = await axios.get("/api/health/distribution");
    healthDistribution.value = healthRes.data;
    console.log("健康状态分布数据:", healthDistribution.value);

    // 加载服务使用频次
    const serviceRes = await axios.get("/api/service/frequency");
    serviceFrequency.value = serviceRes.data;
    console.log("服务使用频次数据:", serviceFrequency.value);

    // 初始化图表
    initCharts();
  } catch (error) {
    console.error("加载数据失败:", error);
  }
};

// 初始化图表
const initCharts = () => {
  // 健康状态分布图表
  if (healthChart) {
    healthChart.dispose();
  }
  healthChart = echarts.init(
    document.getElementById("healthDistributionChart"),
  );
  healthChart.setOption({
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

  // 服务使用频次图表
  if (serviceChart) {
    serviceChart.dispose();
  }
  serviceChart = echarts.init(document.getElementById("serviceFrequencyChart"));
  serviceChart.setOption({
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

  // 响应式调整
  window.addEventListener("resize", () => {
    healthChart?.resize();
    serviceChart?.resize();
  });
};

// 生成数据
const generateData = async () => {
  if (!confirm("确定要重新生成模拟数据吗？这将清空现有数据！")) return;

  try {
    const response = await axios.post("/api/generate");
    if (response.data.error) {
      ElMessage.error("生成失败：" + response.data.error);
    } else {
      ElMessage.success(response.data.message);
      // 重新加载数据
      setTimeout(loadData, 1000);
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
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
      // 重新加载数据
      setTimeout(loadData, 1000);
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
  }
};

// 训练模型
const trainModel = async () => {
  if (!confirm("确定要训练模型吗？")) return;

  try {
    const response = await axios.post("/api/train");
    if (response.data.error) {
      ElMessage.error("训练失败：" + response.data.error);
    } else {
      ElMessage.success(
        `模型训练完成！R² 评分: ${response.data.r2_score}，MAE: ${response.data.mae}，RMSE: ${response.data.rmse}`,
      );
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
  }
};

// 打开弹窗方法
const openSeniorDetail = () => {
  dialogVisible.value.senior = true;
  setTimeout(() => {
    initSeniorAgeChart();
  }, 100);
};

const openServiceDetail = () => {
  dialogVisible.value.service = true;
  setTimeout(() => {
    initServiceTypeChart();
  }, 100);
};

const openSatisfactionDetail = () => {
  dialogVisible.value.satisfaction = true;
  setTimeout(() => {
    initSatisfactionChart();
  }, 100);
};

const openHighRiskDetail = () => {
  dialogVisible.value.highRisk = true;
  setTimeout(() => {
    initHighRiskChart();
  }, 100);
};

const openHealthDetail = () => {
  dialogVisible.value.health = true;
  setTimeout(() => {
    initHealthDetailChart();
  }, 100);
};

const openServiceFrequencyDetail = () => {
  openServiceDetail();
};

// 初始化弹窗图表
const initSeniorAgeChart = () => {
  if (seniorAgeChart.value) {
    const chart = echarts.init(seniorAgeChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: seniorDetailData.value.map(item => item.age_group)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '人数',
          type: 'bar',
          data: seniorDetailData.value.map(item => item.count),
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

const initServiceTypeChart = () => {
  if (serviceTypeChart.value) {
    const chart = echarts.init(serviceTypeChart.value);
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
          name: '服务类型',
          type: 'pie',
          radius: '60%',
          data: serviceDetailData.value.map(item => ({
            value: item.count,
            name: item.type
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

const initSatisfactionChart = () => {
  if (satisfactionChart.value) {
    const chart = echarts.init(satisfactionChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: satisfactionDetailData.value.map(item => item.score + '分')
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '数量',
          type: 'bar',
          data: satisfactionDetailData.value.map(item => item.count),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#87ceeb' },
              { offset: 1, color: '#00bfff' }
            ])
          }
        }
      ]
    });
  }
};

const initHighRiskChart = () => {
  if (highRiskChart.value) {
    const chart = echarts.init(highRiskChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: highRiskDetailData.value.map(item => item.risk_type),
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '人数',
          type: 'bar',
          data: highRiskDetailData.value.map(item => item.count),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#ff7f50' },
              { offset: 1, color: '#ff4500' }
            ])
          }
        }
      ]
    });
  }
};

const initHealthDetailChart = () => {
  if (healthDetailChart.value) {
    const chart = echarts.init(healthDetailChart.value);
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
          data: healthDetailData.value.map(item => ({
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

// 页面加载时初始化
onMounted(() => {
  console.log("页面加载，开始加载数据");
  loadData();
});
</script>

<style scoped>
.home-container {
  height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.header-left h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #0066cc;
}

.header-right {
  display: flex;
  align-items: center;
}

.metric-card {
  border-left: 4px solid #0066cc;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-content {
  text-align: center;
  padding: 20px 0;
}

.metric-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.metric-desc {
  font-size: 0.8rem;
  color: #999;
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

.metric-action {
  margin-top: 10px;
  font-size: 0.8rem;
  color: #0066cc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s ease;
}

.metric-action:hover {
  color: #004080;
}

.metric-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
  transition: all 0.3s ease;
}

.el-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
