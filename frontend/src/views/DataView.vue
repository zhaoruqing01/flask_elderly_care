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
        <div class="stats-container">
          <div class="stat-item">
            <div class="stat-value">{{ stats.senior_count }}</div>
            <div class="stat-label">老人总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.health_records }}</div>
            <div class="stat-label">健康记录</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.service_logs }}</div>
            <div class="stat-label">服务记录</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.communities }}</div>
            <div class="stat-label">社区数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.caregivers }}</div>
            <div class="stat-label">护工总数</div>
          </div>
        </div>
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
        <div class="pagination" style="margin-top: 20px">
          <el-pagination
            v-model:current-page="predictionCurrentPage"
            v-model:page-size="predictionPageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalPredictions"
            @size-change="handlePredictionSizeChange"
            @current-change="handlePredictionCurrentChange"
          />
        </div>
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
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="handleEditCaregiver(scope.row)"
                >修改</el-button
              >
              <el-button
                size="small"
                type="danger"
                @click="handleDeleteCaregiver(scope.row.caregiver_id)"
                >删除</el-button
              >
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 排班管理 -->
      <!-- <el-card v-if="isInstitution || isCaregiver" style="margin-bottom: 20px">
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
      </el-card> -->

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
            @size-change="handleServiceSizeChange"
            @current-change="handleServiceCurrentChange"
          />
        </div>
      </el-card>
    </el-main>

    <!-- 弹窗部分 -->
    <!-- 社区弹窗 -->
    <el-dialog
      v-model="dialogs.community.visible"
      :title="dialogs.community.isEdit ? '编辑社区' : '新增社区'"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="communityFormRef"
        :model="dialogs.community.form"
        :rules="communityRules"
        label-width="100px"
      >
        <el-form-item label="社区ID" prop="community_id">
          <el-input
            v-model="dialogs.community.form.community_id"
            :disabled="dialogs.community.isEdit"
            placeholder="请输入社区ID，如: C006"
          />
        </el-form-item>
        <el-form-item label="社区名称" prop="name">
          <el-input
            v-model="dialogs.community.form.name"
            placeholder="请输入社区名称"
          />
        </el-form-item>
        <el-form-item label="总人口" prop="total_population">
          <el-input-number
            v-model="dialogs.community.form.total_population"
            :min="0"
            :max="100000"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="老年人口" prop="elderly_population">
          <el-input-number
            v-model="dialogs.community.form.elderly_population"
            :min="0"
            :max="dialogs.community.form.total_population"
            style="width: 100%"
          />
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            老年人口不能超过总人口
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.community.visible = false">取消</el-button>
        <el-button type="primary" @click="submitCommunity" :loading="submitting"
          >提交</el-button
        >
      </template>
    </el-dialog>

    <!-- 老人弹窗 -->
    <el-dialog
      v-model="dialogs.elderly.visible"
      :title="dialogs.elderly.isEdit ? '编辑老人信息' : '新增老人'"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="elderlyFormRef"
        :model="dialogs.elderly.form"
        :rules="elderlyRules"
        label-width="100px"
      >
        <el-form-item label="老人ID" prop="elderly_id">
          <el-input
            v-model="dialogs.elderly.form.elderly_id"
            :disabled="dialogs.elderly.isEdit"
            placeholder="请输入老人ID，如: E00011"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="dialogs.elderly.form.name"
            placeholder="请输入姓名"
          />
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number
            v-model="dialogs.elderly.form.age"
            :min="60"
            :max="120"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="dialogs.elderly.form.gender" style="width: 100%">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属社区" prop="community_id">
          <el-select
            v-model="dialogs.elderly.form.community_id"
            style="width: 100%"
            placeholder="请选择社区"
            filterable
          >
            <el-option
              v-for="c in communitiesFullData"
              :key="c.community_id"
              :label="`${c.name} (${c.community_id})`"
              :value="c.community_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.elderly.visible = false">取消</el-button>
        <el-button type="primary" @click="submitElderly" :loading="submitting"
          >提交</el-button
        >
      </template>
    </el-dialog>

    <!-- 护工弹窗 -->
    <el-dialog
      v-model="dialogs.caregiver.visible"
      :title="dialogs.caregiver.isEdit ? '编辑护工' : '新增护工'"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="caregiverFormRef"
        :model="dialogs.caregiver.form"
        :rules="caregiverRules"
        label-width="100px"
      >
        <el-form-item label="护工ID" prop="caregiver_id">
          <el-input
            v-model="dialogs.caregiver.form.caregiver_id"
            :disabled="dialogs.caregiver.isEdit"
            placeholder="请输入护工ID，如: CG006"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="dialogs.caregiver.form.name"
            placeholder="请输入姓名"
          />
        </el-form-item>
        <el-form-item label="所属社区" prop="community_id">
          <el-select
            v-model="dialogs.caregiver.form.community_id"
            style="width: 100%"
            placeholder="请选择社区"
            filterable
          >
            <el-option
              v-for="c in communitiesFullData"
              :key="c.community_id"
              :label="`${c.name} (${c.community_id})`"
              :value="c.community_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="资质" prop="qualification">
          <el-input
            v-model="dialogs.caregiver.form.qualification"
            placeholder="请输入资质，如: 初级护理员"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.caregiver.visible = false">取消</el-button>
        <el-button type="primary" @click="submitCaregiver" :loading="submitting"
          >提交</el-button
        >
      </template>
    </el-dialog>

    <!-- 健康记录弹窗 -->
    <el-dialog
      v-model="dialogs.healthRecord.visible"
      title="上报健康记录"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="healthRecordFormRef"
        :model="dialogs.healthRecord.form"
        :rules="healthRecordRules"
        label-width="100px"
      >
        <el-form-item label="老人ID" prop="elderly_id">
          <el-input
            v-model="dialogs.healthRecord.form.elderly_id"
            placeholder="请输入老人ID"
          />
        </el-form-item>
        <el-form-item label="记录日期" prop="record_date">
          <el-date-picker
            v-model="dialogs.healthRecord.form.record_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            placeholder="选择日期"
          />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="收缩压" prop="sbp">
              <el-input-number
                v-model="dialogs.healthRecord.form.sbp"
                :min="50"
                :max="250"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="舒张压" prop="dbp">
              <el-input-number
                v-model="dialogs.healthRecord.form.dbp"
                :min="30"
                :max="150"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="血糖" prop="blood_sugar">
              <el-input-number
                v-model="dialogs.healthRecord.form.blood_sugar"
                :precision="1"
                :step="0.1"
                :min="1"
                :max="30"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="心率" prop="heart_rate">
              <el-input-number
                v-model="dialogs.healthRecord.form.heart_rate"
                :min="40"
                :max="200"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="健康状态" prop="health_status">
          <el-select
            v-model="dialogs.healthRecord.form.health_status"
            style="width: 100%"
          >
            <el-option label="良好" value="良好">
              <span style="float: left">良好</span>
              <span style="float: right; color: #67c23a; font-size: 13px"
                >正常范围</span
              >
            </el-option>
            <el-option label="临界" value="临界">
              <span style="float: left">临界</span>
              <span style="float: right; color: #e6a23c; font-size: 13px"
                >需关注</span
              >
            </el-option>
            <el-option label="高危" value="高危">
              <span style="float: left">高危</span>
              <span style="float: right; color: #f56c6c; font-size: 13px"
                >立即处理</span
              >
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.healthRecord.visible = false"
          >取消</el-button
        >
        <el-button
          type="primary"
          @click="submitHealthRecord"
          :loading="submitting"
          >提交</el-button
        >
      </template>
    </el-dialog>

    <!-- 排班弹窗 -->
    <el-dialog
      v-model="dialogs.schedule.visible"
      title="新增排班"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="scheduleFormRef"
        :model="dialogs.schedule.form"
        :rules="scheduleRules"
        label-width="100px"
      >
        <el-form-item label="护工" prop="caregiver_id">
          <el-select
            v-model="dialogs.schedule.form.caregiver_id"
            style="width: 100%"
            placeholder="请选择护工"
            filterable
          >
            <el-option
              v-for="c in caregiversData"
              :key="c.caregiver_id"
              :label="`${c.name} (${c.caregiver_id})`"
              :value="c.caregiver_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="老人ID" prop="elderly_id">
          <el-input
            v-model="dialogs.schedule.form.elderly_id"
            placeholder="请输入老人ID"
          />
        </el-form-item>
        <el-form-item label="服务类型" prop="service_type">
          <el-select
            v-model="dialogs.schedule.form.service_type"
            style="width: 100%"
          >
            <el-option v-for="s in services" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务日期" prop="service_date">
          <el-date-picker
            v-model="dialogs.schedule.form.service_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            placeholder="选择日期"
          />
        </el-form-item>
        <el-form-item label="时间段" prop="service_time_slot">
          <el-input
            v-model="dialogs.schedule.form.service_time_slot"
            placeholder="如: 09:00-10:00"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.schedule.visible = false">取消</el-button>
        <el-button type="primary" @click="submitSchedule" :loading="submitting"
          >提交</el-button
        >
      </template>
    </el-dialog>

    <!-- 服务记录弹窗 -->
    <el-dialog
      v-model="dialogs.serviceRecord.visible"
      title="提交服务记录"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="serviceRecordFormRef"
        :model="dialogs.serviceRecord.form"
        :rules="serviceRecordRules"
        label-width="100px"
      >
        <el-form-item label="老人ID" prop="elderly_id">
          <el-input
            v-model="dialogs.serviceRecord.form.elderly_id"
            placeholder="请输入老人ID"
          />
        </el-form-item>
        <el-form-item label="所属社区" prop="community_id">
          <el-select
            v-model="dialogs.serviceRecord.form.community_id"
            style="width: 100%"
            placeholder="请选择社区"
            filterable
          >
            <el-option
              v-for="c in communitiesFullData"
              :key="c.community_id"
              :label="`${c.name} (${c.community_id})`"
              :value="c.community_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="服务类型" prop="service_type">
          <el-select
            v-model="dialogs.serviceRecord.form.service_type"
            style="width: 100%"
          >
            <el-option v-for="s in services" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务日期" prop="service_date">
          <el-date-picker
            v-model="dialogs.serviceRecord.form.service_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            placeholder="选择日期"
          />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="时长(分钟)" prop="duration">
              <el-input-number
                v-model="dialogs.serviceRecord.form.duration"
                :min="1"
                :max="480"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="满意度" prop="satisfaction">
              <el-rate
                v-model="dialogs.serviceRecord.form.satisfaction"
                :max="5"
                show-score
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="护工ID" prop="caregiver_id">
          <el-input
            v-model="dialogs.serviceRecord.form.caregiver_id"
            placeholder="请输入护工ID（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.serviceRecord.visible = false"
          >取消</el-button
        >
        <el-button
          type="primary"
          @click="submitServiceRecord"
          :loading="submitting"
          >提交</el-button
        >
      </template>
    </el-dialog>

    <!-- 报表对话框 -->
    <el-dialog
      v-model="reportDialogVisible"
      title="社区全景统计报表"
      width="90%"
      :close-on-click-modal="false"
      class="report-dialog"
      top="20px"
    >
      <div class="report-container">
        <div class="chart-section">
          <h3 class="chart-title">健康状态分布</h3>
          <div ref="healthChartRef" class="chart-wrapper"></div>
        </div>
        <div class="chart-section">
          <h3 class="chart-title">人口统计</h3>
          <div ref="populationChartRef" class="chart-wrapper"></div>
        </div>
        <div class="chart-section">
          <h3 class="chart-title">服务统计</h3>
          <div ref="serviceChartRef" class="chart-wrapper large"></div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="reportDialogVisible = false"
          >关闭</el-button
        >
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import auth from "@/utils/auth";
import axios from "@/utils/http";
import * as echarts from "echarts";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
} from "element-plus";
import { computed, nextTick, onMounted, reactive, ref, watch } from "vue";

