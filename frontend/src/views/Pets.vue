<template>
  <div class="pets">
    <el-card shadow="hover">
      <div class="toolbar">
        <el-input
          v-model="searchText"
          placeholder="搜索宠物"
          prefix-icon="Search"
          style="width: 300px"
        />
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          创建宠物
        </el-button>
      </div>

      <el-table :data="pets" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="species" label="物种" width="100" />
        <el-table-column prop="level" label="等级" width="80" />
        <el-table-column prop="emotion" label="情绪" width="100">
          <template #default="{ row }">
            <el-tag>{{ getEmotionText(row.emotion) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hunger" label="饥饿度" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.hunger" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column prop="happiness" label="快乐度" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.happiness"
              :stroke-width="8"
              status="success"
            />
          </template>
        </el-table-column>
        <el-table-column prop="deviceName" label="所属设备" width="120" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">
              详情
            </el-button>
            <el-button link type="primary" @click="handleInteract(row)">
              交互
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">
              删除
            </el-button>
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

interface Pet {
  id: number
  name: string
  species: string
  level: number
  emotion: string
  hunger: number
  happiness: number
  deviceName: string
}

const loading = ref(false)
const searchText = ref('')
const pets = ref<Pet[]>([
  {
    id: 1,
    name: '小诺',
    species: '猫咪',
    level: 5,
    emotion: 'happy',
    hunger: 30,
    happiness: 80,
    deviceName: 'Device-001',
  },
  {
    id: 2,
    name: '小宠',
    species: '狗狗',
    level: 3,
    emotion: 'calm',
    hunger: 50,
    happiness: 60,
    deviceName: 'Device-002',
  },
])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(2)

const handleAdd = () => {
  ElMessage.info('创建宠物功能开发中')
}

const handleView = (row: Pet) => {
  ElMessage.info(`查看宠物: ${row.name}`)
}

const handleInteract = (row: Pet) => {
  ElMessage.info(`与 ${row.name} 交互`)
}

const handleDelete = (row: Pet) => {
  ElMessage.info(`删除宠物: ${row.name}`)
}

const getEmotionText = (emotion: string) => {
  const texts: Record<string, string> = {
    happy: '开心',
    sad: '难过',
    angry: '生气',
    calm: '平静',
    excited: '兴奋',
  }
  return texts[emotion] || emotion
}
</script>

<style scoped lang="scss">
.pets {
  .toolbar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
  }

  .el-pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
}
</style>
