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
      </div>
    </el-header>
    <el-main>
      <!-- 数据统计 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>数据统计概览</span>
            <el-button
              v-if="isInstitution || isRegulatory"
              type="text"
              @click="showReportDialog"
              >查看详细报表</el-button
            >
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="4">
            <div class="stat-item">
              <div class="stat-value">{{ stats.senior_count }}</div>
              <div class="stat-label">老人总数</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="stat-item">
              <div class="stat-value">{{ stats.health_records }}</div>
              <div class="stat-label">健康记录</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="stat-item">
              <div class="stat-value">{{ stats.service_logs }}</div>
              <div class="stat-label">服务记录</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="stat-item">
              <div class="stat-value">{{ stats.communities }}</div>
              <div class="stat-label">社区数量</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="stat-item">
              <div class="stat-value">{{ stats.caregivers }}</div>
              <div class="stat-label">护工总数</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 需求预测 (所有角色可见，护工仅看本社区) -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>社区养老需求查看</span>
          </div>
        </template>
        <el-table :data="predictionsData" style="width: 100%" border>
          <el-table-column prop="community_id" label="社区ID" />
          <el-table-column prop="service_type" label="服务类型" />
          <el-table-column prop="prediction_date" label="预测日期" />
          <el-table-column prop="predicted_demand" label="预测需求量" />
        </el-table>
      </el-card>

      <!-- 社区信息管理 (仅养老机构可见) -->
      <el-card v-if="isInstitution" style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>社区信息管理</span>
            <div class="card-header-actions">
              <el-button
                type="primary"
                size="small"
                icon="Plus"
                @click="showAddCommunityDialog"
              >
                新增社区
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="communitiesFullData" style="width: 100%" border>
          <el-table-column prop="community_id" label="社区ID" />
          <el-table-column prop="name" label="社区名称" />
          <el-table-column prop="total_population" label="总人口" />
          <el-table-column prop="elderly_population" label="老年人口" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button
                size="small"
                @click="showEditCommunityDialog(scope.row)"
                >修改</el-button
              >
              <el-button
                size="small"
                type="danger"
                @click="handleDeleteCommunity(scope.row.community_id)"
                >删除</el-button
              >
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 护工管理 (仅养老机构可见) -->
      <el-card v-if="isInstitution" style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>护工管理</span>
            <div class="card-header-actions">
              <el-button
                type="success"
                size="small"
                icon="Plus"
                @click="showAddCaregiverDialog"
              >
                新增护工
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="caregiversData" style="width: 100%" border>
          <el-table-column prop="caregiver_id" label="护工ID" />
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="community_id" label="所属社区" />
          <el-table-column prop="qualification" label="资质" />
        </el-table>
      </el-card>

      <!-- 排班管理 (养老机构可见管理，护工可见自身) -->
      <el-card v-if="isInstitution || isCaregiver" style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>排班管理</span>
            <div class="card-header-actions">
              <el-button
                v-if="isInstitution"
                type="warning"
                size="small"
                icon="Plus"
                @click="showAddScheduleDialog"
              >
                新增排班
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="schedulesData" style="width: 100%" border>
          <el-table-column prop="caregiver_id" label="护工ID" />
          <el-table-column prop="elderly_id" label="老人ID" />
          <el-table-column prop="service_type" label="服务类型" />
          <el-table-column prop="service_date" label="服务日期" />
          <el-table-column prop="service_time_slot" label="时间段" />
          <el-table-column prop="status" label="状态" />
        </el-table>
      </el-card>

      <!-- 数据表格 -->
      <el-card style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>老人基本信息</span>
            <div class="card-header-actions">
              <el-button
                v-if="isInstitution"
                type="primary"
                size="small"
                icon="Plus"
                @click="showAddElderlyDialog"
                style="margin-right: 10px"
              >
                新增老人
              </el-button>
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
        <el-table
          :data="seniorsData"
          style="width: 100%"
          border
          show-overflow-tooltip
        >
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
          <el-table-column prop="avg_satisfaction" label="平均满意度" />
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
              <el-button
                v-if="isCaregiver"
                type="danger"
                size="small"
                icon="Plus"
                @click="showAddHealthRecordDialog"
                style="margin-right: 10px"
              >
                上报健康记录
              </el-button>
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
        <el-table
          :data="healthRecords"
          style="width: 100%"
          border
          show-overflow-tooltip
        >
          <!-- <el-table-column prop="id" label="记录ID" /> -->
          <el-table-column prop="id" label="老人ID" />
          <el-table-column prop="created_at" label="记录日期" />
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
              <el-button
                v-if="isCaregiver"
                type="info"
                size="small"
                icon="Plus"
                @click="showAddServiceRecordDialog"
                style="margin-right: 10px"
              >
                提交服务记录
              </el-button>
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
        <el-table
          :data="serviceRecords"
          style="width: 100%"
          border
          show-overflow-tooltip
        >
          <!-- <el-table-column prop="id" label="记录ID" /> -->
          <el-table-column prop="id" label="老人ID" />
          <el-table-column prop="service_date" label="服务日期" />
          <el-table-column prop="service_type" label="服务类型" />
          <el-table-column prop="duration" label="服务时长(分钟)" />
          <el-table-column prop="satisfaction" label="满意度">
            <template #default="scope">
              <el-rate v-model="scope.row.satisfaction" disabled />
            </template>
          </el-table-column>
          <el-table-column prop="community_id" label="社区" />
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
import auth from "@/utils/auth";
import axios from "@/utils/http";
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, ref } from "vue";