const currentUser = computed(() => auth.getCurrentUser());
const isInstitution = computed(() => currentUser.value?.role === "institution");
const isCaregiver = computed(() => currentUser.value?.role === "caregiver");
const isRegulatory = computed(() => currentUser.value?.role === "regulatory");

// 表单引用
const communityFormRef = ref<FormInstance>();
const elderlyFormRef = ref<FormInstance>();
const caregiverFormRef = ref<FormInstance>();
const healthRecordFormRef = ref<FormInstance>();
const scheduleFormRef = ref<FormInstance>();
const serviceRecordFormRef = ref<FormInstance>();

// 提交状态
const submitting = ref(false);

// 响应式数据
const stats = ref({
  senior_count: 0,
  health_records: 0,
  service_logs: 0,
  communities: 0,
  caregivers: 0,
});

// 报表对话框
const reportDialogVisible = ref(false);
const healthChartRef = ref<HTMLElement>();
const populationChartRef = ref<HTMLElement>();
const serviceChartRef = ref<HTMLElement>();

const seniorsData = ref([]);
const totalSeniors = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const tableFilter = ref("all");
const communities = ref([]);

const healthRecords = ref([]);
const totalHealthRecords = ref(0);
const healthCurrentPage = ref(1);
const healthPageSize = ref(10);
const dateRange = ref([]);

