<template>
  <a-modal
    :open="open"
    title="修改密码"
    :closable="false"
    :maskClosable="false"
    :footer="null"
  >
    <p style="margin-bottom: 16px; color: #666;">首次登录，请修改密码后继续使用系统。</p>
    <a-form :model="formState" @finish="handleSubmit" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
      <a-form-item label="旧密码" name="oldPassword" :rules="[{ required: true, message: '请输入旧密码' }]">
        <a-input-password v-model:value="formState.oldPassword" placeholder="请输入旧密码" />
      </a-form-item>
      <a-form-item label="新密码" name="newPassword" :rules="[{ required: true, message: '请输入新密码' }]">
        <a-input-password v-model:value="formState.newPassword" placeholder="请输入新密码" />
      </a-form-item>
      <a-form-item label="确认密码" name="confirmPassword" :rules="[{ required: true, message: '请确认新密码' }]">
        <a-input-password v-model:value="formState.confirmPassword" placeholder="请再次输入新密码" />
      </a-form-item>
      <a-form-item :wrapper-col="{ offset: 6, span: 16 }">
        <a-button type="primary" html-type="submit" :loading="loading" block>确认修改</a-button>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { changePasswordApi } from '@/api/user'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ success: [] }>()

const formState = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const loading = ref(false)

async function handleSubmit() {
  if (formState.newPassword !== formState.confirmPassword) {
    message.error('两次输入的密码不一致')
    return
  }
  if (formState.newPassword.length < 6) {
    message.error('新密码长度不能少于6位')
    return
  }
  loading.value = true
  try {
    await changePasswordApi({ oldPassword: formState.oldPassword, newPassword: formState.newPassword })
    message.success('密码修改成功')
    formState.oldPassword = ''
    formState.newPassword = ''
    formState.confirmPassword = ''
    emit('success')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '密码修改失败')
  } finally {
    loading.value = false
  }
}
</script>
