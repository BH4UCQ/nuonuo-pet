<template>
  <div class="interactions">
    <el-card shadow="hover">
      <div class="toolbar">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        />
        <el-select v-model="filterType" placeholder="交互类型" clearable>
          <el-option label="对话" value="chat" />
          <el-option label="触摸" value="touch" />
          <el-option label="喂食" value="feed" />
          <el-option label="玩耍" value="play" />
        </el-select>
        <el-button type="primary" @click="fetchInteractions">
          查询
        </el-button>
      </div>

      <el-table :data="interactions" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="deviceName" label="设备" width="120" />
        <el-table-column prop="petName" label="宠物" width="100" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeStyle(row.type)">
              {{ getTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" show-overflow-tooltip />
        <el-table-column prop="response" label="响应" show-overflow-tooltip />
        <el-table-column prop="emotion" label="情绪变化" width="100">
          <template #default="{ row }">
            <span :class="getEmotionClass(row.emotion)">
              {{ row.emotion > 0 ? '+' : '' }}{{ row.emotion }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Interaction {
  id: number
  time: string
  deviceName: string
  petName: string
  type: string
  content: string
  response: string
  emotion: number
}

const loading = ref(false)
const dateRange = ref<[Date, Date]>()
const filterType = ref('')
const interactions = ref<Interaction[]>([
  {
    id: 1,
    time: '2025-04-10 14:30:00',
    deviceName: 'Device-001',
    petName: '小诺',
    type: 'chat',
    content: '你好呀，今天心情怎么样？',
    response: '我今天很开心，想和你一起玩！',
    emotion: 10,
  },
  {
    id: 2,
    time: '2025-04-10 14:25:00',
    deviceName: 'Device-001',
    petName: '小诺',
    type: 'touch',
    content: '摸摸头',
    response: '喵~好舒服',
    emotion: 5,
  },
])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(2)

const fetchInteractions = () => {
  // TODO: 实现查询
}

const getTypeStyle = (type: string) => {
  const styles: Record<string, string> = {
    chat: 'primary',
    touch: 'success',
    feed: 'warning',
    play: 'info',
  }
  return styles[type] || ''
}

const getTypeText = (type: string) => {
  const texts: Record<string, string> = {
    chat: '对话',
    touch: '触摸',
    feed: '喂食',
    play: '玩耍',
  }
  return texts[type] || type
}

const getEmotionClass = (emotion: number) => {
  return emotion > 0 ? 'emotion-positive' : 'emotion-negative'
}
</script>

<style scoped lang="scss">
.interactions {
  .toolbar {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
  }

  .emotion-positive {
    color: #67c23a;
    font-weight: bold;
  }

  .emotion-negative {
    color: #f56c6c;
    font-weight: bold;
  }

  .el-pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
}
</style>
