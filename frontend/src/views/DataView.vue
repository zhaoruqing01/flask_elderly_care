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

      <!-- 需求预测 -->
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

      <!-- 社区信息管理 -->
      <el-card v-if="isInstitution" style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>社区信息管理</span>
            <div class="card-header-actions">
              <el-button
                type="primary"
                size="small"
                icon="Plus"
                @click="dialogs.community.visible = true"
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
              <el-button size="small" @click="handleEditCommunity(scope.row)"
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

      <!-- 护工管理 -->
      <el-card v-if="isInstitution" style="margin-bottom: 20px">
        <template #header>
          <div class="card-header">
            <span>护工管理</span>
            <div class="card-header-actions">
              <el-button
                type="success"
                size="small"
                icon="Plus"
                @click="dialogs.caregiver.visible = true"
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

      <!-- 排班管理 -->
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
                @click="dialogs.schedule.visible = true"
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

      <!-- 老人基本信息 -->
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
                @click="dialogs.elderly.visible = true"
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
          <el-table-column prop="elderly_id" label="ID" />
          <el-table-column prop="name" label="姓名" />
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
          <el-table-column label="操作" width="150" v-if="isInstitution">
            <template #default="scope">
              <el-button size="small" @click="handleEditElderly(scope.row)"
                >修改</el-button
              >
              <el-button
                size="small"
                type="danger"
                @click="handleDeleteElderly(scope.row.elderly_id)"
                >删除</el-button
              >
            </template>
          </el-table-column>
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

      <!-- 健康记录 -->
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
                @click="dialogs.healthRecord.visible = true"
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
          <el-table-column prop="elderly_id" label="老人ID" />
          <el-table-column prop="record_date" label="记录日期" />
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

      <!-- 服务记录 -->
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
                @click="dialogs.serviceRecord.visible = true"
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
          <el-table-column prop="elderly_id" label="老人ID" />
          <el-table-column prop="service_date" label="服务日期" />
          <el-table-column prop="service_type" label="服务类型" />
          <el-table-column prop="duration" label="服务时长(分钟)" />
          <el-table-column prop="satisfaction" label="满意度" />
          <el-table-column prop="community_id" label="社区" />
        </el-table>
        <div class="pagination" style="margin-top: 20px">
          <el-pagination
            v-model:current-page="serviceCurrentPage"
            v-model:page-size="servicePageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalServiceRecords"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </el-main>

    <!-- 弹窗部分 -->
    <!-- 社区弹窗 -->
    <el-dialog
      v-model="dialogs.community.visible"
      :title="dialogs.community.isEdit ? '编辑社区' : '新增社区'"
      width="500px"
    >
      <el-form :model="dialogs.community.form" label-width="100px">
        <el-form-item label="社区ID">
          <el-input
            v-model="dialogs.community.form.community_id"
            :disabled="dialogs.community.isEdit"
          />
        </el-form-item>
        <el-form-item label="社区名称">
          <el-input v-model="dialogs.community.form.name" />
        </el-form-item>
        <el-form-item label="总人口">
          <el-input-number v-model="dialogs.community.form.total_population" />
        </el-form-item>
        <el-form-item label="老年人口">
          <el-input-number
            v-model="dialogs.community.form.elderly_population"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.community.visible = false">取消</el-button>
        <el-button type="primary" @click="submitCommunity">提交</el-button>
      </template>
    </el-dialog>

    <!-- 老人弹窗 -->
    <el-dialog v-model="dialogs.elderly.visible" :title="dialogs.elderly.isEdit ? '编辑老人信息' : '新增老人'" width="500px">
      <el-form :model="dialogs.elderly.form" label-width="100px">
        <el-form-item label="老人ID">
          <el-input v-model="dialogs.elderly.form.elderly_id" :disabled="dialogs.elderly.isEdit" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="dialogs.elderly.form.name" />
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="dialogs.elderly.form.age" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="dialogs.elderly.form.gender">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属社区">
          <el-select v-model="dialogs.elderly.form.community_id">
            <el-option
              v-for="c in communitiesFullData"
              :key="c.community_id"
              :label="c.name"
              :value="c.community_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.elderly.visible = false">取消</el-button>
        <el-button type="primary" @click="submitElderly">提交</el-button>
      </template>
    </el-dialog>

    <!-- 护工弹窗 -->
    <el-dialog
      v-model="dialogs.caregiver.visible"
      title="新增护工"
      width="500px"
    >
      <el-form :model="dialogs.caregiver.form" label-width="100px">
        <el-form-item label="护工ID">
          <el-input v-model="dialogs.caregiver.form.caregiver_id" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="dialogs.caregiver.form.name" />
        </el-form-item>
        <el-form-item label="所属社区">
          <el-select v-model="dialogs.caregiver.form.community_id">
            <el-option
              v-for="c in communitiesFullData"
              :key="c.community_id"
              :label="c.name"
              :value="c.community_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="资质">
          <el-input v-model="dialogs.caregiver.form.qualification" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.caregiver.visible = false">取消</el-button>
        <el-button type="primary" @click="submitCaregiver">提交</el-button>
      </template>
    </el-dialog>

    <!-- 健康记录弹窗 -->
    <el-dialog
      v-model="dialogs.healthRecord.visible"
      title="上报健康记录"
      width="500px"
    >
      <el-form :model="dialogs.healthRecord.form" label-width="100px">
        <el-form-item label="老人ID">
          <el-input v-model="dialogs.healthRecord.form.elderly_id" />
        </el-form-item>
        <el-form-item label="记录日期">
          <el-date-picker
            v-model="dialogs.healthRecord.form.record_date"
            type="date"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="收缩压">
          <el-input-number v-model="dialogs.healthRecord.form.sbp" />
        </el-form-item>
        <el-form-item label="舒张压">
          <el-input-number v-model="dialogs.healthRecord.form.dbp" />
        </el-form-item>
        <el-form-item label="血糖">
          <el-input-number
            v-model="dialogs.healthRecord.form.blood_sugar"
            :precision="1"
            :step="0.1"
          />
        </el-form-item>
        <el-form-item label="心率">
          <el-input-number v-model="dialogs.healthRecord.form.heart_rate" />
        </el-form-item>
        <el-form-item label="健康状态">
          <el-select v-model="dialogs.healthRecord.form.health_status">
            <el-option label="良好" value="良好" />
            <el-option label="临界" value="临界" />
            <el-option label="高危" value="高危" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.healthRecord.visible = false"
          >取消</el-button
        >
        <el-button type="primary" @click="submitHealthRecord">提交</el-button>
      </template>
      </el-dialog>
    <!-- 排班弹窗 -->
    <el-dialog v-model="dialogs.schedule.visible" title="新增排班" width="500px">
      <el-form :model="dialogs.schedule.form" label-width="100px">
        <el-form-item label="护工ID">
          <el-select v-model="dialogs.schedule.form.caregiver_id">
            <el-option v-for="c in caregiversData" :key="c.caregiver_id" :label="c.name" :value="c.caregiver_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="老人ID">
          <el-input v-model="dialogs.schedule.form.elderly_id" />
        </el-form-item>
        <el-form-item label="服务类型">
          <el-select v-model="dialogs.schedule.form.service_type">
            <el-option v-for="s in services" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务日期">
          <el-date-picker v-model="dialogs.schedule.form.service_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="时间段">
          <el-input v-model="dialogs.schedule.form.service_time_slot" placeholder="如: 09:00-10:00" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.schedule.visible = false">取消</el-button>
        <el-button type="primary" @click="submitSchedule">提交</el-button>
      </template>
    </el-dialog>

    <!-- 服务记录弹窗 -->
    <el-dialog v-model="dialogs.serviceRecord.visible" title="提交服务记录" width="500px">
      <el-form :model="dialogs.serviceRecord.form" label-width="100px">
        <el-form-item label="老人ID">
          <el-input v-model="dialogs.serviceRecord.form.elderly_id" />
        </el-form-item>
        <el-form-item label="所属社区">
          <el-select v-model="dialogs.serviceRecord.form.community_id">
            <el-option v-for="c in communitiesFullData" :key="c.community_id" :label="c.name" :value="c.community_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务类型">
          <el-select v-model="dialogs.serviceRecord.form.service_type">
            <el-option v-for="s in services" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务日期">
          <el-date-picker v-model="dialogs.serviceRecord.form.service_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="时长(分钟)">
          <el-input-number v-model="dialogs.serviceRecord.form.duration" :min="1" />
        </el-form-item>
        <el-form-item label="满意度">
          <el-rate v-model="dialogs.serviceRecord.form.satisfaction" :max="5" />
        </el-form-item>
        <el-form-item label="护工ID">
          <el-input v-model="dialogs.serviceRecord.form.caregiver_id" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.serviceRecord.visible = false">取消</el-button>
        <el-button type="primary" @click="submitServiceRecord">提交</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import auth from "@/utils/auth";
