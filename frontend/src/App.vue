<script setup lang="ts">
import { onMounted } from 'vue'
import { getUserInfoApi } from './api/user'
import ForcePasswordChangeModal from './components/ForcePasswordChangeModal.vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()

onMounted(async () => {
  if (userStore.token && !userStore.userInfo) {
    try {
      const info = await getUserInfoApi()
      userStore.setAuthPayload(info)
    } catch {
      userStore.clearToken()
    }
  }
})
</script>

<template>
  <router-view />
  <ForcePasswordChangeModal
    :open="userStore.mustChangePassword"
    @success="userStore.mustChangePassword = false"
  />
</template>
