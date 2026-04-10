<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409eff">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.deviceCount }}</div>
              <div class="stat-label">设备总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.petCount }}</div>
              <div class="stat-label">宠物总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.interactionCount }}</div>
              <div class="stat-label">交互次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.userCount }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>交互趋势</span>
          </template>
          <div ref="interactionChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>设备状态分布</span>
          </template>
          <div ref="deviceChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card shadow="hover" class="recent-activities">
      <template #header>
        <span>最近活动</span>
      </template>
      <el-table :data="recentActivities" style="width: 100%">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="device" label="设备" width="150" />
        <el-table-column prop="pet" label="宠物" width="150" />
        <el-table-column prop="action" label="活动" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const interactionChart = ref<HTMLElement>()
const deviceChart = ref<HTMLElement>()

const stats = ref({
  deviceCount: 128,
  petCount: 256,
  interactionCount: 1024,
  userCount: 64,
})

const recentActivities = ref([
  {
    time: '2025-04-10 14:30:00',
    device: 'Device-001',
    pet: '小诺',
    action: '用户发起对话交互',
    status: 'success',
  },
  {
    time: '2025-04-10 14:25:00',
    device: 'Device-002',
    pet: '小诺',
    action: '宠物情绪更新',
    status: 'success',
  },
  {
    time: '2025-04-10 14:20:00',
    device: 'Device-003',
    pet: '小诺',
    action: '设备心跳上报',
    status: 'success',
  },
])

onMounted(() => {
  initInteractionChart()
  initDeviceChart()
})

const initInteractionChart = () => {
  if (!interactionChart.value) return
  const chart = echarts.init(interactionChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '交互次数',
        type: 'line',
        smooth: true,
        data: [120, 200, 150, 80, 70, 110, 130],
        areaStyle: { opacity: 0.3 },
      },
    ],
  })
}

const initDeviceChart = () => {
  if (!deviceChart.value) return
  const chart = echarts.init(deviceChart.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: '设备状态',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 80, name: '在线' },
          { value: 30, name: '离线' },
          { value: 18, name: '待激活' },
        ],
      },
    ],
  })
}
</script>

<style scoped lang="scss">
.dashboard {
  .stat-cards {
    margin-bottom: 20px;
  }

  .stat-card {
    display: flex;
    align-items: center;

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;

      .el-icon {
        font-size: 28px;
        color: #fff;
      }
    }

    .stat-info {
      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #333;
      }

      .stat-label {
        font-size: 14px;
        color: #999;
        margin-top: 5px;
      }
    }
  }

  .charts-row {
    margin-bottom: 20px;

    .chart {
      height: 300px;
    }
  }

  .recent-activities {
    margin-bottom: 20px;
  }
}
</style>