const currentUser = computed(() => auth.getCurrentUser());
const isInstitution = computed(() => currentUser.value?.role === "institution");
const isCaregiver = computed(() => currentUser.value?.role === "caregiver");
const isRegulatory = computed(() => currentUser.value?.role === "regulatory");
const isReadOnly = computed(() => isRegulatory.value);

// 护工与排班数据
const caregiversData = ref([]);
const schedulesData = ref([]);
const predictionsData = ref([]);
const communitiesFullData = ref([]);

// --- 弹窗逻辑 ---
const showAddCommunityDialog = () => {
  ElMessageBox.prompt(
    "请输入社区信息 (格式: ID,名称,总人口,老年人口)",
    "新增社区",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
    },
  ).then(async ({ value }) => {
    const [id, name, total, elderly] = value.split(",");
    await axios.post("/api/data/communities", {
      community_id: id,
      name,
      total_population: parseInt(total),
      elderly_population: parseInt(elderly),
    });
    refreshData();
  });
};

const showEditCommunityDialog = (row: any) => {
  ElMessageBox.prompt(
    "请修改社区信息 (格式: 名称,总人口,老年人口)",
    "修改社区",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      inputValue: `${row.name},${row.total_population},${row.elderly_population}`,
    },
  ).then(async ({ value }) => {
    const [name, total, elderly] = value.split(",");
    await axios.put(`/api/data/communities/${row.community_id}`, {
      name,
      total_population: parseInt(total),
      elderly_population: parseInt(elderly),
    });
    refreshData();
  });
};

const handleDeleteCommunity = (id: string) => {
  ElMessageBox.confirm("确定删除该社区吗？", "提示", { type: "warning" }).then(
    async () => {
      try {
        await axios.delete(`/api/data/communities/${id}`);
        refreshData();
      } catch (e: any) {
        ElMessage.error(e.response?.data?.error || "删除失败");
      }
    },
  );
};

const showAddElderlyDialog = () => {
  ElMessageBox.prompt(
    "请输入老人信息 (格式: ID,姓名,年龄,性别,社区ID)",
    "新增老人",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
    },
  ).then(async ({ value }) => {
    const [id, name, age, gender, commId] = value.split(",");
    await axios.post("/api/data/seniors", {
      elderly_id: id,
      name,
      age: parseInt(age),
      gender,
      community_id: commId,
    });
    refreshData();
  });
};

const showAddCaregiverDialog = () => {
  ElMessageBox.prompt(
    "请输入护工信息 (格式: ID,姓名,社区ID,资质)",
    "新增护工",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
    },
  ).then(async ({ value }) => {
    const [id, name, commId, qual] = value.split(",");
    await axios.post("/api/data/caregivers", {
      caregiver_id: id,
      name,
      community_id: commId,
      qualification: qual,
    });
    refreshData();
  });
};

