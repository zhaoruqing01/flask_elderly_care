<template>
  <el-container class="login-page">
    <el-main>
      <div class="card-wrap">
        <el-card class="login-card">
          <!-- 品牌标题 -->
          <div class="brand">
            <h1>养老服务平台</h1>
            <p class="subtitle">智慧养老服务大数据分析系统</p>
          </div>

          <!-- 登录表单：动态显示 -->
          <el-form
            v-if="isLogin"
            :model="form"
            ref="formRef"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="用户名"
                prefix-icon="User"
                @keyup.enter.prevent="handleLogin"
              ></el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="密码"
                prefix-icon="Lock"
                show-password
                @keyup.enter.prevent="handleLogin"
              ></el-input>
            </el-form-item>
            <!-- 
            <div class="helpers">
              <el-button type="text" @click="toggleForm"
                >没有账号？注册</el-button
              >
            </div> -->

            <div class="actions">
              <el-button
                type="primary"
                @click="handleLogin"
                style="width: 100%"
              >
                登录
              </el-button>
            </div>

            <div class="quick-login">
              <el-button
                type="info"
                plain
                @click="showRoleDialog = true"
                style="width: 100%"
              >
                <el-icon><UserFilled /></el-icon>
                快速登录（选择角色）
              </el-button>
            </div>
          </el-form>

          <!-- 注册表单：动态显示 -->
          <el-form
            v-else
            :model="reg"
            class="reg-form"
            @submit.prevent="handleRegister"
          >
            <el-form-item>
              <el-input
                v-model="reg.username"
                placeholder="注册用户名"
                prefix-icon="User"
                @keyup.enter.prevent="handleRegister"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="reg.password"
                type="password"
                placeholder="密码（至少6位）"
                prefix-icon="Lock"
                show-password
                @keyup.enter.prevent="handleRegister"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="reg.confirm"
                type="password"
                placeholder="确认密码"
                prefix-icon="Lock"
                show-password
                @keyup.enter.prevent="handleRegister"
              ></el-input>
            </el-form-item>

            <div class="actions">
              <el-button
                type="success"
                @click="handleRegister"
                style="width: 100%"
              >
                注册并登录
              </el-button>
              <el-button @click="toggleForm" style="width: 100%">
                返回登录
              </el-button>
            </div>
          </el-form>
        </el-card>
      </div>
    </el-main>

    <!-- 角色选择弹窗 -->
    <el-dialog
      v-model="showRoleDialog"
      title="选择登录角色"
      width="900px"
      :close-on-click-modal="false"
      class="role-dialog"
      align-center
      :lock-scroll="true"
    >
      <div class="role-selection">
        <el-row :gutter="16">
          <el-col :span="24" v-for="role in roleList" :key="role.role">
            <el-card
              class="role-card"
              :class="{ 'role-card-selected': selectedRole === role.role }"
              @click="selectRole(role)"
              shadow="hover"
              body-style="padding: 12px;"
            >
              <div class="role-header">
                <el-icon class="role-icon" :class="`icon-${role.role}`">
                  <component :is="role.icon" />
                </el-icon>
                <div class="role-title">
                  <h3>{{ role.name }}</h3>
                  <el-tag :type="role.tagType" size="small">{{
                    role.role
                  }}</el-tag>
                </div>
              </div>

              <div class="role-info">
                <div class="info-section">
                  <h4>
                    <el-icon><Key /></el-icon> 默认账号
                  </h4>
                  <p>
                    <strong>用户名：</strong>{{ role.username }} |
                    <strong>密码：</strong>{{ role.password }}
                  </p>
                </div>

                <div class="info-section compact">
                  <h4>
                    <el-icon><Collection /></el-icon> 核心功能
                  </h4>
                  <el-tooltip
                    v-if="role.features.length > 4"
                    placement="top"
                    effect="light"
                    :show-after="300"
                  >
                    <template #content>
                      <div class="tooltip-content">
                        <div
                          v-for="feature in role.features"
                          :key="feature"
                          class="tooltip-item"
                        >
                          {{ feature }}
                        </div>
                      </div>
                    </template>
                    <ul class="feature-list">
                      <li
                        v-for="feature in role.features.slice(0, 4)"
                        :key="feature"
                      >
                        {{ feature }}
                      </li>
                      <li class="more-text">
                        等{{ role.features.length }}项功能...
                      </li>
                    </ul>
                  </el-tooltip>
                  <ul v-else class="feature-list">
                    <li v-for="feature in role.features" :key="feature">
                      {{ feature }}
                    </li>
                  </ul>
                </div>

                <div class="info-section compact">
                  <h4>
                    <el-icon><Lock /></el-icon> 权限范围
                  </h4>
                  <div class="perm-tags">
                    <el-tag
                      v-for="perm in role.permissions"
                      :key="perm"
                      size="small"
                    >
                      {{ perm }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <template #footer>
        <el-button @click="showRoleDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="confirmQuickLogin"
          :disabled="!selectedRole"
        >
          确认登录
        </el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import auth from "@/utils/auth";
import { ElMessage } from "element-plus";
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();

// 登录表单数据
const form = ref({ username: "", password: "" });
// 注册表单数据
const reg = ref({ username: "", password: "", confirm: "" });
// 表单ref
const formRef = ref();
// 动态控制：true=显示登录，false=显示注册
const isLogin = ref(true);

// 角色选择弹窗
const showRoleDialog = ref(false);
const selectedRole = ref("");

// 角色列表配置
const roleList = [
  {
    role: "institution",
    name: "机构管理员",
    username: "admin",
    password: "123456",
    icon: "Management",
    tagType: "danger",
    features: [
      "管理社区信息（增删改查）",
      "管理老人档案（增删改查）",
      "管理护工信息（新增/查看）",
      "查看所有健康记录",
      "查看所有服务记录",
      "查看需求预测结果",
      "生成和清洗数据",
      "训练机器学习模型",
      "查看社区全景统计报表",
    ],
    permissions: ["数据管理", "护工管理", "系统配置", "报表查看"],
  },
  {
    role: "caregiver",
    name: "护工",
    username: "caregiver1",
    password: "123456",
    icon: "Service",
    tagType: "warning",
    features: [
      "上报老人健康记录",
      "提交服务完成记录",
      "查看负责的老人信息",
      "查看健康统计数据",
      "查看服务统计数据",
    ],
    permissions: ["健康上报", "服务记录", "需求预测"],
  },
  {
    role: "regulatory",
    name: "监管部门",
    username: "gov",
    password: "123456",
    icon: "Monitor",
    tagType: "success",
    features: [
      "查看全区老人总数统计",
      "查看健康状态分布",
      "查看服务使用频次",
      "查看服务满意度分析",
      "查看社区对比数据",
      "查看社区全景统计报表",
      "查看需求预测趋势",
    ],
    permissions: ["数据查看", "统计分析", "报表导出"],
  },
];

// 选择角色
function selectRole(role: any) {
  selectedRole.value = role.role;
}

// 确认快速登录
async function confirmQuickLogin() {
  const role = roleList.find((r) => r.role === selectedRole.value);
  if (!role) return;

  form.value.username = role.username;
  form.value.password = role.password;

  showRoleDialog.value = false;

  // 自动登录
  const ok = await auth.login(form.value.username, form.value.password);
  if (ok) {
    ElMessage.success(`以 ${role.name} 身份登录成功`);
    // 如果有重定向参数，跳转到目标页面，否则跳转到首页
    const redirect = (route.query.redirect as string) || "/";
    router.push({ path: redirect });
  } else {
    ElMessage.error("登录失败，请检查账号是否存在");
  }
}

// 登录处理
async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning("请填写用户名和密码");
    return;
  }
  const ok = await auth.login(form.value.username, form.value.password);
  if (ok) {
    ElMessage.success("登录成功");
    // 如果有重定向参数，跳转到目标页面，否则跳转到首页
    const redirect = (route.query.redirect as string) || "/";
    router.push({ path: redirect });
  } else {
    ElMessage.error("用户名或密码错误");
  }
}

