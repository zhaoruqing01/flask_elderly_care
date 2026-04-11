<template>
  <el-container class="login-page">
    <el-main>
      <div class="card-wrap">
        <el-card class="login-card">
          <!-- 品牌标题 -->
          <div class="brand">
            <h1>养老服务平台</h1>
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
              <el-input v-model="form.username" placeholder="用户名"></el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="密码"
              ></el-input>
            </el-form-item>

            <div class="helpers">
              <!-- 切换到注册 -->
              <el-button type="text" @click="toggleForm"
                >没有账号？注册</el-button
              >
            </div>

            <div class="actions">
              <el-button type="primary" @click="handleLogin" style="width: 48%">
                登录
              </el-button>
              <el-button @click="fillDefault" style="width: 48%">
                填充默认
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
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="reg.password"
                type="password"
                placeholder="密码（至少6位）"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="reg.confirm"
                type="password"
                placeholder="确认密码"
              ></el-input>
            </el-form-item>

            <div class="actions">
              <el-button
                type="success"
                @click="handleRegister"
                style="width: 48%"
              >
                注册并登录
              </el-button>
              <el-button @click="toggleForm" style="width: 48%">
                返回登录
              </el-button>
            </div>
          </el-form>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import auth from "@/utils/auth";
import { ElMessage } from "element-plus";
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 备用用户名
const backupUsers = ["admin", "backup1", "backup2", "backup3"];

// 登录表单数据
const form = ref({ username: "", password: "" });
// 注册表单数据
const reg = ref({ username: "", password: "", confirm: "" });
// 表单ref
const formRef = ref();
// 动态控制：true=显示登录，false=显示注册
const isLogin = ref(true);

// 登录处理
function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning("请填写用户名和密码");
    return;
  }
  const ok = auth.login(form.value.username, form.value.password);
  if (ok) {
    ElMessage.success("登录成功");
    router.push({ path: "/" });
  } else {
    ElMessage.error("用户名或密码错误");
  }
}

// 注册处理
function handleRegister() {
  if (!reg.value.username || reg.value.password.length < 6) {
    ElMessage.warning("用户名不能为空，且密码至少6位");
    return;
  }
  if (reg.value.password !== reg.value.confirm) {
    ElMessage.warning("两次密码不一致");
    return;
  }
  const ok = auth.register(reg.value.username, reg.value.password);
  if (ok) {
    ElMessage.success("注册并登录成功");
    router.push({ path: "/" });
  } else {
    ElMessage.error("用户名已存在");
  }
}

// 填充默认账号密码
function fillDefault() {
  form.value.username = "admin";
  form.value.password = "123456";
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
/* 页面全屏居中 */
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  margin: 0;
  padding: 0;
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

.subtitle {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

/* 辅助栏样式 */
.helpers {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

/* 按钮组样式 */
.actions {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

/* 注册表单间距 */
.reg-form {
  margin-top: 0;
}
</style>
