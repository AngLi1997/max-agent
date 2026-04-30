<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { useTabStore } from '@/stores/tab'
import { logoutApi } from '@/api/user'
import TabBar from '@/components/TabBar.vue'
import {
  DashboardOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  ToolOutlined,
  SettingOutlined,
  UserOutlined,
  TeamOutlined,
  SafetyCertificateOutlined,
  MenuOutlined,
  ControlOutlined,
  FileTextOutlined,
  LoginOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons-vue'

const iconMap: Record<string, any> = {
  DashboardOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  ToolOutlined,
  SettingOutlined,
  UserOutlined,
  TeamOutlined,
  SafetyCertificateOutlined,
  MenuOutlined,
  ControlOutlined,
  FileTextOutlined,
  LoginOutlined,
}

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()
const tabStore = useTabStore()

const selectedKeys = computed(() => [route.path])
const openKeys = ref<string[]>(['/setting'])

// 页面标题与强调色：保持由路由 meta 驱动（用于页面壳层 header 展示）
const currentPageTitle = computed(() => (route.meta?.title as string) || '')
const pageAccentStyle = computed(() => ({
  '--page-title-accent': ((route.meta as any)?.accent as string) || '#1677ff',
}))

watch(() => route.path, () => {
  tabStore.syncRoute(route)
}, { immediate: true })

function handleMenuClick({ key }: { key: string }) {
  router.push(key)
}

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
  <a-layout style="height: 100vh; overflow: hidden">
    <a-layout-sider
      v-model:collapsed="appStore.sidebarCollapsed"
      collapsible
      :trigger="null"
      :width="220"
      theme="dark"
    >
      <div style="height: 64px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: 600;">
        <span v-if="!appStore.sidebarCollapsed">Max-Agent</span>
        <span v-else>MA</span>
      </div>
      <a-menu
        theme="dark"
        mode="inline"
        :selected-keys="selectedKeys"
        v-model:open-keys="openKeys"
        @click="handleMenuClick"
      >
        <template v-for="menu in userStore.menus" :key="menu.path">
          <a-sub-menu v-if="menu.children && menu.children.length > 0" :key="menu.path">
            <template #icon>
              <component :is="iconMap[menu.icon]" v-if="menu.icon && iconMap[menu.icon]" />
            </template>
            <template #title>{{ menu.name }}</template>
            <a-menu-item v-for="child in menu.children" :key="child.path">
              <template #icon>
                <component :is="iconMap[child.icon]" v-if="child.icon && iconMap[child.icon]" />
              </template>
              {{ child.name }}
            </a-menu-item>
          </a-sub-menu>
          <a-menu-item v-else :key="menu.path">
            <template #icon>
              <component :is="iconMap[menu.icon]" v-if="menu.icon && iconMap[menu.icon]" />
            </template>
            {{ menu.name }}
          </a-menu-item>
        </template>
      </a-menu>
    </a-layout-sider>
    <a-layout style="min-height: 0; overflow: hidden">
      <a-layout-header style="background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between;">
        <component
          :is="appStore.sidebarCollapsed ? MenuUnfoldOutlined : MenuFoldOutlined"
          style="font-size: 18px; cursor: pointer;"
          @click="appStore.toggleSidebar"
        />
        <a-dropdown>
          <span style="cursor: pointer;">
            <a-avatar :size="32">
              {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() || 'A' }}
            </a-avatar>
            <span style="margin-left: 8px;">{{ userStore.userInfo?.username || 'Admin' }}</span>
          </span>
          <template #overlay>
            <a-menu>
              <a-menu-item key="logout" @click="handleLogout">
                <template #icon><LogoutOutlined /></template>
                退出登录
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </a-layout-header>
      <TabBar class="layout-tabbar" />
      <a-layout-content class="layout-content-shell">
        <div class="workspace-shell">
          <div class="page-shell">
            <div v-if="currentPageTitle" class="page-shell-header">
              <span class="page-shell-accent" :style="pageAccentStyle"></span>
              <span class="page-shell-title">{{ currentPageTitle }}</span>
            </div>
            <div class="page-shell-body">
              <router-view v-slot="{ Component }">
                <keep-alive :include="tabStore.cachedNames">
                  <component :is="Component" />
                </keep-alive>
              </router-view>
            </div>
          </div>
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.layout-tabbar {
  margin: 12px 16px 0;
  background: transparent;
}

.layout-content-shell {
  margin: 0 16px 16px;
  min-height: 0;
  display: flex;
}

.workspace-shell {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e7edf6;
  border-top: none;
  border-radius: 0 0 16px 16px;
  overflow: hidden;
}

.page-shell {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.page-shell-header {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 48px;
  padding: 12px 20px;
  border-bottom: 1px solid #f2f4f7;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
}

.page-shell-accent {
  width: 4px;
  height: 18px;
  border-radius: 999px;
  background: var(--page-title-accent);
  flex-shrink: 0;
}

.page-shell-title {
  line-height: 1.2;
}

.page-shell-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  background: #fff;
}
</style>
