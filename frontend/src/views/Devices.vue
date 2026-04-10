<template>
  <div class="devices">
    <el-card shadow="hover">
      <!-- 搜索和操作栏 -->
      <div class="toolbar">
        <el-input
          v-model="searchText"
          placeholder="搜索设备"
          prefix-icon="Search"
          style="width: 300px"
          @input="handleSearch"
        />
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加设备
        </el-button>
      </div>

      <!-- 设备列表 -->
      <el-table :data="devices" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="设备ID" width="120" />
        <el-table-column prop="name" label="设备名称" width="150" />
        <el-table-column prop="model" label="设备型号" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastOnline" label="最后在线" width="180" />
        <el-table-column prop="petName" label="关联宠物" width="120" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">
              查看
            </el-button>
            <el-button link type="primary" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchDevices"
        @current-change="fetchDevices"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deviceApi } from '@/api/device'

interface Device {
  id: string
  name: string
  model: string
  status: string
  lastOnline: string
  petName: string
}

const loading = ref(false)
const searchText = ref('')
const devices = ref<Device[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

onMounted(() => {
  fetchDevices()
})

const fetchDevices = async () => {
  loading.value = true
  try {
    const res = await deviceApi.getList({
      page: currentPage.value,
      size: pageSize.value,
      search: searchText.value,
    })
    devices.value = res.data.items
    total.value = res.data.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取设备列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchDevices()
}

const handleAdd = () => {
  // TODO: 打开添加设备对话框
  ElMessage.info('添加设备功能开发中')
}

const handleView = (row: Device) => {
  // TODO: 查看设备详情
  ElMessage.info(`查看设备: ${row.name}`)
}

const handleEdit = (row: Device) => {
  // TODO: 编辑设备
  ElMessage.info(`编辑设备: ${row.name}`)
}

const handleDelete = async (row: Device) => {
  try {
    await ElMessageBox.confirm(`确定要删除设备 ${row.name} 吗?`, '提示', {
      type: 'warning',
    })
    await deviceApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchDevices()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    online: 'success',
    offline: 'info',
    pending: 'warning',
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    online: '在线',
    offline: '离线',
    pending: '待激活',
  }
  return texts[status] || status
}
</script>

<style scoped lang="scss">
.devices {
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
