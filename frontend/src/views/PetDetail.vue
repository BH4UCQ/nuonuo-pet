<template>
  <div class="pet-detail">
    <el-row :gutter="20">
      <!-- 左侧：宠物交互 -->
      <el-col :span="16">
        <el-card shadow="hover">
          <PetInteraction :pet-id="petId" @update="loadPetDetail" />
        </el-card>
      </el-col>

      <!-- 右侧：宠物信息 -->
      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>
            <span>宠物信息</span>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="名称">{{ pet?.name }}</el-descriptions-item>
            <el-descriptions-item label="物种">{{ pet?.species }}</el-descriptions-item>
            <el-descriptions-item label="等级">Lv.{{ pet?.level }}</el-descriptions-item>
            <el-descriptions-item label="经验值">{{ pet?.experience }}</el-descriptions-item>
            <el-descriptions-item label="总交互">{{ pet?.total_interactions }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="hover" class="growth-card">
          <template #header>
            <span>成长进度</span>
          </template>

          <div class="growth-info">
            <div class="stage">
              <span class="label">成长阶段</span>
              <el-tag>{{ growthStage }}</el-tag>
            </div>
            <div class="progress">
              <span class="label">升级进度</span>
              <el-progress :percentage="levelProgress" />
            </div>
          </div>
        </el-card>

        <el-card shadow="hover" class="history-card">
          <template #header>
            <span>最近交互</span>
          </template>

          <el-timeline>
            <el-timeline-item
              v-for="item in recentHistory"
              :key="item.id"
              :timestamp="formatTime(item.created_at)"
              placement="top"
            >
              <el-tag size="small">{{ item.type }}</el-tag>
              <span class="history-content">{{ item.content }}</span>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import PetInteraction from '@/components/PetInteraction.vue'
import { petApi } from '@/api/pet'

const route = useRoute()
const petId = computed(() => Number(route.params.id))

const pet = ref<any>(null)
const recentHistory = ref<any[]>([])

const growthStages: Record<string, string> = {
  baby: '幼年期',
  child: '少年期',
  teen: '青年期',
  adult: '成年期',
  elder: '长老期',
}

const growthStage = computed(() => {
  return growthStages[pet.value?.custom_data?.growth_stage || 'baby'] || '幼年期'
})

const levelProgress = computed(() => {
  // 简化计算
  const level = pet.value?.level || 1
  const exp = pet.value?.experience || 0
  const levelExp = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500]
  if (level >= 10) return 100
  const current = levelExp[level - 1] || 0
  const next = levelExp[level] || 100
  return Math.min(100, ((exp - current) / (next - current)) * 100)
})

const loadPetDetail = async () => {
  try {
    const res = await petApi.getDetail(petId.value)
    pet.value = res.data
  } catch (error: any) {
    ElMessage.error('加载宠物信息失败')
  }
}

const loadHistory = async () => {
  try {
    const res = await petApi.getHistory(petId.value, { page: 1, size: 5 })
    recentHistory.value = res.data.items || []
  } catch (error) {
    // 忽略错误
  }
}

const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

onMounted(() => {
  loadPetDetail()
  loadHistory()
})
</script>

<style scoped lang="scss">
.pet-detail {
  .info-card,
  .growth-card,
  .history-card {
    margin-bottom: 20px;
  }

  .growth-info {
    .stage,
    .progress {
      margin-bottom: 15px;

      .label {
        display: block;
        font-size: 12px;
        color: #666;
        margin-bottom: 5px;
      }
    }
  }

  .history-content {
    margin-left: 10px;
    color: #666;
  }
}
</style>
