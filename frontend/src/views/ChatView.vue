<template>
  <el-container class="chat-container">
    <el-header height="60px" class="header">
      <div class="header-left">
        <h2>AI聊天</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="clearChat" icon="Delete">
          清空聊天
        </el-button>
      </div>
    </el-header>
    <el-main>
      <el-card>
        <template #header>
          <div class="card-header">
            <span>智能助手</span>
            <div class="card-header-actions">
              <el-tag type="info">实时问答</el-tag>
            </div>
          </div>
        </template>
        <div class="chat-messages" ref="chatMessagesRef">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="[
              'message',
              message.sender === 'user' ? 'user-message' : 'ai-message',
            ]"
          >
            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">{{
                  message.sender === "user" ? "您" : "AI助手"
                }}</span>
                <span class="message-time">{{ message.timestamp }}</span>
              </div>
              <div class="message-text">{{ message.text }}</div>
            </div>
          </div>
          <!-- 当没有消息时显示常见问题 -->
          <div v-if="messages.length === 1" class="initial-questions">
            <div class="initial-questions-header">热门问题</div>
            <div class="common-questions">
              <el-tag
                v-for="(question, index) in commonQuestions"
                :key="index"
                class="common-question-tag"
                @click="selectQuestion(question)"
              >
                {{ question }}
              </el-tag>
            </div>
          </div>
          <div v-if="isLoading" class="loading-message">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>AI正在思考...</span>
          </div>
        </div>
        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题，例如：某老人的最大需求是什么？"
            @keyup.enter.ctrl="sendMessage"
          />
          <!-- <div class="input-actions"> -->
          <el-button
            type="primary"
            class="sub-btn"
            @click="sendMessage"
            :loading="isLoading"
          >
            发送
          </el-button>
        </div>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import auth from "@/utils/auth";
import axios from "@/utils/http";
import { Loading } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, ref } from "vue";

// 响应式数据
const messages = ref([]);
const currentUser = computed(() => auth.getCurrentUser());
const isCaregiver = computed(() => currentUser.value?.role === "caregiver");

// 触发紧急预警
function showEmergencyDialog() {
  ElMessageBox.prompt("请输入老人ID和异常情况描述", "紧急预警", {
    confirmButtonText: "提交预警",
    cancelButtonText: "取消",
    inputPlaceholder: "格式：老人ID:异常描述",
  }).then(async ({ value }) => {
    if (value) {
      try {
        await axios.post("/api/chat/emergency", {
          content: value,
          sender: currentUser.value?.username,
        });
        ElMessage.success("预警已提交，管理人员将尽快处理");

        // 自动发送一条消息到聊天框
        messages.value.push({
          sender: "user",
          text: `[紧急预警] ${value}`,
          timestamp: new Date().toLocaleTimeString(),
        });
      } catch (e) {
        ElMessage.error("预警提交失败");
      }
    }
  });
}
const inputMessage = ref("");
const isLoading = ref(false);
const commonQuestions = ref([]);
const chatMessagesRef = ref(null);

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) {
    ElMessage.warning("请输入问题");
    return;
  }

  // 添加用户消息
  const userMessage = {
    sender: "user",
    text: inputMessage.value.trim(),
    timestamp: new Date().toLocaleTimeString(),
  };
  messages.value.push(userMessage);

  // 清空输入框
  const question = inputMessage.value.trim();
  inputMessage.value = "";

  // 显示加载状态
  isLoading.value = true;

  try {
    // 调用后端API
    const response = await axios.post("/api/chat", {
      question: question,
    });

    // 添加AI回复
    const aiMessage = {
      sender: "ai",
      text: response.data.answer,
      timestamp: new Date().toLocaleTimeString(),
    };
    messages.value.push(aiMessage);
    // 滚动到对话底部
    scrollToBottom();
  } catch (error) {
    console.error("发送消息失败:", error);
    ElMessage.error("发送消息失败，请稍后重试");

    // 添加错误消息
    const errorMessage = {
      sender: "ai",
      text: "抱歉，我暂时无法回答您的问题，请稍后重试。",
      timestamp: new Date().toLocaleTimeString(),
    };
    messages.value.push(errorMessage);
    // 滚动到对话底部
    scrollToBottom();
  } finally {
    // 隐藏加载状态
    isLoading.value = false;
  }
};

// 选择常见问题
const selectQuestion = (question: string) => {
  inputMessage.value = question;
  sendMessage();
};

