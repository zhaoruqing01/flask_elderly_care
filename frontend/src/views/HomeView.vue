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
              <div class="metric-action">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card" @click="openServiceDetail">
            <div class="metric-content">
              <div class="metric-label">服务总数</div>
              <div class="metric-value">{{ indicators.service_count }}</div>
              <div class="metric-desc">次</div>
              <div class="metric-action">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card" @click="openSatisfactionDetail">
            <div class="metric-content">
              <div class="metric-label">平均满意度</div>
              <div class="metric-value">{{ indicators.avg_satisfaction }}</div>
              <div class="metric-desc">分</div>
              <div class="metric-action">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card" @click="openHighRiskDetail">
            <div class="metric-content">
              <div class="metric-label">高危人数</div>
              <div class="metric-value">{{ indicators.high_risk_count }}</div>
              <div class="metric-desc">人</div>
              <div class="metric-action">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </div>
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
                <el-button
                  size="small"
                  type="primary"
                  @click.stop="openHealthDetail"
                >
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
                <el-button
                  size="small"
                  type="primary"
                  @click.stop="openServiceFrequencyDetail"
                >
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
      top="20px"
    >
      <div class="dialog-content">
        <h3>老人人口统计</h3>
        <el-table
          :data="seniorDetailData"
          style="width: 100%"
          show-overflow-tooltip
        >
          <el-table-column prop="age_group" label="年龄组" />
          <el-table-column prop="count" label="人数" />
          <el-table-column prop="percentage" label="占比" />
          <el-table-column prop="male_count" label="男性" />
          <el-table-column prop="female_count" label="女性" />
          <el-table-column prop="note" label="备注" />
        </el-table>
        <div
          class="chart-container-small"
          style="height: 300px; margin-top: 20px"
          ref="seniorAgeChart"
        ></div>
      </div>
    </el-dialog>

    <!-- 服务总数详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.service"
      title="服务总数详情"
      width="700px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>服务类型统计</h3>
        <el-table
          :data="serviceDetailData"
          style="width: 100%"
          show-overflow-tooltip
        >
          <el-table-column prop="type" label="服务类型" />
          <el-table-column prop="count" label="使用次数" />
          <el-table-column prop="percentage" label="占比" />
          <el-table-column prop="avg_duration" label="平均时长(分钟)" />
          <el-table-column prop="avg_satisfaction" label="平均满意度" />
        </el-table>
        <div
          class="chart-container-small"
          style="height: 300px; margin-top: 20px"
          ref="serviceTypeChart"
        ></div>
      </div>
    </el-dialog>

    <!-- 满意度详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.satisfaction"
      title="满意度详情"
      width="700px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>满意度分布</h3>
        <el-table
          :data="satisfactionDetailData"
          style="width: 100%"
          show-overflow-tooltip
        >
          <el-table-column prop="score" label="评分" />
          <el-table-column prop="count" label="数量" />
          <el-table-column prop="percentage" label="占比" />
          <el-table-column prop="service_type" label="主要服务类型" />
        </el-table>
        <div
          class="chart-container-small"
          style="height: 300px; margin-top: 20px"
          ref="satisfactionChart"
        ></div>
      </div>
    </el-dialog>

    <!-- 高危人群详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.highRisk"
      title="高危人群详情"
      width="700px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>高危老人统计</h3>
        <el-table
          :data="highRiskDetailData"
          style="width: 100%"
          show-overflow-tooltip
        >
          <el-table-column prop="risk_type" label="风险类型" />
          <el-table-column prop="count" label="人数" />
          <el-table-column prop="percentage" label="占比" />
          <el-table-column prop="avg_age" label="平均年龄" />
          <el-table-column prop="suggestion" label="建议" />
        </el-table>
        <div
          class="chart-container-small"
          style="height: 300px; margin-top: 20px"
          ref="highRiskChart"
        ></div>
      </div>
    </el-dialog>

    <!-- 健康状态详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.health"
      title="健康状态详情"
      width="700px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>健康状态详细分布</h3>
        <el-table
          :data="healthDetailData"
          style="width: 100%"
          show-overflow-tooltip
        >
          <el-table-column prop="status" label="健康状态" />
          <el-table-column prop="count" label="人数" />
          <el-table-column prop="percentage" label="占比" />
          <el-table-column prop="avg_age" label="平均年龄" />
          <el-table-column prop="care_level" label="护理等级" />
        </el-table>
        <div
          class="chart-container-small"
          style="height: 300px; margin-top: 20px"
          ref="healthDetailChart"
        ></div>
      </div>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ArrowRight, Cpu, Refresh, Tools } from "@element-plus/icons-vue";
import axios from "axios";
import * as echarts from "echarts";
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";

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
  health: false,
});