import axios from "@/utils/http";
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

const currentUser = computed(() => auth.getCurrentUser());
const isInstitution = computed(() => currentUser.value?.role === "institution");
const isCaregiver = computed(() => currentUser.value?.role === "caregiver");
const isRegulatory = computed(() => currentUser.value?.role === "regulatory");

// 响应式数据
const stats = ref({
  senior_count: 0,
  health_records: 0,
  service_logs: 0,
  communities: 0,
  caregivers: 0,
});

const seniorsData = ref([]);
const totalSeniors = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const tableFilter = ref("all");
const communities = ref([]);

const healthRecords = ref([]);
const totalHealthRecords = ref(0);
const healthCurrentPage = ref(1);
const healthPageSize = ref(20);
const dateRange = ref([]);

const serviceRecords = ref([]);
const totalServiceRecords = ref(0);
const serviceCurrentPage = ref(1);
const servicePageSize = ref(20);
const serviceTypeFilter = ref("all");
const services = ref(["助餐", "助医", "保洁", "陪护", "康复"]);

const caregiversData = ref([]);
const schedulesData = ref([]);
const predictionsData = ref([]);
const communitiesFullData = ref([]);

// 弹窗状态管理
const dialogs = reactive({
  community: {
    visible: false,
    isEdit: false,
    form: {
      community_id: "",
      name: "",
      total_population: 0,
      elderly_population: 0,
    },
  },
  elderly: {
    visible: false,
    isEdit: false,
    form: { elderly_id: "", name: "", age: 70, gender: "男", community_id: "" },
  },
  caregiver: {
    visible: false,
    form: { caregiver_id: "", name: "", community_id: "", qualification: "" },
  },
  schedule: {
    visible: false,
    form: {
      caregiver_id: "",
      elderly_id: "",
      service_type: "助餐",
      service_date: "",
      service_time_slot: "",
    },
  },
  healthRecord: {
    visible: false,
    form: {
      elderly_id: "",
      record_date: "",
      sbp: 120,
      dbp: 80,
      blood_sugar: 5.0,
      heart_rate: 75,
      health_status: "良好",
    },
  },
  serviceRecord: {
    visible: false,
    form: {
      elderly_id: "",
      community_id: "",
      service_type: "助餐",
      service_date: "",
      duration: 60,
      satisfaction: 5,
      caregiver_id: "",
    },
  },
});