const serviceRecords = ref([]);
const totalServiceRecords = ref(0);
const serviceCurrentPage = ref(1);
const servicePageSize = ref(10);
const serviceTypeFilter = ref("all");
const services = ref(["助餐", "助医", "保洁", "陪护", "康复"]);

const caregiversData = ref([]);
const schedulesData = ref([]);
const predictionsData = ref([]);
const totalPredictions = ref(0);
const predictionCurrentPage = ref(1);
const predictionPageSize = ref(10);
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
    isEdit: false,
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

// 表单验证规则
const communityRules: FormRules = {
  community_id: [
    { required: true, message: "请输入社区ID", trigger: "blur" },
    {
      pattern: /^C\d+$/,
      message: "社区ID格式不正确，如: C006",
      trigger: "blur",
    },
  ],
  name: [{ required: true, message: "请输入社区名称", trigger: "blur" }],
  total_population: [
    { required: true, message: "请输入总人口", trigger: "blur" },
  ],
  elderly_population: [
    { required: true, message: "请输入老年人口", trigger: "blur" },
  ],
};

const elderlyRules: FormRules = {
  elderly_id: [
    { required: true, message: "请输入老人ID", trigger: "blur" },
    {
      pattern: /^E\d+$/,
      message: "老人ID格式不正确，如: E00011",
      trigger: "blur",
    },
  ],
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  age: [{ required: true, message: "请输入年龄", trigger: "blur" }],
  gender: [{ required: true, message: "请选择性别", trigger: "change" }],
  community_id: [
    { required: true, message: "请选择所属社区", trigger: "change" },
  ],
};