// 注册处理
async function handleRegister() {
  if (!reg.value.username || reg.value.password.length < 6) {
    ElMessage.warning("用户名不能为空，且密码至少6位");
    return;
  }
  if (reg.value.password !== reg.value.confirm) {
    ElMessage.warning("两次密码不一致");
    return;
  }
  const ok = await auth.register(reg.value.username, reg.value.password);
  if (ok) {
    ElMessage.success("注册并登录成功");
    // 如果有重定向参数，跳转到目标页面，否则跳转到首页
    const redirect = (route.query.redirect as string) || "/";
    router.push({ path: redirect });
  } else {
    ElMessage.error("用户名已存在或注册失败");
  }
}

// 切换登录/注册表单（清空表单数据，避免残留）
function toggleForm() {
  isLogin.value = !isLogin.value;
  // 切换时清空输入框
  if (isLogin.value) {
    reg.value = { username: "", password: "", confirm: "" };
  } else {
    form.value = { username: "", password: "" };
  }
}
</script>

<style scoped>
/* 页面全屏居中，杜绝外部大滚动条 */
.login-page {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  margin: 0;
  padding: 0;
  overflow: hidden;
}

/* 卡片容器宽度控制 */
.card-wrap {
  width: 420px;
  /* 居中兜底 */
  margin: 0 auto;
}