// 滚动到对话底部
const scrollToBottom = () => {
  setTimeout(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTo({
        top: chatMessagesRef.value.scrollHeight,
        behavior: "smooth",
      });
    }
  }, 100);
};

// 清空聊天
const clearChat = () => {
  messages.value = [];
  inputMessage.value = "";
  // 重新加载初始化消息
  loadInitialMessage();
};

// 加载常见问题
const loadCommonQuestions = async () => {
  try {
    const response = await axios.get("/api/common-questions");
    if (response.data.error) {
      ElMessage.error("加载失败：" + response.data.error);
    } else {
      commonQuestions.value = response.data.data;
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
    //  fallback to default questions if API fails
    commonQuestions.value = [
      "某老人的最大需求是什么？",
      "如何提高老人的服务满意度？",
      "哪些社区的服务需求最高？",
      "老人的健康状况如何？",
      "如何优化服务资源配置？",
    ];
  }
};

// 加载初始化消息
const loadInitialMessage = async () => {
  try {
    const response = await axios.get("/api/chat/initial");
    if (response.data.error) {
      ElMessage.error("加载失败：" + response.data.error);
      // fallback to default message if API fails
      messages.value = [
        {
          sender: "ai",
          text: "您好！我是养老服务智能助手，有什么可以帮您的吗？",
          timestamp: new Date().toLocaleTimeString(),
        },
      ];
    } else {
      messages.value = [
        {
          sender: "ai",
          text: response.data.answer,
          timestamp: new Date().toLocaleTimeString(),
        },
      ];
      // 滚动到对话底部
      scrollToBottom();
    }
  } catch (error) {
    ElMessage.error("请求失败：" + error);
    // fallback to default message if API fails
    messages.value = [
      {
        sender: "ai",
        text: "您好！我是养老服务智能助手，有什么可以帮您的吗？",
        timestamp: new Date().toLocaleTimeString(),
      },
    ];
    // 滚动到对话底部
    scrollToBottom();
  }
};

// 页面加载时初始化
onMounted(() => {
  loadCommonQuestions();
  loadInitialMessage();
});
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #f8fafd;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0 20px;
  border-bottom: 1px solid #eee;
}

.header-left h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #0066cc;
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
}

.card-header span {
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
}

.chat-messages {
  flex: 1;
  height: auto;
  min-height: 300px;
  max-height: 50vh;
  overflow-y: auto;
  padding: 20px;
  border-bottom: 1px solid #eaeef1;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 20px;
  display: flex;
  opacity: 0;
  transform: translateY(10px);
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.user-message .message-content {
  background: linear-gradient(145deg, #d4e6f8, #e8f3ff);
  color: #0056b3;
  border-bottom-right-radius: 4px;
}

.ai-message .message-content {
  background: linear-gradient(145deg, #f0f2f5, #f5f7fa);
  color: #333;
  border-bottom-left-radius: 4px;
}

.user-message .message-content:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
}

.ai-message .message-content:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 0.8rem;
  color: #777;
}

.message-text {
  line-height: 1.5;
}

.loading-message {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 15px 0;
  color: #606266;
  font-size: 14px;
}

.loading-message .el-icon {
  margin-right: 8px;
  color: #0066cc;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.chat-input {
  display: flex;
  gap: 10px;
  position: relative;
}

.sub-btn {
  border-radius: 8px;
  width: 80px;
  height: 75px;
  align-self: flex-end;
  background-color: #0066cc;
  border-color: #0066cc;
}

.sub-btn:hover {
  background-color: #0056b3;
  border-color: #0056b3;
}

.sub-btn:active {
  background-color: #004499;
  border-color: #004499;
}

.initial-questions {
  padding: 15px;
  text-align: center;
  background-color: #f9fafc;
  border-radius: 10px;
  margin-bottom: 15px;
}

.initial-questions-header {
  font-weight: 600;
  color: #555;
  margin-bottom: 10px;
  font-size: 14px;
}

.common-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.common-question-tag {
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f0f7ff;
  border: 1px solid #d4e6f8;
  color: #0066cc;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  box-shadow: 0 2px 4px rgba(0, 102, 204, 0.08);
}

.common-question-tag:hover {
  background-color: #e8f3ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 102, 204, 0.15);
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

:deep(.chat-input .el-textarea__inner:focus) {
  border-color: #0066cc;
  box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2);
}

:deep(.el-card) {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eee;
  overflow: hidden;
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

  .chat-messages {
    min-height: 250px;
  }

  .message-content {
    max-width: 90%;
  }

  .common-question-tag {
    font-size: 12px;
    padding: 5px 10px;
  }
}
</style>