// 获取状态样式
const getHealthStatusType = (status: string) => {
  if (status === "良好" || status === "healthy") return "success";
  if (status === "临界" || status === "hypertension") return "warning";
  if (status === "高危" || status === "diabetes") return "danger";
  return "info";
};

// 刷新数据
const refreshData = async () => {
  try {
    const statsRes = await axios.get("/api/data/stats");
    stats.value = statsRes.data;

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

    loadSeniorsData();
    loadHealthRecords();
    loadServiceRecords();
  } catch (error) {
    console.error("加载数据失败:", error);
  }
};

const loadSeniorsData = async () => {
  const res = await axios.get("/api/data/seniors", {
    params: {
      page: currentPage.value,
      page_size: pageSize.value,
      community: tableFilter.value === "all" ? "" : tableFilter.value,
    },
  });
  seniorsData.value = res.data.items;
  totalSeniors.value = res.data.total;
};

const loadHealthRecords = async () => {
  const res = await axios.get("/api/data/health-records", {
    params: {
      page: healthCurrentPage.value,
      page_size: healthPageSize.value,
      start_date: dateRange.value?.[0] || "",
      end_date: dateRange.value?.[1] || "",
    },
  });
  healthRecords.value = res.data.items;
  totalHealthRecords.value = res.data.total;
};

