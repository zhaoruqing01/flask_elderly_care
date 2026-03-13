<template>
  <el-container class="data-container">
    <el-header height="60px" class="header">
      <div class="header-left">
        <h2>数据管理</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="refreshData" icon="Refresh">
          刷新数据
        </el-button>
        <el-button
          type="success"
          @click="exportData"
          icon="Download"
          style="margin-left: 10px"
        >
          导出数据
        </el-button>
      </div>
    </el-header>
    <el-main>
      <!-- 数据统计 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>数据统计</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-value">{{ stats.senior_count }}</div>
              <div class="stat-label">老人总数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-value">{{ stats.health_records }}</div>
              <div class="stat-label">健康记录</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-value">{{ stats.service_logs }}</div>
              <div class="stat-label">服务记录</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-value">{{ stats.communities }}</div>
              <div class="stat-label">社区数量</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 数据表格 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>老人基本信息</span>
            <div class="card-header-actions">
              <el-select
                v-model="tableFilter"
                placeholder="按社区筛选"
                style="width: 150px"
              >
                <el-option label="全部社区" value="all" />
                <el-option
                  v-for="community in communities"
                  :key="community"
                  :label="community"
                  :value="community"
                />
              </el-select>
            </div>
          </div>
        </template>
        <el-table :data="seniorsData" style="width: 100%" border>
          <el-table-column prop="id" label="ID" />
          <el-table-column prop="age" label="年龄" />
          <el-table-column prop="community_id" label="社区" />
          <el-table-column prop="health_status" label="健康状态">
            <template #default="scope">
              <el-tag :type="getHealthStatusType(scope.row.health_status)">
                {{ scope.row.health_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="service_count" label="服务次数" />
          <el-table-column
            prop="avg_satisfaction"
            label="平均满意度"
            width="120"
          />
        </el-table>
        <div class="pagination" style="margin-top: 20px">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalSeniors"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>

      <!-- 健康记录表格 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>健康记录</span>
            <div class="card-header-actions">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 240px"
              />
              <el-button
                size="small"
                @click="filterHealthRecords"
                style="margin-left: 10px"
              >
                筛选
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="healthRecords" style="width: 100%" border>
          <el-table-column prop="id" label="记录ID" />
          <el-table-column prop="senior_id" label="老人ID" />
          <el-table-column prop="date" label="记录日期" />
          <el-table-column prop="sbp" label="收缩压" />
          <el-table-column prop="dbp" label="舒张压" />
          <el-table-column prop="blood_sugar" label="血糖" />
          <el-table-column prop="heart_rate" label="心率" />
          <el-table-column prop="health_status" label="健康状态">
            <template #default="scope">
              <el-tag :type="getHealthStatusType(scope.row.health_status)">
                {{ scope.row.health_status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination" style="margin-top: 20px">
          <el-pagination
            v-model:current-page="healthCurrentPage"
            v-model:page-size="healthPageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalHealthRecords"
            @size-change="handleHealthSizeChange"
            @current-change="handleHealthCurrentChange"
          />
        </div>
      </el-card>

      <!-- 服务记录表格 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>服务记录</span>
            <div class="card-header-actions">
              <el-select
                v-model="serviceTypeFilter"
                placeholder="按服务类型筛选"
                style="width: 120px"
              >
                <el-option label="全部类型" value="all" />
                <el-option
                  v-for="service in services"
                  :key="service"
                  :label="service"
                  :value="service"
                />
              </el-select>
              <el-button
                size="small"
                @click="filterServiceRecords"
                style="margin-left: 10px"
              >
                筛选
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="serviceRecords" style="width: 100%" border>
          <el-table-column prop="id" label="记录ID" />
          <el-table-column prop="senior_id" label="老人ID" />
          <el-table-column prop="service_date" label="服务日期" />
          <el-table-column prop="service_type" label="服务类型" />
          <el-table-column prop="duration" label="服务时长(分钟)" />
          <el-table-column prop="satisfaction" label="满意度">
            <template #default="scope">
              <el-rate v-model="scope.row.satisfaction" disabled />
            </template>
          </el-table-column>
          <el-table-column prop="community_id" label="社区" width="100" />
        </el-table>
        <div class="pagination" style="margin-top: 20px">
          <el-pagination
            v-model:current-page="serviceCurrentPage"
            v-model:page-size="servicePageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalServiceRecords"
            @size-change="handleServiceSizeChange"
            @current-change="handleServiceCurrentChange"
          />
        </div>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import axios from "axios";
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";

// 响应式数据
const stats = ref({
  senior_count: 0,
  health_records: 0,
  service_logs: 0,
  communities: 0,
});

const communities = ref(["社区A", "社区B", "社区C", "社区D", "社区E"]);
const services = ref(["助餐", "助医", "保洁", "陪护", "康复"]);

// 表格数据
const seniorsData = ref([]);
const healthRecords = ref([]);
const serviceRecords = ref([]);

// 分页数据
const currentPage = ref(1);
const pageSize = ref(20);
const totalSeniors = ref(0);

const healthCurrentPage = ref(1);
const healthPageSize = ref(20);
const totalHealthRecords = ref(0);

const serviceCurrentPage = ref(1);
const servicePageSize = ref(20);
const totalServiceRecords = ref(0);

// 筛选条件
const tableFilter = ref("all");
const dateRange = ref(null);
const serviceTypeFilter = ref("all");

// 获取健康状态类型
const getHealthStatusType = (status) => {
  switch (status) {
    case "良好":
      return "success";
    case "临界":
      return "warning";
    case "高危":
      return "danger";
    default:
      return "info";
  }
};

// 加载数据统计
const loadStats = async () => {
  try {
    const response = await axios.get("/api/data/stats");
    stats.value = response.data;
  } catch (error) {
    console.error("加载数据统计失败:", error);
  }
};

// 加载老人数据
const loadSeniorsData = async () => {
  try {
    const response = await axios.get("/api/data/seniors", {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        community: tableFilter.value === "all" ? "" : tableFilter.value,
      },
    });
    seniorsData.value = response.data.items;
    totalSeniors.value = response.data.total;
  } catch (error) {
    console.error("加载老人数据失败:", error);
  }
};

// 加载健康记录
const loadHealthRecords = async () => {
  try {
    const params = {
      page: healthCurrentPage.value,
      page_size: healthPageSize.value,
    };
    if (dateRange.value) {
      params.start_date = dateRange.value[0];
      params.end_date = dateRange.value[1];
    }
    const response = await axios.get("/api/data/health-records", { params });
    healthRecords.value = response.data.items;
    totalHealthRecords.value = response.data.total;
  } catch (error) {
    console.error("加载健康记录失败:", error);
  }
};

// 加载服务记录
const loadServiceRecords = async () => {
  try {
    const params = {
      page: serviceCurrentPage.value,
      page_size: servicePageSize.value,
    };
    if (serviceTypeFilter.value !== "all") {
      params.service_type = serviceTypeFilter.value;
    }
    const response = await axios.get("/api/data/service-records", { params });
    serviceRecords.value = response.data.items;
    totalServiceRecords.value = response.data.total;
  } catch (error) {
    console.error("加载服务记录失败:", error);
  }
};

// 刷新数据
const refreshData = () => {
  loadStats();
  loadSeniorsData();
  loadHealthRecords();
  loadServiceRecords();
};

// 导出数据
const exportData = async () => {
  try {
    const response = await axios.get("/api/data/export", {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `data_export_${new Date().toISOString().slice(0, 10)}.xlsx`,
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    ElMessage.success("数据导出成功");
  } catch (error) {
    console.error("导出数据失败:", error);
    ElMessage.error("导出数据失败");
  }
};

// 筛选健康记录
const filterHealthRecords = () => {
  healthCurrentPage.value = 1;
  loadHealthRecords();
};

// 筛选服务记录
const filterServiceRecords = () => {
  serviceCurrentPage.value = 1;
  loadServiceRecords();
};

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size;
  loadSeniorsData();
};

const handleCurrentChange = (current) => {
  currentPage.value = current;
  loadSeniorsData();
};

const handleHealthSizeChange = (size) => {
  healthPageSize.value = size;
  loadHealthRecords();
};

const handleHealthCurrentChange = (current) => {
  healthCurrentPage.value = current;
  loadHealthRecords();
};

const handleServiceSizeChange = (size) => {
  servicePageSize.value = size;
  loadServiceRecords();
};

const handleServiceCurrentChange = (current) => {
  serviceCurrentPage.value = current;
  loadServiceRecords();
};

// 页面加载时初始化
onMounted(() => {
  loadStats();
  loadSeniorsData();
  loadHealthRecords();
  loadServiceRecords();
});
</script>

<style scoped>
.data-container {
  width: 100%;
  height: 100%;
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

.stat-item {
  background-color: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border-left: 4px solid #0066cc;
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}

/* 响应式调整 */
@media (max-width: 768px) {
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

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .card-header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