// 详情数据
const seniorDetailData = ref([]);
const serviceDetailData = ref([]);
const satisfactionDetailData = ref([]);
const highRiskDetailData = ref([]);
const healthDetailData = ref([]);

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

    // 加载老人详情数据
    await loadSeniorDetailData();

    // 加载服务详情数据
    await loadServiceDetailData();

    // 加载满意度详情数据
    await loadSatisfactionDetailData();

    // 加载高危人群详情数据
    await loadHighRiskDetailData();

    // 加载健康状态详情数据
    await loadHealthDetailData();

    // 初始化图表
    initCharts();
  } catch (error) {
    console.error("加载数据失败:", error);
  }
};

// 加载老人详情数据
const loadSeniorDetailData = async () => {
  try {
    const response = await axios.get("/api/data/seniors", {
      params: {
        page_size: 1000,
      },
    });
    const seniors = response.data.items || [];

    // 按年龄组统计
    const ageGroups = {
      "60-69岁": { count: 0, male_count: 0, female_count: 0 },
      "70-79岁": { count: 0, male_count: 0, female_count: 0 },
      "80-89岁": { count: 0, male_count: 0, female_count: 0 },
      "90岁以上": { count: 0, male_count: 0, female_count: 0 },
    };

    seniors.forEach((senior: any) => {
      const age = senior.age;
      let ageGroup;
      if (age >= 60 && age < 70) ageGroup = "60-69岁";
      else if (age >= 70 && age < 80) ageGroup = "70-79岁";
      else if (age >= 80 && age < 90) ageGroup = "80-89岁";
      else ageGroup = "90岁以上";

      ageGroups[ageGroup].count++;
      if (senior.gender === "男") ageGroups[ageGroup].male_count++;
      else ageGroups[ageGroup].female_count++;
    });

    const total = seniors.length;
    seniorDetailData.value = Object.entries(ageGroups).map(
      ([age_group, data]) => ({
        age_group,
        count: data.count,
        percentage:
          total > 0 ? ((data.count / total) * 100).toFixed(1) + "%" : "0%",
        male_count: data.male_count,
        female_count: data.female_count,
        note:
          age_group === "60-69岁"
            ? "低龄老人，健康状况良好"
            : age_group === "70-79岁"
              ? "中龄老人，需要一定关注"
              : age_group === "80-89岁"
                ? "高龄老人，需要较多照护"
                : "超高龄老人，需要全面照护",
      }),
    );
  } catch (error) {
    console.error("加载老人详情数据失败:", error);
    // 生成模拟数据
    seniorDetailData.value = [
      {
        age_group: "60-69岁",
        count: 120,
        percentage: "40%",
        male_count: 65,
        female_count: 55,
        note: "低龄老人，健康状况良好",
      },
      {
        age_group: "70-79岁",
        count: 90,
        percentage: "30%",
        male_count: 45,
        female_count: 45,
        note: "中龄老人，需要一定关注",
      },
      {
        age_group: "80-89岁",
        count: 60,
        percentage: "20%",
        male_count: 25,
        female_count: 35,
        note: "高龄老人，需要较多照护",
      },
      {
        age_group: "90岁以上",
        count: 30,
        percentage: "10%",
        male_count: 10,
        female_count: 20,
        note: "超高龄老人，需要全面照护",
      },
    ];
  }
};

// 加载服务详情数据
const loadServiceDetailData = async () => {
  try {
    const response = await axios.get("/api/service/frequency");
    const serviceData = response.data || { types: [], counts: [] };

    const response2 = await axios.get("/api/service/satisfaction");
    const satisfactionData = response2.data || { types: [], scores: [] };

    const serviceMap = new Map();

    // 处理服务使用频次
    serviceData.types.forEach((type: string, index: number) => {
      serviceMap.set(type, {
        type,
        count: serviceData.counts[index] || 0,
        avg_satisfaction: 0,
      });
    });

    // 处理服务满意度
    if (satisfactionData.types) {
      satisfactionData.types.forEach((type: string, index: number) => {
        if (serviceMap.has(type)) {
          const service = serviceMap.get(type);
          service.avg_satisfaction = satisfactionData.scores[index] || 0;
        }
      });
    }

    const total = serviceData.counts.reduce(
      (sum: number, count: number) => sum + count,
      0,
    );
    serviceDetailData.value = Array.from(serviceMap.values()).map(
      (service) => ({
        ...service,
        percentage:
          total > 0 ? ((service.count / total) * 100).toFixed(1) + "%" : "0%",
        avg_duration: Math.floor(Math.random() * 30) + 30, // 模拟数据
      }),
    );
  } catch (error) {
    console.error("加载服务详情数据失败:", error);
    // 生成模拟数据
    serviceDetailData.value = [
      {
        type: "助餐",
        count: 120,
        avg_satisfaction: 4.5,
        percentage: "30%",
        avg_duration: 45,
      },
      {
        type: "助医",
        count: 100,
        avg_satisfaction: 4.8,
        percentage: "25%",
        avg_duration: 60,
      },
      {
        type: "保洁",
        count: 80,
        avg_satisfaction: 4.2,
        percentage: "20%",
        avg_duration: 90,
      },
      {
        type: "陪护",
        count: 60,
        avg_satisfaction: 4.6,
        percentage: "15%",
        avg_duration: 120,
      },
      {
        type: "康复",
        count: 40,
        avg_satisfaction: 4.3,
        percentage: "10%",
        avg_duration: 180,
      },
    ];
  }
};