const caregiverRules: FormRules = {
  caregiver_id: [
    { required: true, message: "请输入护工ID", trigger: "blur" },
    {
      pattern: /^CG\d+$/,
      message: "护工ID格式不正确，如: CG006",
      trigger: "blur",
    },
  ],
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  community_id: [
    { required: true, message: "请选择所属社区", trigger: "change" },
  ],
};

const healthRecordRules: FormRules = {
  elderly_id: [{ required: true, message: "请输入老人ID", trigger: "blur" }],
  record_date: [
    { required: true, message: "请选择记录日期", trigger: "change" },
  ],
  sbp: [{ required: true, message: "请输入收缩压", trigger: "blur" }],
  dbp: [{ required: true, message: "请输入舒张压", trigger: "blur" }],
  blood_sugar: [{ required: true, message: "请输入血糖值", trigger: "blur" }],
  heart_rate: [{ required: true, message: "请输入心率", trigger: "blur" }],
  health_status: [
    { required: true, message: "请选择健康状态", trigger: "change" },
  ],
};

const scheduleRules: FormRules = {
  caregiver_id: [{ required: true, message: "请选择护工", trigger: "change" }],
  elderly_id: [{ required: true, message: "请输入老人ID", trigger: "blur" }],
  service_type: [
    { required: true, message: "请选择服务类型", trigger: "change" },
  ],
  service_date: [
    { required: true, message: "请选择服务日期", trigger: "change" },
  ],
  service_time_slot: [
    { required: true, message: "请输入时间段", trigger: "blur" },
    {
      pattern: /^\d{2}:\d{2}-\d{2}:\d{2}$/,
      message: "时间格式不正确，如: 09:00-10:00",
      trigger: "blur",
    },
  ],
};

const serviceRecordRules: FormRules = {
  elderly_id: [{ required: true, message: "请输入老人ID", trigger: "blur" }],
  community_id: [
    { required: true, message: "请选择所属社区", trigger: "change" },
  ],
  service_type: [
    { required: true, message: "请选择服务类型", trigger: "change" },
  ],
  service_date: [
    { required: true, message: "请选择服务日期", trigger: "change" },
  ],
  duration: [{ required: true, message: "请输入服务时长", trigger: "blur" }],
  satisfaction: [
    { required: true, message: "请评价满意度", trigger: "change" },
  ],
};

