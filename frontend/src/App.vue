<script setup lang="ts">
import { onMounted } from 'vue'
import { getUserInfoApi } from './api/user'
import { useUserStore } from './stores/user'

const userStore = useUserStore()

onMounted(async () => {
  if (userStore.token && !userStore.userInfo) {
    const userInfo = await getUserInfoApi()
    userStore.setUserInfo(userInfo)
  }
})
</script>

<template>
  <router-view />
</template>
