<template>
  <div class="pet-interaction">
    <!-- 宠物显示区域 -->
    <div class="pet-display">
      <div class="pet-avatar" :class="emotionClass">
        <span class="pet-emoji">{{ emotionEmoji }}</span>
      </div>
      <div class="pet-info">
        <h2>{{ pet?.name || '我的宠物' }}</h2>
        <div class="pet-stats">
          <span class="level">Lv.{{ pet?.level || 1 }}</span>
          <span class="species">{{ pet?.species || '猫咪' }}</span>
        </div>
      </div>
    </div>

    <!-- 状态条 -->
    <div class="status-bars">
      <div class="status-item">
        <span class="label">快乐度</span>
        <el-progress :percentage="pet?.happiness || 50" :stroke-width="10" status="success" />
      </div>
      <div class="status-item">
        <span class="label">饥饿度</span>
        <el-progress :percentage="pet?.hunger || 50" :stroke-width="10" status="warning" />
      </div>
      <div class="status-item">
        <span class="label">能量</span>
        <el-progress :percentage="pet?.energy || 50" :stroke-width="10" />
      </div>
    </div>

    <!-- 对话区域 -->
    <div class="chat-area" ref="chatArea">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="message"
        :class="msg.role"
      >
        <div class="message-content">{{ msg.content }}</div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input
        v-model="inputMessage"
        placeholder="和宠物聊天..."
        @keyup.enter="sendChat"
        :disabled="loading"
      >
        <template #append>
          <el-button @click="sendChat" :loading="loading">发送</el-button>
        </template>
      </el-input>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <el-button circle @click="doAction('touch')" :loading="actionLoading === 'touch'">
        <span class="action-icon">👆</span>
      </el-button>
      <el-button circle @click="doAction('feed')" :loading="actionLoading === 'feed'">
        <span class="action-icon">🍖</span>
      </el-button>
      <el-button circle @click="doAction('play')" :loading="actionLoading === 'play'">
        <span class="action-icon">🎾</span>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { petApi } from '@/api/pet'

interface Props {
  petId: number
}

const props = defineProps<Props>()
const emit = defineEmits(['update'])

const pet = ref<any>(null)
const messages = ref<Array<{ role: string; content: string }>>([])
const inputMessage = ref('')
const loading = ref(false)
const actionLoading = ref('')
const chatArea = ref<HTMLElement>()

// 情绪 emoji 映射
const emotionEmojis: Record<string, string> = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  fear: '😨',
  surprise: '😲',
  calm: '😌',
  excited: '🤩',
  lonely: '🥺',
}

const emotionEmoji = computed(() => {
  return emotionEmojis[pet.value?.emotion || 'calm'] || '😐'
})

const emotionClass = computed(() => {
  return `emotion-${pet.value?.emotion || 'calm'}`
})

// 加载宠物状态
const loadPetStatus = async () => {
  try {
    const res = await petApi.getDetail(props.petId)
    pet.value = res.data
  } catch (error: any) {
    ElMessage.error('加载宠物状态失败')
  }
}

// 发送聊天
const sendChat = async () => {
  if (!inputMessage.value.trim()) return

  const message = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.value.push({ role: 'user', content: message })
  scrollToBottom()

  loading.value = true
  try {
    const res = await petApi.interact(props.petId, {
      type: 'chat',
      content: message,
    })

    if (res.success) {
      // 添加宠物回复
      messages.value.push({ role: 'assistant', content: res.response })
      
      // 更新宠物状态
      if (res.emotion) {
        pet.value.emotion = res.emotion.emotion
      }
      if (res.growth?.level_up) {
        ElMessage.success(`🎉 升级了！当前等级: ${res.growth.new_level}`)
      }
      
      emit('update')
    } else {
      messages.value.push({ role: 'assistant', content: res.response || '抱歉，出了点问题...' })
    }

    scrollToBottom()
  } catch (error: any) {
    ElMessage.error('发送失败')
    messages.value.pop() // 移除用户消息
  } finally {
    loading.value = false
  }
}

// 执行快捷操作
const doAction = async (action: string) => {
  actionLoading.value = action
  try {
    const res = await petApi.interact(props.petId, {
      type: action,
      content: '',
    })

    if (res.success) {
      messages.value.push({ role: 'assistant', content: res.response })
      
      // 更新状态
      if (res.happiness !== undefined) {
        pet.value.happiness = res.happiness
      }
      if (res.hunger !== undefined) {
        pet.value.hunger = res.hunger
      }
      if (res.emotion) {
        pet.value.emotion = res.emotion.emotion
      }
      
      scrollToBottom()
      emit('update')
    }
  } catch (error: any) {
    ElMessage.error('操作失败')
  } finally {
    actionLoading.value = ''
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight
    }
  })
}

onMounted(() => {
  loadPetStatus()
})
</script>

<style scoped lang="scss">
.pet-interaction {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;

  .pet-display {
    text-align: center;
    margin-bottom: 20px;

    .pet-avatar {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      margin-bottom: 10px;

      .pet-emoji {
        font-size: 60px;
      }
    }

    .pet-info {
      h2 {
        margin: 0;
        font-size: 24px;
      }

      .pet-stats {
        margin-top: 5px;
        color: #666;

        .level {
          font-weight: bold;
          color: #409eff;
          margin-right: 10px;
        }
      }
    }
  }

  .status-bars {
    margin-bottom: 20px;

    .status-item {
      margin-bottom: 10px;

      .label {
        display: block;
        font-size: 12px;
        color: #666;
        margin-bottom: 4px;
      }
    }
  }

  .chat-area {
    height: 300px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
    background: #f9f9f9;

    .message {
      margin-bottom: 10px;

      .message-content {
        padding: 8px 12px;
        border-radius: 8px;
        max-width: 80%;
        word-wrap: break-word;
      }

      &.user {
        text-align: right;

        .message-content {
          background: #409eff;
          color: white;
          display: inline-block;
        }
      }

      &.assistant {
        text-align: left;

        .message-content {
          background: white;
          display: inline-block;
        }
      }
    }
  }

  .input-area {
    margin-bottom: 20px;
  }

  .quick-actions {
    display: flex;
    justify-content: center;
    gap: 20px;

    .el-button {
      width: 60px;
      height: 60px;

      .action-icon {
        font-size: 24px;
      }
    }
  }
}
</style>
