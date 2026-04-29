<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { getUserInfoApi, loginApi } from '../../api/user'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const formState = reactive({
  username: '',
  password: '',
  remember: true,
})

async function handleLogin() {
  loading.value = true
  try {
    const result = await loginApi({
      username: formState.username,
      password: formState.password,
    })
    userStore.setToken(result.token)
    const userInfo = await getUserInfoApi()
    userStore.setAuthPayload(userInfo)
    message.success('登录成功')
    router.push(userInfo.menus?.[0]?.path || '/dashboard')
  } catch (e: any) {
    message.error(e.response?.data?.detail || e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5;">
    <a-card style="width: 400px; border-radius: 8px;" :bordered="false">
      <div style="text-align: center; margin-bottom: 32px;">
        <h1 style="font-size: 28px; font-weight: 600; color: #1677ff; margin: 0;">Max-Agent</h1>
        <p style="color: #999; margin-top: 8px;">后台管理系统</p>
      </div>
      <a-form :model="formState" @finish="handleLogin">
        <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="formState.username" placeholder="用户名" size="large">
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
          <a-input-password v-model:value="formState.password" placeholder="密码" size="large">
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>
        <a-form-item>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <a-checkbox v-model:checked="formState.remember">记住我</a-checkbox>
          </div>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading" block size="large">
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>
