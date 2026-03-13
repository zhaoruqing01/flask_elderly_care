<template>
  <el-container class="service-container">
    <el-header height="60px" class="header">
      <div class="header-left">
        <h2>服务分析</h2>
      </div>
    </el-header>
    <el-main>
      <!-- 服务使用频次 -->
      <el-card style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>服务使用频次</span>
          </div>
        </template>
        <div id="serviceFrequencyChart" class="chart-container"></div>
      </el-card>

      <!-- 按社区分析服务使用频次 -->
      <el-card style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>按社区分析服务使用频次</span>
          </div>
        </template>
        <div id="serviceByCommunityChart" class="chart-container"></div>
      </el-card>

      <!-- 服务满意度 -->
      <el-card style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>服务满意度</span>
          </div>
        </template>
        <div id="serviceSatisfactionChart" class="chart-container"></div>
      </el-card>

      <!-- 服务使用趋势 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>服务使用趋势</span>
          </div>
        </template>
        <div id="serviceTrendChart" class="chart-container"></div>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

// 类型定义
interface ServiceFrequency {
  types: string[]
  counts: number[]
}

interface ServiceByCommunity {
  communities: string[]
  datasets: {
    name: string
    values: number[]
  }[]
}

interface ServiceSatisfaction {
  types: string[]
  satisfaction: number[]
}

interface ServiceTrend {
  dates: string[]
  datasets: {
    name: string
    values: number[]
  }[]
}

// 响应式数据
const serviceFrequency = ref<ServiceFrequency>({ types: [], counts: [] })
const serviceByCommunity = ref<ServiceByCommunity>({ communities: [], datasets: [] })
const serviceSatisfaction = ref<ServiceSatisfaction>({ types: [], satisfaction: [] })
const serviceTrend = ref<ServiceTrend>({ dates: [], datasets: [] })

// 图表实例
let serviceFrequencyChart: echarts.ECharts | null = null
let serviceByCommunityChart: echarts.ECharts | null = null
let serviceSatisfactionChart: echarts.ECharts | null = null
let serviceTrendChart: echarts.ECharts | null = null

// 加载数据
const loadData = async () => {
  try {
    // 加载服务使用频次
    const frequencyRes = await axios.get('/api/service/frequency')
    serviceFrequency.value = frequencyRes.data

    // 加载按社区分析的服务使用频次
    const communityRes = await axios.get('/api/service/frequency/community')
    serviceByCommunity.value = communityRes.data

    // 加载服务满意度
    const satisfactionRes = await axios.get('/api/service/satisfaction')
    serviceSatisfaction.value = satisfactionRes.data

    // 加载服务使用趋势
    const trendRes = await axios.get('/api/service/trend')
    serviceTrend.value = trendRes.data

    // 初始化图表
    initCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 初始化图表
const initCharts = () => {
  // 服务使用频次图表
  if (serviceFrequencyChart) {
    serviceFrequencyChart.dispose()
  }
  serviceFrequencyChart = echarts.init(document.getElementById('serviceFrequencyChart'))
  serviceFrequencyChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: serviceFrequency.value.types || []
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '使用次数',
        type: 'bar',
        data: serviceFrequency.value.counts || [],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }
    ]
  })

  // 按社区分析服务使用频次图表
  if (serviceByCommunityChart) {
    serviceByCommunityChart.dispose()
  }
  serviceByCommunityChart = echarts.init(document.getElementById('serviceByCommunityChart'))
  serviceByCommunityChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: serviceByCommunity.value.datasets?.map((item: any) => item.name) || []
    },
    xAxis: {
      type: 'category',
      data: serviceByCommunity.value.communities || []
    },
    yAxis: {
      type: 'value'
    },
    series: serviceByCommunity.value.datasets?.map((item: any) => ({
      name: item.name,
      type: 'bar',
      data: item.data
    })) || []
  })

  // 服务满意度图表
  if (serviceSatisfactionChart) {
    serviceSatisfactionChart.dispose()
  }
  serviceSatisfactionChart = echarts.init(document.getElementById('serviceSatisfactionChart'))
  serviceSatisfactionChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: serviceSatisfaction.value.types || []
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 5
    },
    series: [
      {
        name: '满意度',
        type: 'bar',
        data: serviceSatisfaction.value.satisfaction || [],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#87e0fd' },
            { offset: 0.5, color: '#53cbf1' },
            { offset: 1, color: '#0096c7' }
          ])
        }
      }
    ]
  })

  // 服务使用趋势图表
  if (serviceTrendChart) {
    serviceTrendChart.dispose()
  }
  serviceTrendChart = echarts.init(document.getElementById('serviceTrendChart'))
  serviceTrendChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: serviceTrend.value.datasets?.map((item: any) => item.name) || []
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: serviceTrend.value.dates || []
    },
    yAxis: {
      type: 'value'
    },
    series: serviceTrend.value.datasets?.map((item: any) => ({
      name: item.name,
      type: 'line',
      data: item.data
    })) || []
  })

  // 响应式调整
  window.addEventListener('resize', () => {
    serviceFrequencyChart?.resize()
    serviceByCommunityChart?.resize()
    serviceSatisfactionChart?.resize()
    serviceTrendChart?.resize()
  })
}

// 页面加载时初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.service-container {
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
  color: #0066CC;
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
</style>
