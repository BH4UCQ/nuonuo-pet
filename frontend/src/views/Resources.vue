<template>
  <div class="resources">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="物种资源" name="species">
        <el-card shadow="hover">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddSpecies">
              <el-icon><Plus /></el-icon>
              添加物种
            </el-button>
          </div>
          <el-table :data="species" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="stages" label="成长阶段" width="100" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary">编辑</el-button>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="主题资源" name="themes">
        <el-card shadow="hover">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddTheme">
              <el-icon><Plus /></el-icon>
              添加主题
            </el-button>
          </div>
          <el-table :data="themes" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="colors" label="配色" width="200" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary">编辑</el-button>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="音效资源" name="sounds">
        <el-card shadow="hover">
          <div class="toolbar">
            <el-button type="primary" @click="handleAddSound">
              <el-icon><Plus /></el-icon>
              上传音效
            </el-button>
          </div>
          <el-table :data="sounds" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" width="150" />
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column prop="duration" label="时长" width="100" />
            <el-table-column prop="size" label="大小" width="100" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button link type="primary">播放</el-button>
                <el-button link type="primary">下载</el-button>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('species')

const species = ref([
  { id: 1, name: '猫咪', description: '可爱的小猫咪', stages: 5 },
  { id: 2, name: '狗狗', description: '忠诚的小狗狗', stages: 5 },
  { id: 3, name: '兔子', description: '萌萌的小兔子', stages: 4 },
])

const themes = ref([
  { id: 1, name: '默认主题', description: '经典蓝色主题', colors: '#409EFF, #67C23A' },
  { id: 2, name: '粉色主题', description: '可爱粉色主题', colors: '#FF69B4, #FFB6C1' },
])

const sounds = ref([
  { id: 1, name: 'meow_01.mp3', category: '猫咪', duration: '1.2s', size: '24KB' },
  { id: 2, name: 'bark_01.mp3', category: '狗狗', duration: '0.8s', size: '18KB' },
])

const handleAddSpecies = () => ElMessage.info('添加物种功能开发中')
const handleAddTheme = () => ElMessage.info('添加主题功能开发中')
const handleAddSound = () => ElMessage.info('上传音效功能开发中')
</script>

<style scoped lang="scss">
.resources {
  .toolbar {
    margin-bottom: 20px;
  }
}
</style>