const loadServiceRecords = async () => {
  const res = await axios.get("/api/data/service-records", {
    params: {
      page: serviceCurrentPage.value,
      page_size: servicePageSize.value,
      service_type:
        serviceTypeFilter.value === "all" ? "" : serviceTypeFilter.value,
    },
  });
  serviceRecords.value = res.data.items;
  totalServiceRecords.value = res.data.total;
};

// 提交逻辑
const submitCommunity = async () => {
  try {
    if (dialogs.community.isEdit) {
      await axios.put(
        `/api/data/communities/${dialogs.community.form.community_id}`,
        dialogs.community.form,
      );
    } else {
      await axios.post("/api/data/communities", dialogs.community.form);
    }
    ElMessage.success("保存成功");
    dialogs.community.visible = false;
    refreshData();
  } catch (e: any) {
    ElMessage.error(e.error || "保存失败");
  }
};

const handleEditCommunity = (row: any) => {
  dialogs.community.isEdit = true;
  dialogs.community.form = { ...row };
  dialogs.community.visible = true;
};

const handleDeleteCommunity = (id: string) => {
  ElMessageBox.confirm("确定删除该社区吗？", "提示", { type: "warning" }).then(
    async () => {
      try {
        await axios.delete(`/api/data/communities/${id}`);
        ElMessage.success("删除成功");
        refreshData();
      } catch (e: any) {
        ElMessage.error(e.error || "删除失败");
      }
    },
  );
};

const submitElderly = async () => {
  try {
    if (dialogs.elderly.isEdit) {
      await axios.put(`/api/data/seniors/${dialogs.elderly.form.elderly_id}`, dialogs.elderly.form);
    } else {
      await axios.post("/api/data/seniors", dialogs.elderly.form);
    }
    ElMessage.success("保存成功");
    dialogs.elderly.visible = false;
    refreshData();
  } catch (e: any) {
    ElMessage.error(e.error || "保存失败");
  }
};

const handleEditElderly = (row: any) => {
  dialogs.elderly.isEdit = true;
  dialogs.elderly.form = { ...row };
  dialogs.elderly.visible = true;
};

const handleDeleteElderly = (id: string) => {
  ElMessageBox.confirm('确定删除该老人信息吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      await axios.delete(`/api/data/seniors/${id}`);
      ElMessage.success("删除成功");
      refreshData();
    } catch (e: any) {
      ElMessage.error(e.error || "删除失败");
    }
  });
};

const submitCaregiver = async () => {
  try {
    await axios.post("/api/data/caregivers", dialogs.caregiver.form);
    ElMessage.success("添加成功");
    dialogs.caregiver.visible = false;
    refreshData();
  } catch (e: any) {
    ElMessage.error(e.error || "添加失败");
  }
};

const submitSchedule = async () => {
  try {
    await axios.post("/api/data/schedules", dialogs.schedule.form);
    ElMessage.success("排班成功");
    dialogs.schedule.visible = false;
    refreshData();
  } catch (e: any) {
    ElMessage.error(e.error || "排班失败");
  }
};

const submitHealthRecord = async () => {
  try {
    await axios.post("/api/data/health-records", dialogs.healthRecord.form);
    ElMessage.success("上报成功");
    dialogs.healthRecord.visible = false;
    refreshData();
  } catch (e: any) {
    ElMessage.error(e.error || "上报失败");
  }
};

const submitServiceRecord = async () => {
  try {
    await axios.post("/api/data/service-records", dialogs.serviceRecord.form);
    ElMessage.success("提交成功");
    dialogs.serviceRecord.visible = false;
    refreshData();
  } catch (e: any) {
    ElMessage.error(e.error || "提交失败");
  }
};

const showReportDialog = async () => {
  const res = await axios.get("/api/data/reports/community");
  ElMessageBox.alert(
    `<pre>${JSON.stringify(res.data, null, 2)}</pre>`,
    "社区全景统计报表",
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: "确定",
    },
  );
};

// 分页与筛选
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  loadSeniorsData();
};
const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  loadSeniorsData();
};
const filterHealthRecords = () => {
  healthCurrentPage.value = 1;
  loadHealthRecords();
};
const filterServiceRecords = () => {
  serviceCurrentPage.value = 1;
  loadServiceRecords();
};

onMounted(() => {
  refreshData();
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
