<script setup lang="ts">
import { useRouter } from 'vue-router'
import ForcePasswordChangeModal from './components/ForcePasswordChangeModal.vue'
import { useUserStore } from './stores/user'
import { logoutApi } from './api/user'

const userStore = useUserStore()
const router = useRouter()

async function handleLogout() {
  try {
    if (userStore.token) {
      await logoutApi()
    }
  } finally {
    userStore.clearToken()
    router.push('/login')
  }
}
</script>

<template>
  <router-view />
  <ForcePasswordChangeModal
    :open="userStore.mustChangePassword"
    @success="userStore.mustChangePassword = false"
    @logout="handleLogout"
  />
</template>