// 获取当前用户角色
const getUserRole = () => {
  return currentUser.value?.role || "admin";
};

// 排班管理状态字典
const scheduleStatusDict: Record<string, string> = {
  pending: "待处理",
  completed: "已处理",
  canceled: "已取消",
};

// 刷新数据
const refreshData = async () => {
  try {
    const role = getUserRole();
    const statsRes = await axios.get("/api/data/stats", { params: { role } });
    stats.value = statsRes.data;

    const commRes = await axios.get("/api/data/communities", {
      params: { role },
    });
    communitiesFullData.value = commRes.data;
    communities.value = commRes.data.map((c: any) => c.name);

    // 加载预测数据
    await loadPredictions();

    if (isInstitution.value || isCaregiver.value) {
      const cgRes = await axios.get("/api/data/caregivers", {
        params: { role },
      });
      caregiversData.value = cgRes.data;

      const schRes = await axios.get("/api/data/schedules", {
        params: isCaregiver.value
          ? { caregiver_id: currentUser.value?.username, role }
          : { role },
      });
      schedulesData.value = schRes.data.map((s: any) => ({
        ...s,
        status: scheduleStatusDict[s.status],
      }));
    }

    loadSeniorsData();
    loadHealthRecords();
    loadServiceRecords();
    loadPredictions();
    ElMessage.success("刷新数据成功");
  } catch (error) {
    console.error("加载数据失败:", error);
  }
};

const loadSeniorsData = async () => {
  const role = getUserRole();
  const res = await axios.get("/api/data/seniors", {
    params: {
      page: currentPage.value,
      page_size: pageSize.value,
      community: tableFilter.value === "all" ? "" : tableFilter.value,
      role,
    },
  });
  seniorsData.value = res.data.items;
  totalSeniors.value = res.data.total;
};

const loadHealthRecords = async () => {
  const role = getUserRole();
  const res = await axios.get("/api/data/health-records", {
    params: {
      page: healthCurrentPage.value,
      page_size: healthPageSize.value,
      start_date: dateRange.value?.[0] || "",
      end_date: dateRange.value?.[1] || "",
      role,
    },
  });
  healthRecords.value = res.data.items;
  totalHealthRecords.value = res.data.total;
};

const loadServiceRecords = async () => {
  const role = getUserRole();
  const res = await axios.get("/api/data/service-records", {
    params: {
      page: serviceCurrentPage.value,
      page_size: servicePageSize.value,
      service_type:
        serviceTypeFilter.value === "all" ? "" : serviceTypeFilter.value,
      role,
    },
  });
  serviceRecords.value = res.data.items;
  totalServiceRecords.value = res.data.total;
};

const loadPredictions = async () => {
  const role = getUserRole();
  const res = await axios.get("/api/data/predictions", {
    params: {
      page: predictionCurrentPage.value,
      page_size: predictionPageSize.value,
      role,
    },
  });
  predictionsData.value = res.data.items;
  totalPredictions.value = res.data.total;
};

// 提交逻辑
const submitCommunity = async () => {
  if (!communityFormRef.value) return;

  await communityFormRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;
    try {
      const role = getUserRole();
      if (dialogs.community.isEdit) {
        await axios.put(
          `/api/data/communities/${dialogs.community.form.community_id}?role=${role}`,
          dialogs.community.form,
        );
      } else {
        await axios.post(
          `/api/data/communities?role=${role}`,
          dialogs.community.form,
        );
      }
      ElMessage.success("保存成功");
      dialogs.community.visible = false;
      refreshData();
    } catch (e: any) {
      ElMessage.error(e.response?.data?.error || e.error || "保存失败");
    } finally {
      submitting.value = false;
    }
  });
};

const handleEditCommunity = (row: any) => {
  dialogs.community.isEdit = true;
  dialogs.community.form = { ...row };
  dialogs.community.visible = true;
};