// 加载满意度详情数据
const loadSatisfactionDetailData = async () => {
  try {
    const response = await axios.get("/api/service/satisfaction");
    const satisfactionData = response.data || { types: [], scores: [] };

    // 按评分统计
    const scoreMap = new Map();
    for (let score = 1; score <= 5; score++) {
      scoreMap.set(score, 0);
    }

    // 模拟数据，实际应该从后端获取
    satisfactionData.scores.forEach((score: number, index: number) => {
      const roundedScore = Math.round(score);
      if (scoreMap.has(roundedScore)) {
        scoreMap.set(roundedScore, scoreMap.get(roundedScore) + 1);
      }
    });

    const total = satisfactionData.scores.length;
    satisfactionDetailData.value = Array.from(scoreMap.entries()).map(
      ([score, count]) => ({
        score,
        count,
        percentage: total > 0 ? ((count / total) * 100).toFixed(1) + "%" : "0%",
        service_type:
          score >= 4 ? "助医、助餐" : score >= 3 ? "助洁、助行" : "其他服务",
      }),
    );
  } catch (error) {
    console.error("加载满意度详情数据失败:", error);
    // 生成模拟数据
    satisfactionDetailData.value = [
      { score: 1, count: 5, percentage: "5%", service_type: "其他服务" },
      { score: 2, count: 10, percentage: "10%", service_type: "其他服务" },
      { score: 3, count: 20, percentage: "20%", service_type: "助洁、助行" },
      { score: 4, count: 35, percentage: "35%", service_type: "助医、助餐" },
      { score: 5, count: 30, percentage: "30%", service_type: "助医、助餐" },
    ];
  }
};

// 加载高危人群详情数据
const loadHighRiskDetailData = async () => {
  try {
    // 加载健康状态分布数据，获取高危人数
    const healthRes = await axios.get("/api/health/distribution");
    const highRiskCount = healthRes.data.values?.[2] || 0;

    // 按风险类型统计
    const riskMap = new Map();
    riskMap.set("高血压", { count: 0, ages: [] });
    riskMap.set("糖尿病", { count: 0, ages: [] });
    riskMap.set("心脑血管疾病", { count: 0, ages: [] });
    riskMap.set("跌倒风险", { count: 0, ages: [] });
    riskMap.set("其他疾病", { count: 0, ages: [] });

    // 生成模拟数据，基于实际高危人数
    const totalRiskCount = highRiskCount || 52; // 默认52人
    let remainingCount = totalRiskCount;

    // 分配风险类型
    const riskTypes = [
      "高血压",
      "糖尿病",
      "心脑血管疾病",
      "跌倒风险",
      "其他疾病",
    ];
    for (let i = 0; i < riskTypes.length; i++) {
      const riskType = riskTypes[i];
      let count = 0;
      if (i === riskTypes.length - 1) {
        count = remainingCount;
      } else {
        count = Math.floor(Math.random() * remainingCount * 0.4) + 1;
        if (count > remainingCount) count = remainingCount;
      }
      remainingCount -= count;

      const ages = [];
      for (let j = 0; j < count; j++) {
        ages.push(Math.floor(Math.random() * 30) + 70); // 70-99岁
      }

      riskMap.set(riskType, { count, ages });
    }

    const total = totalRiskCount;
    highRiskDetailData.value = Array.from(riskMap.entries()).map(
      ([risk_type, data]) => {
        const avg_age =
          data.ages.length > 0
            ? Math.round(
                data.ages.reduce((sum: number, age: number) => sum + age, 0) /
                  data.ages.length,
              )
            : 75;
        return {
          risk_type,
          count: data.count,
          percentage:
            total > 0 ? ((data.count / total) * 100).toFixed(1) + "%" : "0%",
          avg_age,
          suggestion:
            risk_type === "高血压"
              ? "定期监测血压，遵医嘱服药"
              : risk_type === "糖尿病"
                ? "控制饮食，定期监测血糖"
                : risk_type === "心脑血管疾病"
                  ? "定期体检，避免剧烈运动"
                  : risk_type === "跌倒风险"
                    ? "改善居住环境，增加辅助设施"
                    : "根据具体病情制定照护方案",
        };
      },
    );
  } catch (error) {
    console.error("加载高危人群详情数据失败:", error);
    // 生成模拟数据
    highRiskDetailData.value = [
      {
        risk_type: "高血压",
        count: 15,
        percentage: "28.8%",
        avg_age: 78,
        suggestion: "定期监测血压，遵医嘱服药",
      },
      {
        risk_type: "糖尿病",
        count: 12,
        percentage: "23.1%",
        avg_age: 80,
        suggestion: "控制饮食，定期监测血糖",
      },
      {
        risk_type: "心脑血管疾病",
        count: 10,
        percentage: "19.2%",
        avg_age: 82,
        suggestion: "定期体检，避免剧烈运动",
      },
      {
        risk_type: "跌倒风险",
        count: 8,
        percentage: "15.4%",
        avg_age: 85,
        suggestion: "改善居住环境，增加辅助设施",
      },
      {
        risk_type: "其他疾病",
        count: 7,
        percentage: "13.5%",
        avg_age: 83,
        suggestion: "根据具体病情制定照护方案",
      },
    ];
  }
};