const showAddScheduleDialog = () => {
  ElMessageBox.prompt(
    "请输入排班信息 (格式: 护工ID,老人ID,类型,日期,时段)",
    "新增排班",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
    },
  ).then(async ({ value }) => {
    const [cgId, eId, type, date, slot] = value.split(",");
    await axios.post("/api/data/schedules", {
      caregiver_id: cgId,
      elderly_id: eId,
      service_type: type,
      service_date: date,
      service_time_slot: slot,
    });
    refreshData();
  });
};

const showAddHealthRecordDialog = () => {
  ElMessageBox.prompt(
    "请输入健康记录 (格式: 老人ID,日期,高压,低压,血糖,心率,状态)",
    "上报健康记录",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
    },
  ).then(async ({ value }) => {
    const [eId, date, sbp, dbp, sugar, hr, status] = value.split(",");
    await axios.post("/api/data/health-records", {
      elderly_id: eId,
      record_date: date,
      sbp: parseInt(sbp),
      dbp: parseInt(dbp),
      blood_sugar: parseFloat(sugar),
      heart_rate: parseInt(hr),
      health_status: status,
    });
    refreshData();
  });
};

const showAddServiceRecordDialog = () => {
  ElMessageBox.prompt(
    "请输入服务记录 (格式: 老人ID,社区ID,类型,日期,时长,满意度,护工ID)",
    "提交服务记录",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
    },
  ).then(async ({ value }) => {
    const [eId, commId, type, date, dur, sat, cgId] = value.split(",");
    await axios.post("/api/data/service-records", {
      elderly_id: eId,
      community_id: commId,
      service_type: type,
      service_date: date,
      duration: parseInt(dur),
      satisfaction: parseInt(sat),
      caregiver_id: cgId,
    });
    refreshData();
  });
};

const showReportDialog = async () => {
  const res = await axios.get("/api/data/reports/community");
  ElMessageBox.alert(JSON.stringify(res.data, null, 2), "社区全景统计报表", {
    customClass: "report-msgbox",
  });
};

const communities = ref([]);
const services = ref([]);

// 响应式统计数据
const stats = ref({
  senior_count: 0,
  health_records: 0,
  service_logs: 0,
  communities: 0,
  caregivers: 0,
});

// 表格数据
const seniorsData = ref([]);
const totalSeniors = ref(0);
const healthRecords = ref([]);
const totalHealthRecords = ref(0);
const serviceRecords = ref([]);
const totalServiceRecords = ref(0);

// 分页数据
const currentPage = ref(1);
const pageSize = ref(20);

const healthCurrentPage = ref(1);
const healthPageSize = ref(20);

const serviceCurrentPage = ref(1);
const servicePageSize = ref(20);

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

// 加载社区列表
const loadCommunities = async () => {
  try {
    const response = await axios.get("/api/data/communities");
    communities.value = response.data;
  } catch (error) {
    console.error("加载社区列表失败:", error);
  }
};

// 加载服务类型列表
const loadServices = async () => {
  try {
    const response = await axios.get("/api/data/services");
    services.value = response.data;
  } catch (error) {
    console.error("加载服务类型列表失败:", error);
  }
};

// 刷新数据
const refreshData = async () => {
  try {
    await loadStats();

    const commRes = await axios.get("/api/data/communities");
    communitiesFullData.value = commRes.data;
    communities.value = commRes.data.map((c: any) => c.name);

    const predRes = await axios.get("/api/data/predictions");
    predictionsData.value = predRes.data;

    if (isInstitution.value || isCaregiver.value) {
      const cgRes = await axios.get("/api/data/caregivers");
      caregiversData.value = cgRes.data;

      const schRes = await axios.get("/api/data/schedules", {
        params: isCaregiver.value
          ? { caregiver_id: currentUser.value?.username }
          : {},
      });
      schedulesData.value = schRes.data;
    }

    await loadSeniorsData();
    await loadHealthRecords();
    await loadServiceRecords();
    await loadServices();

    ElMessage.success("数据已刷新");
  } catch (error) {
    console.error("刷新数据失败:", error);
    ElMessage.error("数据加载失败");
  }
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
  loadCommunities();
  loadServices();
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