const handleDeleteCommunity = (id: string) => {
  const role = getUserRole();
  ElMessageBox.confirm("确定删除该社区吗？", "提示", { type: "warning" }).then(
    async () => {
      try {
        await axios.delete(`/api/data/communities/${id}?role=${role}`);
        ElMessage.success("删除成功");
        refreshData();
      } catch (e: any) {
        ElMessage.error(e.response?.data?.error || e.error || "删除失败");
      }
    },
  );
};

const submitElderly = async () => {
  if (!elderlyFormRef.value) return;

  await elderlyFormRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;
    try {
      const role = getUserRole();
      if (dialogs.elderly.isEdit) {
        await axios.put(
          `/api/data/seniors/${dialogs.elderly.form.elderly_id}?role=${role}`,
          dialogs.elderly.form,
        );
      } else {
        await axios.post(
          `/api/data/seniors?role=${role}`,
          dialogs.elderly.form,
        );
      }
      ElMessage.success("保存成功");
      dialogs.elderly.visible = false;
      refreshData();
    } catch (e: any) {
      ElMessage.error(e.response?.data?.error || e.error || "保存失败");
    } finally {
      submitting.value = false;
    }
  });
};

const handleEditElderly = (row: any) => {
  dialogs.elderly.isEdit = true;
  dialogs.elderly.form = { ...row };
  dialogs.elderly.visible = true;
};

const handleDeleteElderly = (id: string) => {
  const role = getUserRole();
  ElMessageBox.confirm("确定删除该老人信息吗？", "提示", {
    type: "warning",
  }).then(async () => {
    try {
      await axios.delete(`/api/data/seniors/${id}?role=${role}`);
      ElMessage.success("删除成功");
      refreshData();
    } catch (e: any) {
      ElMessage.error(e.response?.data?.error || e.error || "删除失败");
    }
  });
};

const submitCaregiver = async () => {
  if (!caregiverFormRef.value) return;

  await caregiverFormRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;
    try {
      const role = getUserRole();
      if (dialogs.caregiver.isEdit) {
        await axios.put(
          `/api/data/caregivers/${dialogs.caregiver.form.caregiver_id}?role=${role}`,
          dialogs.caregiver.form,
        );
      } else {
        await axios.post(
          `/api/data/caregivers?role=${role}`,
          dialogs.caregiver.form,
        );
      }
      ElMessage.success(dialogs.caregiver.isEdit ? "修改成功" : "添加成功");
      dialogs.caregiver.visible = false;
      refreshData();
    } catch (e: any) {
      ElMessage.error(e.response?.data?.error || e.error || "操作失败");
    } finally {
      submitting.value = false;
    }
  });
};

const handleEditCaregiver = (row: any) => {
  dialogs.caregiver.isEdit = true;
  dialogs.caregiver.form = { ...row };
  dialogs.caregiver.visible = true;
};

const handleDeleteCaregiver = (id: string) => {
  const role = getUserRole();
  ElMessageBox.confirm("确定删除该护工吗？", "提示", { type: "warning" }).then(
    async () => {
      try {
        await axios.delete(`/api/data/caregivers/${id}?role=${role}`);
        ElMessage.success("删除成功");
        refreshData();
      } catch (e: any) {
        ElMessage.error(e.response?.data?.error || e.error || "删除失败");
      }
    },
  );
};

const submitSchedule = async () => {
  if (!scheduleFormRef.value) return;

  await scheduleFormRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;
    try {
      const role = getUserRole();
      await axios.post(
        `/api/data/schedules?role=${role}`,
        dialogs.schedule.form,
      );
      ElMessage.success("排班成功");
      dialogs.schedule.visible = false;
      refreshData();
    } catch (e: any) {
      ElMessage.error(e.response?.data?.error || e.error || "排班失败");
    } finally {
      submitting.value = false;
    }
  });
};

const submitHealthRecord = async () => {
  if (!healthRecordFormRef.value) return;

  await healthRecordFormRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;
    try {
      const role = getUserRole();
      await axios.post(
        `/api/data/health-records?role=${role}`,
        dialogs.healthRecord.form,
      );
      ElMessage.success("上报成功");
      dialogs.healthRecord.visible = false;
      refreshData();
    } catch (e: any) {
      ElMessage.error(e.response?.data?.error || e.error || "上报失败");
    } finally {
      submitting.value = false;
    }
  });
};