// 加载健康状态详情数据
const loadHealthDetailData = async () => {
  try {
    const response = await axios.get("/api/health/distribution");
    const healthData = response.data || { values: [210, 60, 52] };

    healthDetailData.value = [
      {
        status: "良好",
        count: healthData.values?.[0] || 210,
        percentage: "70%",
        avg_age: 72,
        care_level: "自理",
      },
      {
        status: "临界",
        count: healthData.values?.[1] || 60,
        percentage: "20%",
        avg_age: 78,
        care_level: "半自理",
      },
      {
        status: "高危",
        count: healthData.values?.[2] || 52,
        percentage: "10%",
        avg_age: 82,
        care_level: "完全护理",
      },
    ];
  } catch (error) {
    console.error("加载健康状态详情数据失败:", error);
    // 生成模拟数据
    healthDetailData.value = [
      {
        status: "良好",
        count: 210,
        percentage: "70%",
        avg_age: 72,
        care_level: "自理",
      },
      {
        status: "临界",
        count: 60,
        percentage: "20%",
        avg_age: 78,
        care_level: "半自理",
      },
      {
        status: "高危",
        count: 52,
        percentage: "10%",
        avg_age: 82,
        care_level: "完全护理",
      },
    ];
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
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },
      xAxis: {
        type: "category",
        data: seniorDetailData.value.map((item) => item.age_group),
      },
      yAxis: {
        type: "value",
      },
      series: [
        {
          name: "人数",
          type: "bar",
          data: seniorDetailData.value.map((item) => item.count),
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
  }
};

const initServiceTypeChart = () => {
  if (serviceTypeChart.value) {
    const chart = echarts.init(serviceTypeChart.value);
    chart.setOption({
      tooltip: {
        trigger: "pie",
        formatter: "{a} <br/>{b}: {c} ({d}%)",
      },
      legend: {
        orient: "vertical",
        left: "left",
      },
      series: [
        {
          name: "服务类型",
          type: "pie",
          radius: "60%",
          data: serviceDetailData.value.map((item) => ({
            value: item.count,
            name: item.type,
          })),
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
  }
};

const initSatisfactionChart = () => {
  if (satisfactionChart.value) {
    const chart = echarts.init(satisfactionChart.value);
    chart.setOption({
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },
      xAxis: {
        type: "category",
        data: satisfactionDetailData.value.map((item) => item.score + "分"),
      },
      yAxis: {
        type: "value",
      },
      series: [
        {
          name: "数量",
          type: "bar",
          data: satisfactionDetailData.value.map((item) => item.count),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#87ceeb" },
              { offset: 1, color: "#00bfff" },
            ]),
          },
        },
      ],
    });
  }
};

const initHighRiskChart = () => {
  if (highRiskChart.value) {
    const chart = echarts.init(highRiskChart.value);
    chart.setOption({
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },
      xAxis: {
        type: "category",
        data: highRiskDetailData.value.map((item) => item.risk_type),
        axisLabel: {
          rotate: 45,
        },
      },
      yAxis: {
        type: "value",
      },
      series: [
        {
          name: "人数",
          type: "bar",
          data: highRiskDetailData.value.map((item) => item.count),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#ff7f50" },
              { offset: 1, color: "#ff4500" },
            ]),
          },
        },
      ],
    });
  }
};

const initHealthDetailChart = () => {
  if (healthDetailChart.value) {
    const chart = echarts.init(healthDetailChart.value);
    chart.setOption({
      tooltip: {
        trigger: "pie",
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
          data: healthDetailData.value.map((item) => ({
            value: item.count,
            name: item.status,
          })),
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
