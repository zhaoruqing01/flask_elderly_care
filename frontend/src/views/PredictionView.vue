<template>
  <el-container class="prediction-container">
    <el-header height="60px" class="header">
      <div class="header-left">
        <h2>需求预测</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="exportData" icon="Download">
          导出数据
        </el-button>
      </div>
    </el-header>
    <el-main>
      <!-- 预测控制栏 -->
      <el-card style="margin-bottom: 20px">
        <div class="control-panel">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-select
                v-model="selectedCommunity"
                placeholder="选择社区"
                style="width: 100%"
              >
                <el-option
                  v-for="community in communities"
                  :key="community"
                  :label="community"
                  :value="community"
                />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select
                v-model="selectedService"
                placeholder="选择服务"
                style="width: 100%"
              >
                <el-option
                  v-for="service in services"
                  :key="service"
                  :label="service"
                  :value="service"
                />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select
                v-model="predictionDays"
                placeholder="预测天数"
                style="width: 100%"
              >
                <el-option label="7天" value="7" />
                <el-option label="14天" value="14" />
                <el-option label="30天" value="30" />
                <el-option label="90天" value="90" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select
                v-model="predictionModel"
                placeholder="预测模型"
                style="width: 100%"
              >
                <el-option label="随机森林" value="random_forest" />
                <el-option label="梯度提升" value="gradient_boosting" />
                <el-option label="XGBoost" value="xgboost" />
                <el-option label="集成模型" value="ensemble" />
              </el-select>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 10px">
            <el-col :span="6">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 100%"
              />
            </el-col>
            <el-col :span="6">
              <el-select
                v-model="seasonalAnalysis"
                placeholder="季节性分析"
                style="width: 100%"
              >
                <el-option label="无" value="none" />
                <el-option label="周度" value="weekly" />
                <el-option label="月度" value="monthly" />
                <el-option label="季度" value="quarterly" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select
                v-model="confidenceLevel"
                placeholder="置信度"
                style="width: 100%"
              >
                <el-option label="80%" value="0.8" />
                <el-option label="90%" value="0.9" />
                <el-option label="95%" value="0.95" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-button
                type="primary"
                @click="refreshData"
                style="width: 100%"
              >
                刷新数据
              </el-button>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 预测趋势 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>服务需求预测趋势</span>
            <div class="card-header-actions">
              <el-switch
                v-model="showConfidenceInterval"
                active-text="显示置信区间"
              />
            </div>
          </div>
        </template>
        <div id="predictionTrendChart" class="chart-container"></div>
      </el-card>

      <!-- 多维度分析 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>多维度分析</span>
            <div class="card-header-actions">
              <el-select
                v-model="analysisDimension"
                placeholder="分析维度"
                style="width: 150px"
              >
                <el-option label="社区" value="community" />
                <el-option label="服务类型" value="service" />
                <el-option label="时间" value="time" />
              </el-select>
            </div>
          </div>
        </template>
        <div class="analysis-grid">
          <div class="analysis-item">
            <h4>需求分布</h4>
            <div id="demandDistributionChart" class="sub-chart-container"></div>
          </div>
          <div class="analysis-item">
            <h4>趋势对比</h4>
            <div id="trendComparisonChart" class="sub-chart-container"></div>
          </div>
        </div>
      </el-card>

      <!-- 资源配置建议 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>资源配置建议</span>
            <div class="card-header-actions">
              <el-select
                v-model="recommendationFilter"
                placeholder="按优先级筛选"
                style="width: 120px"
              >
                <el-option label="全部" value="all" />
                <el-option label="高" value="高" />
                <el-option label="中" value="中" />
                <el-option label="低" value="低" />
              </el-select>
            </div>
          </div>
        </template>
        <el-table :data="filteredRecommendations" style="width: 100%">
          <el-table-column prop="community" label="社区" width="120" />
          <el-table-column prop="service" label="服务类型" width="120" />
          <el-table-column
            prop="predicted_demand"
            label="预测需求"
            width="120"
          />
          <el-table-column prop="daily_avg" label="日均需求" width="120" />
          <el-table-column prop="staff_needed" label="所需人员" width="100" />
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="scope">
              <el-tag :type="getPriorityType(scope.row.priority)">
                {{ scope.row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="suggestion" label="建议" />
          <el-table-column prop="confidence" label="置信度" width="100">
            <template #default="scope">
              <el-progress
                :percentage="scope.row.confidence || 0"
                :format="() => `${scope.row.confidence || 0}%`"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 模型评估与对比 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>模型评估与对比</span>
            <div class="card-header-actions">
              <el-button size="small" @click="trainModel" icon="Refresh">
                重新训练
              </el-button>
            </div>
          </div>
        </template>
        <div class="model-comparison">
          <div class="metrics-grid">
            <div class="metric-item">
              <div class="metric-label">R² 评分</div>
              <div class="metric-value">{{ modelMetrics.r2_score || 0 }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">平均绝对误差</div>
              <div class="metric-value">{{ modelMetrics.mae || 0 }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">均方根误差</div>
              <div class="metric-value">{{ modelMetrics.rmse || 0 }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">平均绝对百分比误差</div>
              <div class="metric-value">{{ modelMetrics.mape || 0 }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">训练样本数</div>
              <div class="metric-value">
                {{ modelMetrics.train_samples || 0 }}
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-label">测试样本数</div>
              <div class="metric-value">
                {{ modelMetrics.test_samples || 0 }}
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-label">交叉验证R²</div>
              <div class="metric-value">{{ modelMetrics.cv_mean_r2 || 0 }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">训练时间</div>
              <div class="metric-value">
                {{ modelMetrics.trained_at || "-" }}
              </div>
            </div>
          </div>
          <div
            id="modelComparisonChart"
            class="chart-container"
            style="height: 300px; margin-top: 20px"
          ></div>
        </div>
      </el-card>

      <!-- 异常检测 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>异常检测</span>
            <div class="card-header-actions">
              <el-button
                size="small"
                @click="detectAnomalies"
                icon="WarningFilled"
              >
                检测异常
              </el-button>
              <el-button
                size="small"
                type="primary"
                @click.stop="openAnomalyDetail"
              >
                查看详情
              </el-button>
            </div>
          </div>
        </template>
        <div v-if="anomalies.length > 0">
          <el-alert
            v-for="(anomaly, index) in anomalies"
            :key="index"
            :title="`异常: ${anomaly.description}`"
            :type="
              anomaly.severity === '高'
                ? 'error'
                : anomaly.severity === '中'
                  ? 'warning'
                  : 'info'
            "
            show-icon
            :closable="false"
            style="margin-bottom: 10px"
          >
            <template #default>
              <div>
                <p>{{ anomaly.details }}</p>
                <p><strong>建议:</strong> {{ anomaly.suggestion }}</p>
              </div>
            </template>
          </el-alert>
        </div>
        <div v-else class="no-anomalies">
          <el-empty description="未检测到异常" />
        </div>
      </el-card>
    </el-main>

    <!-- 弹窗组件 -->
    <!-- 预测趋势详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.predictionDetail"
      title="预测趋势详情"
      width="800px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>详细预测数据</h3>
        <el-table :data="predictionDetailData" style="width: 100%">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="value" label="预测值" width="100" />
          <el-table-column prop="lower_bound" label="下限" width="100" />
          <el-table-column prop="upper_bound" label="上限" width="100" />
          <el-table-column prop="confidence" label="置信度" width="100" />
          <el-table-column prop="trend" label="趋势" />
        </el-table>
        <div
          class="chart-container-small"
          style="height: 400px; margin-top: 20px"
          ref="predictionDetailChart"
        ></div>
      </div>
    </el-dialog>

    <!-- 资源配置详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.resourceDetail"
      title="资源配置详情"
      width="800px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>详细资源配置建议</h3>
        <el-table :data="resourceDetailData" style="width: 100%">
          <el-table-column prop="community" label="社区" width="120" />
          <el-table-column prop="service" label="服务类型" width="120" />
          <el-table-column
            prop="predicted_demand"
            label="预测需求"
            width="120"
          />
          <el-table-column prop="current_staff" label="现有人员" width="100" />
          <el-table-column prop="needed_staff" label="需要人员" width="100" />
          <el-table-column prop="shortage" label="缺口" width="80" />
          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="scope">
              <el-tag :type="getPriorityType(scope.row.priority)">
                {{ scope.row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="suggestion" label="建议" />
        </el-table>
        <div
          class="chart-container-small"
          style="height: 400px; margin-top: 20px"
          ref="resourceDetailChart"
        ></div>
      </div>
    </el-dialog>

    <!-- 模型评估详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.modelDetail"
      title="模型评估详情"
      width="800px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>模型详细评估指标</h3>
        <el-table :data="modelDetailData" style="width: 100%">
          <el-table-column prop="metric" label="指标" width="150" />
          <el-table-column prop="value" label="数值" width="100" />
          <el-table-column prop="description" label="说明" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag
                :type="scope.row.status === '良好' ? 'success' : 'warning'"
              >
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div
          class="chart-container-small"
          style="height: 400px; margin-top: 20px"
          ref="modelDetailChart"
        ></div>
      </div>
    </el-dialog>

    <!-- 异常检测详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.anomalyDetail"
      title="异常检测详情"
      width="800px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>异常详细信息</h3>
        <el-table :data="anomalyDetailData" style="width: 100%">
          <el-table-column prop="description" label="异常描述" width="180" />
          <el-table-column prop="details" label="详细信息" />
          <el-table-column prop="severity" label="严重程度" width="100">
            <template #default="scope">
              <el-tag
                :type="
                  scope.row.severity === '高'
                    ? 'danger'
                    : scope.row.severity === '中'
                      ? 'warning'
                      : 'info'
                "
              >
                {{ scope.row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="detection_time" label="检测时间" width="150" />
          <el-table-column prop="suggestion" label="建议" />
        </el-table>
        <div
          class="chart-container-small"
          style="height: 400px; margin-top: 20px"
          ref="anomalyDetailChart"
        ></div>
      </div>
    </el-dialog>

    <!-- 数据导出详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.exportDetail"
      title="数据导出配置"
      width="600px"
      top="20px"
    >
      <div class="dialog-content">
        <h3>导出选项</h3>
        <el-form :model="exportForm" label-width="120px">
          <el-form-item label="导出格式">
            <el-select v-model="exportForm.format" style="width: 100%">
              <el-option label="Excel" value="xlsx" />
              <el-option label="CSV" value="csv" />
              <el-option label="JSON" value="json" />
            </el-select>
          </el-form-item>
          <el-form-item label="导出内容">
            <el-checkbox-group v-model="exportForm.content">
              <el-checkbox label="预测数据" />
              <el-checkbox label="历史数据" />
              <el-checkbox label="资源配置" />
              <el-checkbox label="模型评估" />
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="exportForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="社区选择">
            <el-select
              v-model="exportForm.community"
              placeholder="选择社区"
              style="width: 100%"
            >
              <el-option label="所有社区" value="all" />
              <el-option
                v-for="community in communities"
                :key="community"
                :label="community"
                :value="community"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="服务类型">
            <el-select
              v-model="exportForm.service"
              placeholder="选择服务"
              style="width: 100%"
            >
              <el-option label="所有服务" value="all" />
              <el-option
                v-for="service in services"
                :key="service"
                :label="service"
                :value="service"
              />
            </el-select>
          </el-form-item>
        </el-form>
        <div style="margin-top: 20px; text-align: right">
          <el-button @click="dialogVisible.exportDetail = false"
            >取消</el-button
          >
          <el-button type="primary" @click="confirmExport">确认导出</el-button>
        </div>
      </div>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import axios from "axios";
import * as echarts from "echarts";
import { ElMessage } from "element-plus";
import { computed, nextTick, onMounted, ref, watch } from "vue";

// 类型定义
interface ModelMetrics {
  r2_score: number;
  mae: number;
  rmse: number;
  mape: number;
  train_samples: number;
  test_samples: number;
  cv_mean_r2: number;
  trained_at: string;
}

interface PredictionTrend {
  historical: {
    dates: string[];
    values: number[];
  };
  predicted: {
    dates: string[];
    values: number[];
    lower_bound?: number[];
    upper_bound?: number[];
  };
}

interface Recommendation {
  community: string;
  service: string;
  predicted_demand: number;
  daily_avg: number;
  staff_needed: number;
  priority: string;
  suggestion: string;
  confidence?: number;
}

interface Anomaly {
  description: string;
  details: string;
  severity: "高" | "中" | "低";
  suggestion: string;
}

interface ModelComparison {
  model: string;
  r2_score: number;
  mae: number;
  rmse: number;
  mape: number;
}

// 响应式数据
const selectedCommunity = ref("社区A");
const selectedService = ref("助餐");
const predictionDays = ref("7");
const predictionModel = ref("random_forest");
const dateRange = ref<[Date, Date] | null>(null);
const seasonalAnalysis = ref("none");
const confidenceLevel = ref("0.9");
const showConfidenceInterval = ref(false);
const analysisDimension = ref("community");
const recommendationFilter = ref("all");

const predictionTrend = ref<PredictionTrend>({
  historical: { dates: [], values: [] },
  predicted: { dates: [], values: [] },
});
const recommendations = ref<Recommendation[]>([]);
const modelMetrics = ref<ModelMetrics>({
  r2_score: 0,
  mae: 0,
  rmse: 0,
  mape: 0,
  train_samples: 0,
  test_samples: 0,
  cv_mean_r2: 0,
  trained_at: "",
});
const modelComparisons = ref<ModelComparison[]>([]);
const anomalies = ref<Anomaly[]>([]);
const isLoading = ref(false);

// 弹窗状态
const dialogVisible = ref({
  predictionDetail: false,
  resourceDetail: false,
  modelDetail: false,
  anomalyDetail: false,
  exportDetail: false,
});

// 详情数据
const predictionDetailData = ref([]);
const resourceDetailData = ref([]);
const modelDetailData = ref([]);
const anomalyDetailData = ref([]);

// 导出表单数据
const exportForm = ref({
  format: "xlsx",
  content: ["预测数据", "历史数据"],
  dateRange: null as [Date, Date] | null,
  community: "all",
  service: "all",
});

// 弹窗图表实例
const predictionDetailChart = ref<HTMLElement | null>(null);
const resourceDetailChart = ref<HTMLElement | null>(null);
const modelDetailChart = ref<HTMLElement | null>(null);
const anomalyDetailChart = ref<HTMLElement | null>(null);

// 计算属性
const filteredRecommendations = computed(() => {
  if (recommendationFilter.value === "all") {
    return recommendations.value;
  }
  return recommendations.value.filter(
    (item) => item.priority === recommendationFilter.value,
  );
});

// 社区和服务列表
const communities = ref([]);
const services = ref([]);

// 图表实例
let predictionChart: echarts.ECharts | null = null;
let demandDistributionChart: echarts.ECharts | null = null;
let trendComparisonChart: echarts.ECharts | null = null;
let modelComparisonChart: echarts.ECharts | null = null;

// 加载预测趋势数据
const loadPredictionTrend = async () => {
  try {
    isLoading.value = true;
    const response = await axios.get("/api/prediction/trend", {
      params: {
        community: selectedCommunity.value,
        service: selectedService.value,
        days: parseInt(predictionDays.value),
        model: predictionModel.value,
        confidence: parseFloat(confidenceLevel.value),
        seasonal: seasonalAnalysis.value,
      },
    });
    predictionTrend.value = response.data;

    // 加载预测详情数据
    await loadPredictionDetailData();

    await initPredictionChart();
  } catch (error) {
    console.error("加载预测趋势失败:", error);
  } finally {
    isLoading.value = false;
  }
};

// 加载预测详情数据
const loadPredictionDetailData = async () => {
  try {
    const response = await axios.get("/api/prediction/trend", {
      params: {
        community: selectedCommunity.value,
        service: selectedService.value,
        days: parseInt(predictionDays.value),
        model: predictionModel.value,
        confidence: parseFloat(confidenceLevel.value),
        seasonal: seasonalAnalysis.value,
      },
    });
    const trendData = response.data;

    predictionDetailData.value = trendData.predicted.dates.map(
      (date: string, index: number) => ({
        date,
        value: trendData.predicted.values?.[index] || 0,
        lower_bound: trendData.predicted.lower_bound?.[index] || 0,
        upper_bound: trendData.predicted.upper_bound?.[index] || 0,
        confidence:
          confidenceLevel.value === "0.9"
            ? "90%"
            : confidenceLevel.value === "0.95"
              ? "95%"
              : "80%",
        trend: "上升",
      }),
    );
  } catch (error) {
    console.error("加载预测详情数据失败:", error);
  }
};

// 加载资源配置建议
const loadRecommendations = async () => {
  try {
    const response = await axios.get(
      "/api/prediction/resource/recommendations",
      {
        params: {
          community: selectedCommunity.value,
        },
      },
    );
    recommendations.value = response.data;

    // 加载资源配置详情数据
    await loadResourceDetailData();
  } catch (error) {
    console.error("加载资源配置建议失败:", error);
  }
};

// 加载资源配置详情数据
const loadResourceDetailData = async () => {
  try {
    const response = await axios.get(
      "/api/prediction/resource/recommendations",
      {
        params: {
          community: selectedCommunity.value,
        },
      },
    );
    const recommendationData = response.data;

    resourceDetailData.value = recommendationData.map((item: any) => ({
      community: item.community,
      service: item.service,
      predicted_demand: item.predicted_demand,
      current_staff: Math.floor(item.staff_needed * 0.8), // 模拟数据
      needed_staff: item.staff_needed,
      shortage: item.staff_needed - Math.floor(item.staff_needed * 0.8), // 模拟数据
      priority: item.priority,
      suggestion: item.suggestion,
    }));
  } catch (error) {
    console.error("加载资源配置详情数据失败:", error);
  }
};

// 加载模型评估指标
const loadModelMetrics = async () => {
  try {
    const response = await axios.get("/api/prediction/model/metrics");
    modelMetrics.value = response.data;

    // 加载模型详情数据
    await loadModelDetailData();
  } catch (error) {
    console.error("加载模型评估指标失败:", error);
  }
};

// 加载模型详情数据
const loadModelDetailData = async () => {
  try {
    const response = await axios.get("/api/prediction/model/metrics");
    const metrics = response.data;

    modelDetailData.value = [
      {
        metric: "R² 评分",
        value: metrics.r2_score || 0,
        description: "模型解释方差的比例",
        status: "良好",
      },
      {
        metric: "平均绝对误差",
        value: metrics.mae || 0,
        description: "预测值与实际值的平均绝对差异",
        status: "良好",
      },
      {
        metric: "均方根误差",
        value: metrics.rmse || 0,
        description: "预测值与实际值的均方根差异",
        status: "良好",
      },
      {
        metric: "平均绝对百分比误差",
        value: metrics.mape || 0,
        description: "预测值与实际值的平均百分比差异",
        status: "良好",
      },
      {
        metric: "训练样本数",
        value: metrics.train_samples || 0,
        description: "用于训练模型的样本数量",
        status: "良好",
      },
      {
        metric: "测试样本数",
        value: metrics.test_samples || 0,
        description: "用于测试模型的样本数量",
        status: "良好",
      },
      {
        metric: "交叉验证R²",
        value: metrics.cv_mean_r2 || 0,
        description: "交叉验证的平均R²评分",
        status: "良好",
      },
      {
        metric: "训练时间",
        value: metrics.trained_at || "-",
        description: "模型训练完成的时间",
        status: "良好",
      },
    ];
  } catch (error) {
    console.error("加载模型详情数据失败:", error);
  }
};

// 加载模型对比数据
const loadModelComparisons = async () => {
  try {
    console.log("开始加载模型对比数据");
    const response = await axios.get("/api/prediction/model/comparison");
    console.log("模型对比数据:", response.data);
    modelComparisons.value = response.data;
    console.log("modelComparisons.value:", modelComparisons.value);
    // 确保数据加载后再初始化图表
    setTimeout(() => {
      initModelComparisonChart();
    }, 100);
  } catch (error) {
    console.error("加载模型对比数据失败:", error);
    // 加载失败时使用备用数据
    modelComparisons.value = [
      { model: "随机森林", r2_score: 0.85, mae: 8.2, rmse: 12.5, mape: 15.3 },
      { model: "梯度提升", r2_score: 0.88, mae: 7.5, rmse: 11.8, mape: 14.2 },
      { model: "XGBoost", r2_score: 0.9, mae: 6.8, rmse: 10.5, mape: 12.8 },
      { model: "集成模型", r2_score: 0.92, mae: 6.2, rmse: 9.8, mape: 11.5 },
    ];
    initModelComparisonChart();
  }
};

// 初始化预测趋势图表
const initPredictionChart = async () => {
  try {
    await nextTick();
    const chartDom = document.getElementById("predictionTrendChart");
    if (!chartDom) {
      console.error("预测趋势图表DOM元素不存在");
      return;
    }
    console.log(
      "预测趋势图表DOM元素存在，尺寸:",
      chartDom.clientWidth,
      "x",
      chartDom.clientHeight,
    );
    if (predictionChart) {
      predictionChart.dispose();
    }
    predictionChart = echarts.init(chartDom);

    // 确保数据结构完整
    const historicalData = predictionTrend.value.historical || {
      dates: [],
      values: [],
    };
    const predictedData = predictionTrend.value.predicted || {
      dates: [],
      values: [],
    };

    const series = [
      {
        name: "历史数据",
        type: "line",
        data: historicalData.values || [],
        itemStyle: {
          color: "#188df0",
        },
      },
      {
        name: "预测数据",
        type: "line",
        data: [
          ...Array(historicalData.values?.length || 0).fill(null),
          ...(predictedData.values || []),
        ],
        itemStyle: {
          color: "#0096c7",
        },
        lineStyle: {
          type: "dashed",
        },
      },
    ];

    // 添加置信区间
    if (
      showConfidenceInterval.value &&
      predictedData.lower_bound &&
      predictedData.upper_bound
    ) {
      series.push({
        name: "置信区间",
        type: "custom",
        renderItem: (params: any, api: any) => {
          const start = api.coord([api.value(0), api.value(1)]);
          const end = api.coord([api.value(0), api.value(2)]);
          const height = end[1] - start[1];
          return {
            type: "rect",
            shape: {
              x: start[0] - 5,
              y: start[1],
              width: 10,
              height: height,
            },
            style: {
              fill: "rgba(0, 150, 199, 0.3)",
            },
          };
        },
        data: predictedData.dates.map((date, index) => [
          index + (historicalData.values?.length || 0),
          predictedData.lower_bound![index],
          predictedData.upper_bound![index],
        ]),
      });
    }

    predictionChart.setOption({
      tooltip: {
        trigger: "axis",
      },
      legend: {
        data: showConfidenceInterval.value
          ? ["历史数据", "预测数据", "置信区间"]
          : ["历史数据", "预测数据"],
      },
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: [...(historicalData.dates || []), ...(predictedData.dates || [])],
      },
      yAxis: {
        type: "value",
      },
      series,
    });

    // 响应式调整
    window.addEventListener("resize", () => {
      predictionChart?.resize();
    });
  } catch (error) {
    console.error("初始化预测趋势图表失败:", error);
  }
};

// 初始化需求分布图表
const initDemandDistributionChart = async () => {
  try {
    await nextTick();
    const chartDom = document.getElementById("demandDistributionChart");
    if (!chartDom) {
      console.error("需求分布图表DOM元素不存在");
      return;
    }
    console.log(
      "需求分布图表DOM元素存在，尺寸:",
      chartDom.clientWidth,
      "x",
      chartDom.clientHeight,
    );
    if (demandDistributionChart) {
      demandDistributionChart.dispose();
    }
    demandDistributionChart = echarts.init(chartDom);

    // 模拟数据
    const data = [
      { name: "助餐", value: 120 },
      { name: "助医", value: 90 },
      { name: "保洁", value: 80 },
      { name: "陪护", value: 70 },
      { name: "康复", value: 60 },
    ];

    demandDistributionChart.setOption({
      tooltip: {
        trigger: "item",
      },
      legend: {
        orient: "vertical",
        left: "left",
      },
      series: [
        {
          name: "需求分布",
          type: "pie",
          radius: "60%",
          data: data,
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

    window.addEventListener("resize", () => {
      demandDistributionChart?.resize();
    });
  } catch (error) {
    console.error("初始化需求分布图表失败:", error);
  }
};

// 初始化趋势对比图表
const initTrendComparisonChart = async () => {
  try {
    await nextTick();
    const chartDom = document.getElementById("trendComparisonChart");
    if (!chartDom) {
      console.error("趋势对比图表DOM元素不存在");
      return;
    }
    console.log(
      "趋势对比图表DOM元素存在，尺寸:",
      chartDom.clientWidth,
      "x",
      chartDom.clientHeight,
    );
    if (trendComparisonChart) {
      trendComparisonChart.dispose();
    }
    trendComparisonChart = echarts.init(chartDom);

    // 模拟数据
    const dates = ["1月", "2月", "3月", "4月", "5月", "6月"];
    const data = [
      {
        name: "社区A",
        type: "line",
        data: [120, 132, 101, 134, 90, 230],
      },
      {
        name: "社区B",
        type: "line",
        data: [220, 182, 191, 234, 290, 330],
      },
      {
        name: "社区C",
        type: "line",
        data: [150, 232, 201, 154, 190, 330],
      },
    ];

    trendComparisonChart.setOption({
      tooltip: {
        trigger: "axis",
      },
      legend: {
        data: data.map((item) => item.name),
      },
      xAxis: {
        type: "category",
        data: dates,
      },
      yAxis: {
        type: "value",
      },
      series: data,
    });

    window.addEventListener("resize", () => {
      trendComparisonChart?.resize();
    });
  } catch (error) {
    console.error("初始化趋势对比图表失败:", error);
  }
};

// 初始化模型对比图表
const initModelComparisonChart = () => {
  try {
    // 检查DOM元素是否存在
    const chartDom = document.getElementById("modelComparisonChart");
    if (!chartDom) {
      console.error("模型对比图表DOM元素不存在");
      return;
    }
    console.log(
      "模型对比图表DOM元素存在，尺寸:",
      chartDom.clientWidth,
      "x",
      chartDom.clientHeight,
    );

    if (modelComparisonChart) {
      modelComparisonChart.dispose();
    }
    modelComparisonChart = echarts.init(chartDom);

    // 确保数据存在
    if (!modelComparisons.value || modelComparisons.value.length === 0) {
      console.error("模型对比数据为空，使用备用数据");
      // 使用备用数据
      const models = ["随机森林", "梯度提升", "XGBoost", "集成模型"];
      const metrics = [
        {
          name: "R² 评分",
          data: [0.85, 0.88, 0.9, 0.92],
        },
        {
          name: "MAE",
          data: [8.2, 7.5, 6.8, 6.2],
        },
        {
          name: "RMSE",
          data: [12.5, 11.8, 10.5, 9.8],
        },
        {
          name: "MAPE",
          data: [15.3, 14.2, 12.8, 11.5],
        },
      ];

      modelComparisonChart.setOption({
        tooltip: {
          trigger: "axis",
        },
        legend: {
          data: metrics.map((item) => item.name),
        },
        xAxis: {
          type: "category",
          data: models,
        },
        yAxis: {
          type: "value",
        },
        series: metrics,
      });
      return;
    }

    // 使用从后端获取的数据
    console.log("使用后端数据渲染图表:", modelComparisons.value);
    const models = modelComparisons.value.map((item) => item.model);
    const metrics = [
      {
        name: "R² 评分",
        data: modelComparisons.value.map((item) => item.r2_score),
        type: "bar",
        itemStyle: { color: "#67C23A" },
      },
      {
        name: "MAE",
        data: modelComparisons.value.map((item) => item.mae),
        type: "bar",
        itemStyle: { color: "#409EFF" },
      },
      {
        name: "RMSE",
        data: modelComparisons.value.map((item) => item.rmse),
        type: "bar",
        itemStyle: { color: "#E6A23C" },
      },
      {
        name: "MAPE",
        data: modelComparisons.value.map((item) => item.mape),
        type: "bar",
        itemStyle: { color: "#F56C6C" },
      },
    ];

    modelComparisonChart.setOption({
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },
      legend: {
        data: metrics.map((item) => item.name),
        bottom: 0,
      },
      xAxis: {
        type: "category",
        data: models,
      },
      yAxis: {
        type: "value",
      },
      series: metrics,
    });

    // 移除旧的 resize 事件监听器，避免重复添加
    window.removeEventListener("resize", handleResize);
    window.addEventListener("resize", handleResize);
  } catch (error) {
    console.error("初始化模型对比图表失败:", error);
  }
};

// 处理窗口大小变化
const handleResize = () => {
  modelComparisonChart?.resize();
};

// 刷新数据
const refreshData = () => {
  loadPredictionTrend();
  loadRecommendations();
  loadModelMetrics();
  loadModelComparisons();
};

// 训练模型
const trainModel = async () => {
  try {
    isLoading.value = true;
    await axios.post("/api/prediction/model/train");
    // 训练完成后刷新数据
    await loadModelMetrics();
    await loadModelComparisons();
    // 显示成功消息
    ElMessage.success("模型训练成功");
  } catch (error) {
    console.error("模型训练失败:", error);
    ElMessage.error("模型训练失败");
  } finally {
    isLoading.value = false;
  }
};

// 检测异常
const detectAnomalies = async () => {
  try {
    isLoading.value = true;
    const response = await axios.get("/api/prediction/anomalies");
    anomalies.value = response.data;

    // 加载异常详情数据
    await loadAnomalyDetailData();
  } catch (error) {
    console.error("检测异常失败:", error);
  } finally {
    isLoading.value = false;
  }
};

// 加载异常详情数据
const loadAnomalyDetailData = async () => {
  try {
    const response = await axios.get("/api/prediction/anomalies");
    const anomalyData = response.data;

    anomalyDetailData.value = anomalyData.map((item: any) => ({
      description: item.description,
      details: item.details,
      severity: item.severity,
      detection_time: new Date().toISOString().slice(0, 19).replace("T", " "), // 模拟数据
      suggestion: item.suggestion,
    }));
  } catch (error) {
    console.error("加载异常详情数据失败:", error);
  }
};

// 加载社区列表
const loadCommunities = async () => {
  try {
    const response = await axios.get("/api/data/communities");
    communities.value = response.data;
    if (communities.value.length > 0) {
      selectedCommunity.value = communities.value[0];
    }
  } catch (error) {
    console.error("加载社区列表失败:", error);
  }
};

// 加载服务列表
const loadServices = async () => {
  try {
    const response = await axios.get("/api/data/services");
    services.value = response.data;
    if (services.value.length > 0) {
      selectedService.value = services.value[0];
    }
  } catch (error) {
    console.error("加载服务列表失败:", error);
  }
};

// 获取优先级类型
const getPriorityType = (priority: string): string => {
  switch (priority) {
    case "高":
      return "danger";
    case "中":
      return "warning";
    case "低":
      return "success";
    default:
      return "info";
  }
};

// 打开弹窗方法
const openPredictionDetail = () => {
  dialogVisible.value.predictionDetail = true;
  setTimeout(() => {
    initPredictionDetailChart();
  }, 100);
};

const openResourceDetail = () => {
  dialogVisible.value.resourceDetail = true;
  setTimeout(() => {
    initResourceDetailChart();
  }, 100);
};

const openModelDetail = () => {
  dialogVisible.value.modelDetail = true;
  setTimeout(() => {
    initModelDetailChart();
  }, 100);
};

const openAnomalyDetail = () => {
  dialogVisible.value.anomalyDetail = true;
  setTimeout(() => {
    initAnomalyDetailChart();
  }, 100);
};

const openExportDetail = () => {
  dialogVisible.value.exportDetail = true;
};

// 初始化弹窗图表
const initPredictionDetailChart = () => {
  if (predictionDetailChart.value) {
    const chart = echarts.init(predictionDetailChart.value);
    chart.setOption({
      tooltip: {
        trigger: "axis",
      },
      legend: {
        data: ["预测值", "上限", "下限"],
      },
      xAxis: {
        type: "category",
        data: predictionDetailData.value.map((item) => item.date),
      },
      yAxis: {
        type: "value",
      },
      series: [
        {
          name: "预测值",
          type: "line",
          data: predictionDetailData.value.map((item) => item.value),
          itemStyle: { color: "#0096c7" },
        },
        {
          name: "上限",
          type: "line",
          data: predictionDetailData.value.map((item) => item.upper_bound),
          itemStyle: { color: "#ff7f50" },
          lineStyle: { type: "dashed" },
        },
        {
          name: "下限",
          type: "line",
          data: predictionDetailData.value.map((item) => item.lower_bound),
          itemStyle: { color: "#ff7f50" },
          lineStyle: { type: "dashed" },
        },
      ],
    });
  }
};

const initResourceDetailChart = () => {
  if (resourceDetailChart.value) {
    const chart = echarts.init(resourceDetailChart.value);
    chart.setOption({
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },
      legend: {
        data: ["现有人员", "需要人员"],
      },
      xAxis: {
        type: "category",
        data: resourceDetailData.value.map(
          (item) => `${item.community}-${item.service}`,
        ),
        axisLabel: {
          rotate: 45,
        },
      },
      yAxis: {
        type: "value",
      },
      series: [
        {
          name: "现有人员",
          type: "bar",
          data: resourceDetailData.value.map((item) => item.current_staff),
          itemStyle: { color: "#67C23A" },
        },
        {
          name: "需要人员",
          type: "bar",
          data: resourceDetailData.value.map((item) => item.needed_staff),
          itemStyle: { color: "#409EFF" },
        },
      ],
    });
  }
};

const initModelDetailChart = () => {
  if (modelDetailChart.value) {
    const chart = echarts.init(modelDetailChart.value);
    chart.setOption({
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },
      xAxis: {
        type: "category",
        data: modelDetailData.value.map((item) => item.metric),
        axisLabel: {
          rotate: 45,
        },
      },
      yAxis: {
        type: "value",
      },
      series: [
        {
          name: "数值",
          type: "bar",
          data: modelDetailData.value.map((item) => item.value),
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

const initAnomalyDetailChart = () => {
  if (anomalyDetailChart.value) {
    const chart = echarts.init(anomalyDetailChart.value);
    chart.setOption({
      tooltip: {
        trigger: "item",
      },
      legend: {
        orient: "vertical",
        left: "left",
      },
      series: [
        {
          name: "异常类型",
          type: "pie",
          radius: "60%",
          data: [
            {
              value: anomalyDetailData.value.filter(
                (item) => item.severity === "高",
              ).length,
              name: "高严重度",
            },
            {
              value: anomalyDetailData.value.filter(
                (item) => item.severity === "中",
              ).length,
              name: "中严重度",
            },
            {
              value: anomalyDetailData.value.filter(
                (item) => item.severity === "低",
              ).length,
              name: "低严重度",
            },
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
  }
};

// 确认导出
const confirmExport = async () => {
  try {
    isLoading.value = true;
    // 这里可以根据exportForm的值构建导出参数
    const response = await axios.get("/api/prediction/export", {
      params: {
        community:
          exportForm.value.community === "all"
            ? selectedCommunity.value
            : exportForm.value.community,
        service:
          exportForm.value.service === "all"
            ? selectedService.value
            : exportForm.value.service,
        days: parseInt(predictionDays.value),
        format: exportForm.value.format,
      },
      responseType: "blob",
    });

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `prediction_${exportForm.value.community}_${exportForm.value.service}_${new Date().toISOString().slice(0, 10)}.${exportForm.value.format}`,
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    ElMessage.success("数据导出成功");
    dialogVisible.value.exportDetail = false;
  } catch (error) {
    console.error("导出数据失败:", error);
    ElMessage.error("导出数据失败");
  } finally {
    isLoading.value = false;
  }
};

// 导出数据
const exportData = () => {
  openExportDetail();
};

// 监听选择变化
watch(
  [
    selectedCommunity,
    selectedService,
    predictionDays,
    predictionModel,
    confidenceLevel,
    seasonalAnalysis,
  ],
  () => {
    loadPredictionTrend();
  },
);

watch(analysisDimension, async () => {
  await initDemandDistributionChart();
  await initTrendComparisonChart();
});

// 页面加载时初始化
onMounted(async () => {
  await loadCommunities();
  await loadServices();
  loadPredictionTrend();
  loadRecommendations();
  loadModelMetrics();
  await loadModelComparisons();
  await initDemandDistributionChart();
  await initTrendComparisonChart();
});
</script>

<style scoped>
.prediction-container {
  height: 100vh;
  overflow-y: auto;
}

.header {
  display: flex;
  justify-content: space-between;
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

.header-right {
  display: flex;
  align-items: center;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.sub-chart-container {
  height: 300px;
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.metric-item {
  background-color: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  border-left: 4px solid #0066cc;
  transition: transform 0.2s ease;
}

.metric-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.metric-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.control-panel {
  padding: 10px 0;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(45%, 1fr));
  gap: 20px;
}

.analysis-item {
  background-color: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.analysis-item h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
  font-size: 1rem;
}

.model-comparison {
  margin-top: 20px;
}

.no-anomalies {
  padding: 40px 0;
  text-align: center;
}

/* 加载状态 */
.is-loading {
  opacity: 0.6;
  pointer-events: none;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .header {
    flex-direction: column;
    height: auto;
    padding: 10px;
  }

  .header-left,
  .header-right {
    width: 100%;
    text-align: center;
    margin-bottom: 10px;
  }
}

/* 弹窗样式 */
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