const submitServiceRecord = async () => {
  if (!serviceRecordFormRef.value) return;

  await serviceRecordFormRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;
    try {
      const role = getUserRole();
      await axios.post(
        `/api/data/service-records?role=${role}`,
        dialogs.serviceRecord.form,
      );
      ElMessage.success("提交成功");
      dialogs.serviceRecord.visible = false;
      refreshData();
    } catch (e: any) {
      ElMessage.error(e.response?.data?.error || e.error || "提交失败");
    } finally {
      submitting.value = false;
    }
  });
};

const showReportDialog = async () => {
  const role = getUserRole();
  const res = await axios.get("/api/data/reports/community", {
    params: { role },
  });

  // 显示对话框
  reportDialogVisible.value = true;

  // 等待 DOM 更新后初始化图表
  await nextTick();

  // 初始化健康状态分布图
  if (healthChartRef.value) {
    initHealthChart(healthChartRef.value, res.data.health);
  }

  // 初始化人口统计图
  if (populationChartRef.value) {
    initPopulationChart(populationChartRef.value, res.data.population);
  }

  // 初始化服务统计图
  if (serviceChartRef.value) {
    initServiceChart(serviceChartRef.value, res.data.service);
  }
};

// 初始化健康状态分布图
const initHealthChart = (chartDom: HTMLElement, healthData: any[]) => {
  const myChart = echarts.init(chartDom);

  // 提取社区名称和健康状态
  const communities = [...new Set(healthData.map((item) => item[0]))];
  const statuses = ["良好", "临界", "高危"];
  const colors = ["#67c23a", "#e6a23c", "#f56c6c"];

  const series = statuses.map((status, index) => ({
    name: status,
    type: "bar",
    stack: "total",
    data: communities.map((community) => {
      const item = healthData.find(
        (d) => d[0] === community && d[1] === status,
      );
      return item ? item[2] : 0;
    }),
    itemStyle: {
      color: colors[index],
    },
  }));

  const option = {
    title: {
      text: "各社区健康状态分布",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: "#303133",
      },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      backgroundColor: "rgba(255, 255, 255, 0.95)",
      borderColor: "#e4e7ed",
      textStyle: {
        color: "#606266",
      },
    },
    legend: {
      data: statuses,
      top: 35,
      itemWidth: 15,
      itemHeight: 10,
      textStyle: {
        color: "#606266",
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      top: "80px",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: communities,
      axisLine: {
        lineStyle: {
          color: "#dcdfe6",
        },
      },
      axisLabel: {
        color: "#606266",
      },
    },
    yAxis: {
      type: "value",
      name: "人数",
      nameTextStyle: {
        color: "#909399",
      },
      axisLine: {
        lineStyle: {
          color: "#dcdfe6",
        },
      },
      axisLabel: {
        color: "#606266",
      },
      splitLine: {
        lineStyle: {
          color: "#ebeef5",
          type: "dashed",
        },
      },
    },
    series: series,
    animationDuration: 1000,
  };

  myChart.setOption(option);

  // 响应式调整
  window.addEventListener("resize", () => myChart.resize());
};

// 初始化人口统计图
const initPopulationChart = (chartDom: HTMLElement, populationData: any[]) => {
  const myChart = echarts.init(chartDom);

  const communities = populationData.map((item) => item.name);
  const totalPopulations = populationData.map((item) => item.total);
  const elderlyPopulations = populationData.map((item) => item.elderly);

  const option = {
    title: {
      text: "各社区人口统计",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: "#303133",
      },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      backgroundColor: "rgba(255, 255, 255, 0.95)",
      borderColor: "#e4e7ed",
      textStyle: {
        color: "#606266",
      },
    },
    legend: {
      data: ["总人口", "老年人口"],
      top: 35,
      itemWidth: 15,
      itemHeight: 10,
      textStyle: {
        color: "#606266",
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      top: "80px",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: communities,
      axisLine: {
        lineStyle: {
          color: "#dcdfe6",
        },
      },
      axisLabel: {
        color: "#606266",
      },
    },
    yAxis: {
      type: "value",
      name: "人数",
      nameTextStyle: {
        color: "#909399",
      },
      axisLine: {
        lineStyle: {
          color: "#dcdfe6",
        },
      },
      axisLabel: {
        color: "#606266",
      },
      splitLine: {
        lineStyle: {
          color: "#ebeef5",
          type: "dashed",
        },
      },
    },
    series: [
      {
        name: "总人口",
        type: "bar",
        data: totalPopulations,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#66b1ff" },
            { offset: 1, color: "#409eff" },
          ]),
        },
        barMaxWidth: 50,
      },
      {
        name: "老年人口",
        type: "bar",
        data: elderlyPopulations,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#95d475" },
            { offset: 1, color: "#67c23a" },
          ]),
        },
        barMaxWidth: 50,
      },
    ],
    animationDuration: 1000,
  };

  myChart.setOption(option);

  // 响应式调整
  window.addEventListener("resize", () => myChart.resize());
};

