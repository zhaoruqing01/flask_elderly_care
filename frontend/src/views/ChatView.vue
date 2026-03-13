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
        <div class="chat-messages">
          <div 
            v-for="(message, index) in messages" 
            :key="index" 
            :class="['message', message.sender === 'user' ? 'user-message' : 'ai-message']"
          >
            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">{{ message.sender === 'user' ? '您' : 'AI助手' }}</span>
                <span class="message-time">{{ message.timestamp }}</span>
              </div>
              <div class="message-text">{{ message.text }}</div>
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
          <div class="input-actions">
            <el-button type="primary" @click="sendMessage" :loading="isLoading" icon="Send">
              发送
            </el-button>
          </div>
        </div>
      </el-card>
      <el-card style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>常见问题</span>
          </div>
        </template>
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
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

// 响应式数据
const messages = ref([
  {
    sender: 'ai',
    text: '您好！我是养老服务智能助手，有什么可以帮您的吗？',
    timestamp: new Date().toLocaleTimeString()
  }
])
const inputMessage = ref('')
const isLoading = ref(false)
const commonQuestions = [
  '某老人的最大需求是什么？',
  '如何提高老人的服务满意度？',
  '哪些社区的服务需求最高？',
  '老人的健康状况如何？',
  '如何优化服务资源配置？'
]

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  
  // 添加用户消息
  const userMessage = {
    sender: 'user',
    text: inputMessage.value.trim(),
    timestamp: new Date().toLocaleTimeString()
  }
  messages.value.push(userMessage)
  
  // 清空输入框
  const question = inputMessage.value.trim()
  inputMessage.value = ''
  
  // 显示加载状态
  isLoading.value = true
  
  try {
    // 调用后端API
    const response = await axios.post('/api/chat', {
      question: question
    })
    
    // 添加AI回复
    const aiMessage = {
      sender: 'ai',
      text: response.data.answer,
      timestamp: new Date().toLocaleTimeString()
    }
    messages.value.push(aiMessage)
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败，请稍后重试')
    
    // 添加错误消息
    const errorMessage = {
      sender: 'ai',
      text: '抱歉，我暂时无法回答您的问题，请稍后重试。',
      timestamp: new Date().toLocaleTimeString()
    }
    messages.value.push(errorMessage)
  } finally {
    // 隐藏加载状态
    isLoading.value = false
  }
}

// 选择常见问题
const selectQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

// 清空聊天
const clearChat = () => {
  messages.value = [
    {
      sender: 'ai',
      text: '您好！我是养老服务智能助手，有什么可以帮您的吗？',
      timestamp: new Date().toLocaleTimeString()
    }
  ]
  inputMessage.value = ''
}

// 页面加载时初始化
onMounted(() => {
  // 可以在这里添加初始化逻辑
})
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
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
  color: #0066CC;
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

.chat-messages {
  height: 500px;
  overflow-y: auto;
  padding: 20px;
  border-bottom: 1px solid #eaeef1;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 20px;
  display: flex;
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.user-message .message-content {
  background-color: #e8f3ff;
  color: #0066CC;
  border-bottom-right-radius: 4px;
}

.ai-message .message-content {
  background-color: #f5f7fa;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.8rem;
  color: #909399;
}

.message-text {
  line-height: 1.5;
}

.loading-message {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  color: #909399;
}

.loading-message .el-icon {
  margin-right: 8px;
}

.chat-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.common-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 0;
}

.common-question-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.common-question-tag:hover {
  background-color: #e8f3ff;
  color: #0066CC;
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
    height: 300px;
  }
  
  .message-content {
    max-width: 90%;
  }
}
</style>