/* 登录卡片样式 */
.login-card {
  padding: 32px 24px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* 标题样式 */
.brand {
  text-align: center;
  margin-bottom: 24px;
}

.brand h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 13px;
  margin: 0;
}

/* 辅助栏样式 */
.helpers {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

/* 按钮组样式 */
.actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

/* 快速登录按钮 */
.quick-login {
  margin-top: 8px;
}

/* 注册表单间距 */
.reg-form {
  margin-top: 0;
}

/* ======== 弹窗内部滚动核心样式 ======== */
/* 将选择器直接指向 .role-dialog (弹窗本身) */
:deep(.role-dialog) {
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

/* 固定头部 */
:deep(.role-dialog .el-dialog__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  margin-right: 0; /* 清除默认右边距 */
  flex-shrink: 0;
}

/* 主体开启滚动 */
:deep(.role-dialog .el-dialog__body) {
  padding: 16px 20px;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
}

/* 固定尾部 */
:deep(.role-dialog .el-dialog__footer) {
  padding: 12px 20px;
  border-top: 1px solid #ebeef5;
  flex-shrink: 0;
}

/* 角色卡片等内部样式保持不变 */
.role-card {
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.role-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.role-card-selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.role-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.role-icon {
  font-size: 32px;
  margin-right: 12px;
}

.icon-institution {
  color: #f56c6c;
}

.icon-caregiver {
  color: #e6a23c;
}

.icon-regulatory {
  color: #67c23a;
}

.role-title h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #303133;
}

.role-info {
  padding-left: 44px;
}

.info-section {
  margin-bottom: 8px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.info-section.compact {
  margin-bottom: 6px;
}

.info-section h4 {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-section p {
  margin: 2px 0;
  font-size: 12px;
  color: #909399;
}

.info-section ul {
  margin: 0;
  padding-left: 16px;
  list-style-type: disc;
}

.feature-list {
  columns: 2;
  column-gap: 16px;
}

.info-section li {
  margin: 2px 0;
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
  break-inside: avoid;
}

.more-text {
  color: #909399;
  font-style: italic;
}

.perm-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* Tooltip 内容样式 */
.tooltip-content {
  max-width: 300px;
}

.tooltip-item {
  padding: 4px 0;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

.tooltip-item:not(:last-child) {
  border-bottom: 1px solid #ebeef5;
}
</style>