// 初始化服务统计图
const initServiceChart = (chartDom: HTMLElement, serviceData: any[]) => {
  const myChart = echarts.init(chartDom);

  // 提取社区和服务类型
  const communities = [...new Set(serviceData.map((item) => item[0]))];
  const serviceTypes = [...new Set(serviceData.map((item) => item[1]))];

  // 为每个服务类型创建系列
  const series = serviceTypes.map((serviceType) => ({
    name: serviceType,
    type: "bar",
    data: communities.map((community) => {
      const item = serviceData.find(
        (d) => d[0] === community && d[1] === serviceType,
      );
      return item ? item[2] : 0;
    }),
  }));

  const option = {
    title: {
      text: "各社区服务统计",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: "#303133",
      },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      backgroundColor: "rgba(255, 255, 255, 0.95)",
      borderColor: "#e4e7ed",
      textStyle: {
        color: "#606266",
      },
    },
    legend: {
      data: serviceTypes,
      top: 35,
      itemWidth: 15,
      itemHeight: 10,
      textStyle: {
        color: "#606266",
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      top: "80px",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: communities,
      axisLine: {
        lineStyle: {
          color: "#dcdfe6",
        },
      },
      axisLabel: {
        color: "#606266",
      },
    },
    yAxis: {
      type: "value",
      name: "服务次数",
      nameTextStyle: {
        color: "#909399",
      },
      axisLine: {
        lineStyle: {
          color: "#dcdfe6",
        },
      },
      axisLabel: {
        color: "#606266",
      },
      splitLine: {
        lineStyle: {
          color: "#ebeef5",
          type: "dashed",
        },
      },
    },
    series: series.map((s) => ({
      ...s,
      barMaxWidth: 40,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
      },
    })),
    animationDuration: 1000,
  };

  myChart.setOption(option);

  // 响应式调整
  window.addEventListener("resize", () => myChart.resize());
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
const handleHealthSizeChange = (val: number) => {
  healthPageSize.value = val;
  loadHealthRecords();
};
const handleHealthCurrentChange = (val: number) => {
  healthCurrentPage.value = val;
  loadHealthRecords();
};
const handleServiceSizeChange = (val: number) => {
  servicePageSize.value = val;
  loadServiceRecords();
};
const handleServiceCurrentChange = (val: number) => {
  serviceCurrentPage.value = val;
  loadServiceRecords();
};
const handlePredictionSizeChange = (val: number) => {
  predictionPageSize.value = val;
  loadPredictions();
};
const handlePredictionCurrentChange = (val: number) => {
  predictionCurrentPage.value = val;
  loadPredictions();
};
const filterHealthRecords = () => {
  healthCurrentPage.value = 1;
  loadHealthRecords();
};
const filterServiceRecords = () => {
  serviceCurrentPage.value = 1;
  loadServiceRecords();
};

// 监听筛选条件变化
watch(tableFilter, () => {
  currentPage.value = 1;
  loadSeniorsData();
});

watch(serviceTypeFilter, () => {
  serviceCurrentPage.value = 1;
  loadServiceRecords();
});

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

.stats-container {
  display: flex;
  justify-content: space-around;
  gap: 10px;
}

.stat-item {
  background-color: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border-left: 4px solid #0066cc;
  transition: transform 0.2s ease;
  flex: 1;
  min-width: 0;
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

/* 报表对话框样式 */
.report-dialog :deep(.el-dialog) {
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.report-dialog :deep(.el-dialog__body) {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.report-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.chart-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.chart-section:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.chart-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  padding-left: 12px;
  border-left: 4px solid #409eff;
}

.chart-wrapper {
  width: 100%;
  height: 400px;
}

.chart-wrapper.large {
  height: 500px;
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
