<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { useTabStore } from '@/stores/tab'
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

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()
const tabStore = useTabStore()

const selectedKeys = computed(() => [route.path])
const openKeys = ref<string[]>(['/setting'])

watch(() => route.path, () => {
  tabStore.syncRoute(route)
}, { immediate: true })

function handleMenuClick({ key }: { key: string }) {
  router.push(key)
}

function handleLogout() {
  userStore.clearToken()
  router.push('/login')
}
</script>

<template>
  <a-layout style="min-height: 100vh">
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
        <a-menu-item key="/dashboard">
          <template #icon><DashboardOutlined /></template>
          仪表盘
        </a-menu-item>
        <a-menu-item key="/model">
          <template #icon><RobotOutlined /></template>
          模型管理
        </a-menu-item>
        <a-menu-item key="/skill">
          <template #icon><ThunderboltOutlined /></template>
          Skills 管理
        </a-menu-item>
        <a-menu-item key="/tool">
          <template #icon><ToolOutlined /></template>
          工具管理
        </a-menu-item>
        <a-sub-menu key="/setting">
          <template #icon><SettingOutlined /></template>
          <template #title>系统设置</template>
          <a-menu-item key="/setting/user">
            <template #icon><UserOutlined /></template>
            用户管理
          </a-menu-item>
          <a-menu-item key="/setting/role">
            <template #icon><TeamOutlined /></template>
            角色管理
          </a-menu-item>
          <a-menu-item key="/setting/permission">
            <template #icon><SafetyCertificateOutlined /></template>
            权限管理
          </a-menu-item>
          <a-menu-item key="/setting/menu">
            <template #icon><MenuOutlined /></template>
            菜单配置
          </a-menu-item>
          <a-menu-item key="/setting/config">
            <template #icon><ControlOutlined /></template>
            系统配置
          </a-menu-item>
          <a-menu-item key="/setting/operation-log">
            <template #icon><FileTextOutlined /></template>
            操作日志
          </a-menu-item>
          <a-menu-item key="/setting/login-log">
            <template #icon><LoginOutlined /></template>
            登录日志
          </a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>
    <a-layout>
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
      <a-layout-content style="margin: 16px; padding: 0; background: #fff; border-radius: 8px; min-height: 280px; overflow: hidden;">
        <TabBar />
        <div style="padding: 24px;">
          <router-view v-slot="{ Component }">
            <keep-alive :include="tabStore.cachedNames">
              <component :is="Component" />
            </keep-alive>
          </router-view>
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>
