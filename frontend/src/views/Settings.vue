<template>
  <div class="settings">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基础设置" name="basic">
        <el-card shadow="hover">
          <el-form :model="basicForm" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="basicForm.systemName" />
            </el-form-item>
            <el-form-item label="系统Logo">
              <el-upload
                action="/api/upload"
                :show-file-list="false"
              >
                <el-button type="primary">上传Logo</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item label="默认语言">
              <el-select v-model="basicForm.language">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBasic">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="AI设置" name="ai">
        <el-card shadow="hover">
          <el-form :model="aiForm" label-width="120px">
            <el-form-item label="主模型">
              <el-select v-model="aiForm.primaryModel">
                <el-option label="GPT-4" value="gpt-4" />
                <el-option label="GPT-3.5" value="gpt-3.5-turbo" />
                <el-option label="Claude-3" value="claude-3" />
              </el-select>
            </el-form-item>
            <el-form-item label="API Key">
              <el-input v-model="aiForm.apiKey" type="password" show-password />
            </el-form-item>
            <el-form-item label="API Base URL">
              <el-input v-model="aiForm.apiBase" />
            </el-form-item>
            <el-form-item label="温度参数">
              <el-slider v-model="aiForm.temperature" :min="0" :max="1" :step="0.1" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveAI">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="通知设置" name="notification">
        <el-card shadow="hover">
          <el-form :model="notifyForm" label-width="120px">
            <el-form-item label="设备离线通知">
              <el-switch v-model="notifyForm.deviceOffline" />
            </el-form-item>
            <el-form-item label="系统更新通知">
              <el-switch v-model="notifyForm.systemUpdate" />
            </el-form-item>
            <el-form-item label="邮件通知">
              <el-switch v-model="notifyForm.email" />
            </el-form-item>
            <el-form-item label="通知邮箱" v-if="notifyForm.email">
              <el-input v-model="notifyForm.emailAddress" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotify">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

const basicForm = reactive({
  systemName: 'Nuonuo Pet',
  language: 'zh-CN',
})

const aiForm = reactive({
  primaryModel: 'gpt-4',
  apiKey: '',
  apiBase: 'https://api.openai.com/v1',
  temperature: 0.7,
})

const notifyForm = reactive({
  deviceOffline: true,
  systemUpdate: true,
  email: false,
  emailAddress: '',
})

const saveBasic = () => ElMessage.success('基础设置已保存')
const saveAI = () => ElMessage.success('AI设置已保存')
const saveNotify = () => ElMessage.success('通知设置已保存')
</script>

<style scoped lang="scss">
.settings {
  .el-card {
    max-width: 800px;
  }
}
</style>
