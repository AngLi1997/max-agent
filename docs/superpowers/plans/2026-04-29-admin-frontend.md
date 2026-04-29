# Max-Agent 后台管理系统前端实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于 Ant Design Vue 4.x 搭建完整的后台管理系统前端，包含登录页、仪表盘、模型/Skills/工具管理，以及系统设置下的用户/角色/权限/菜单/配置/日志等页面。

**Architecture:** Vue 3 + TypeScript SPA，使用 Pinia 管理状态，vue-router 管理路由和导航守卫，axios 做 HTTP 层。布局采用 antd Layout 组件实现侧边栏 + 顶栏结构。后端 API 尚未就绪，所有数据使用 mock。

**Tech Stack:** Vue 3, TypeScript, Vite, ant-design-vue 4.x, @ant-design/icons-vue, vue-router 4, Pinia, axios, echarts, vue-echarts

---

## File Map

### 新建文件

| 文件路径 | 职责 |
|---------|------|
| `src/api/request.ts` | axios 实例，拦截器 |
| `src/api/user.ts` | 用户/登录相关 API |
| `src/api/dashboard.ts` | 仪表盘 API |
| `src/api/model.ts` | 模型管理 API |
| `src/api/skill.ts` | Skills 管理 API |
| `src/api/tool.ts` | 工具管理 API |
| `src/api/role.ts` | 角色管理 API |
| `src/api/permission.ts` | 权限管理 API |
| `src/api/menu.ts` | 菜单配置 API |
| `src/api/config.ts` | 系统配置 API |
| `src/api/log.ts` | 操作日志 + 登录日志 API |
| `src/stores/user.ts` | 用户登录态 store |
| `src/stores/app.ts` | UI 状态 store |
| `src/router/index.ts` | 路由定义 + 守卫 |
| `src/layouts/BasicLayout.vue` | 主布局 |
| `src/views/login/index.vue` | 登录页 |
| `src/views/dashboard/index.vue` | 仪表盘 |
| `src/views/model/index.vue` | 模型管理 |
| `src/views/skill/index.vue` | Skills 管理 |
| `src/views/tool/index.vue` | 工具管理 |
| `src/views/setting/user/index.vue` | 用户管理 |
| `src/views/setting/role/index.vue` | 角色管理 |
| `src/views/setting/permission/index.vue` | 权限管理 |
| `src/views/setting/menu/index.vue` | 菜单配置 |
| `src/views/setting/config/index.vue` | 系统配置 |
| `src/views/setting/operation-log/index.vue` | 操作日志 |
| `src/views/setting/login-log/index.vue` | 登录日志 |

### 修改文件

| 文件路径 | 变更 |
|---------|------|
| `package.json` | 添加依赖 |
| `src/main.ts` | 注册 antd、Pinia、Router |
| `src/App.vue` | 改为 `<router-view />` |
| `src/style.css` | 替换为极简全局样式 |
| `index.html` | 更新 title 为 Max-Agent |

### 删除文件

| 文件路径 | 原因 |
|---------|------|
| `src/components/HelloWorld.vue` | 模板文件，不再使用 |
| `src/assets/hero.png` | 模板资源 |
| `src/assets/vite.svg` | 模板资源 |
| `src/assets/vue.svg` | 模板资源 |

---

<!-- PLAN_TASKS_START -->

### Task 1: 安装依赖与项目配置

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/index.html`
- Modify: `frontend/src/main.ts`
- Modify: `frontend/src/style.css`
- Modify: `frontend/src/App.vue`
- Delete: `frontend/src/components/HelloWorld.vue`
- Delete: `frontend/src/assets/hero.png`
- Delete: `frontend/src/assets/vite.svg`
- Delete: `frontend/src/assets/vue.svg`

- [ ] **Step 1: 安装运行时依赖**

```bash
cd frontend && pnpm add ant-design-vue@4 @ant-design/icons-vue vue-router@4 pinia axios echarts vue-echarts
```

- [ ] **Step 2: 删除模板文件**

```bash
rm src/components/HelloWorld.vue src/assets/hero.png src/assets/vite.svg src/assets/vue.svg
```

- [ ] **Step 3: 更新 index.html**

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Max-Agent</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 4: 替换 style.css**

```css
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}
```

- [ ] **Step 5: 更新 App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 6: 更新 main.ts**

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(Antd)
app.mount('#app')
```

- [ ] **Step 7: 验证项目启动**

```bash
cd frontend && pnpm dev
```

打开浏览器访问 localhost，确认空白页无报错。

- [ ] **Step 8: 提交**

```bash
git add -A frontend/
git commit -m "feat: 安装依赖并配置 antd + router + pinia 基础框架"
```

---

### Task 2: Pinia Stores + Axios 实例

**Files:**
- Create: `src/stores/user.ts`
- Create: `src/stores/app.ts`
- Create: `src/api/request.ts`

- [ ] **Step 1: 创建 user store**

`src/stores/user.ts`:

```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<{ username: string; avatar: string } | null>(null)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function clearToken() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  function setUserInfo(info: { username: string; avatar: string }) {
    userInfo.value = info
  }

  return { token, userInfo, setToken, clearToken, setUserInfo }
})
```

- [ ] **Step 2: 创建 app store**

`src/stores/app.ts`:

```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return { sidebarCollapsed, toggleSidebar }
})
```

- [ ] **Step 3: 创建 axios 实例**

`src/api/request.ts`:

```ts
import axios from 'axios'
import { useUserStore } from '../stores/user'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

request.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.clearToken()
      router.push('/login')
    }
    return Promise.reject(error)
  },
)

export default request
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/stores/ frontend/src/api/request.ts
git commit -m "feat: 添加 Pinia stores 和 axios 实例"
```

---

### Task 3: 路由定义与导航守卫

**Files:**
- Create: `src/router/index.ts`

- [ ] **Step 1: 创建路由文件**

`src/router/index.ts`:

```ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
  },
  {
    path: '/',
    component: () => import('../layouts/BasicLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/index.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'model',
        name: 'Model',
        component: () => import('../views/model/index.vue'),
        meta: { title: '模型管理' },
      },
      {
        path: 'skill',
        name: 'Skill',
        component: () => import('../views/skill/index.vue'),
        meta: { title: 'Skills 管理' },
      },
      {
        path: 'tool',
        name: 'Tool',
        component: () => import('../views/tool/index.vue'),
        meta: { title: '工具管理' },
      },
      {
        path: 'setting',
        name: 'Setting',
        redirect: '/setting/user',
        meta: { title: '系统设置' },
        children: [
          {
            path: 'user',
            name: 'SettingUser',
            component: () => import('../views/setting/user/index.vue'),
            meta: { title: '用户管理' },
          },
          {
            path: 'role',
            name: 'SettingRole',
            component: () => import('../views/setting/role/index.vue'),
            meta: { title: '角色管理' },
          },
          {
            path: 'permission',
            name: 'SettingPermission',
            component: () => import('../views/setting/permission/index.vue'),
            meta: { title: '权限管理' },
          },
          {
            path: 'menu',
            name: 'SettingMenu',
            component: () => import('../views/setting/menu/index.vue'),
            meta: { title: '菜单配置' },
          },
          {
            path: 'config',
            name: 'SettingConfig',
            component: () => import('../views/setting/config/index.vue'),
            meta: { title: '系统配置' },
          },
          {
            path: 'operation-log',
            name: 'SettingOperationLog',
            component: () => import('../views/setting/operation-log/index.vue'),
            meta: { title: '操作日志' },
          },
          {
            path: 'login-log',
            name: 'SettingLoginLog',
            component: () => import('../views/setting/login-log/index.vue'),
            meta: { title: '登录日志' },
          },
        ],
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  if (!userStore.token && to.path !== '/login') {
    return '/login'
  }
  if (userStore.token && to.path === '/login') {
    return '/dashboard'
  }
})

export default router
```

- [ ] **Step 2: 创建所有 view 占位文件**

为每个路由创建最小占位组件，确保路由不报错：

每个 `index.vue` 内容为：

```vue
<template>
  <div>{{ $route.meta.title }}</div>
</template>
```

需要创建的文件：
- `src/views/login/index.vue`（内容为 `<template><div>登录</div></template>`）
- `src/views/dashboard/index.vue`
- `src/views/model/index.vue`
- `src/views/skill/index.vue`
- `src/views/tool/index.vue`
- `src/views/setting/user/index.vue`
- `src/views/setting/role/index.vue`
- `src/views/setting/permission/index.vue`
- `src/views/setting/menu/index.vue`
- `src/views/setting/config/index.vue`
- `src/views/setting/operation-log/index.vue`
- `src/views/setting/login-log/index.vue`

- [ ] **Step 3: 验证路由工作**

```bash
cd frontend && pnpm dev
```

浏览器访问 `/`，应被重定向到 `/login`（因为无 token）。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/router/ frontend/src/views/ frontend/src/layouts/
git commit -m "feat: 添加路由定义、导航守卫和页面占位组件"
```

---

<!-- PLAN_TASK4_PLACEHOLDER -->

### Task 4: BasicLayout 主布局

**Files:**
- Create: `src/layouts/BasicLayout.vue`

- [ ] **Step 1: 实现 BasicLayout**

`src/layouts/BasicLayout.vue`:

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'
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

const selectedKeys = computed(() => [route.path])
const openKeys = ref<string[]>(['/setting'])

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
      <a-layout-content style="margin: 16px; padding: 24px; background: #fff; border-radius: 8px; min-height: 280px;">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>
```

- [ ] **Step 2: 验证布局**

浏览器中手动在 localStorage 设置 `token` 为任意值，刷新页面，确认侧边栏、顶栏、内容区正常渲染，菜单点击可切换路由。

- [ ] **Step 3: 提交**

```bash
git add frontend/src/layouts/BasicLayout.vue
git commit -m "feat: 实现 BasicLayout 侧边栏 + 顶栏主布局"
```

---

### Task 5: 登录页

**Files:**
- Modify: `src/views/login/index.vue`
- Create: `src/api/user.ts`

- [ ] **Step 1: 创建用户 API（mock）**

`src/api/user.ts`:

```ts
export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  username: string
}

export function loginApi(params: LoginParams): Promise<LoginResult> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (params.username === 'admin' && params.password === 'admin123') {
        resolve({ token: 'mock-token-' + Date.now(), username: params.username })
      } else {
        reject(new Error('用户名或密码错误'))
      }
    }, 500)
  })
}

export interface UserInfo {
  username: string
  avatar: string
}

export function getUserInfoApi(): Promise<UserInfo> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ username: 'admin', avatar: '' })
    }, 200)
  })
}
```

- [ ] **Step 2: 实现登录页**

`src/views/login/index.vue`:

```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { loginApi } from '../../api/user'
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
    userStore.setUserInfo({ username: result.username, avatar: '' })
    message.success('登录成功')
    router.push('/dashboard')
  } catch (e: any) {
    message.error(e.message || '登录失败')
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
```

- [ ] **Step 3: 验证登录流程**

浏览器访问 `/login`，输入 admin / admin123，确认登录成功跳转到仪表盘。输入错误密码确认提示错误。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/views/login/ frontend/src/api/user.ts
git commit -m "feat: 实现登录页和用户 API mock"
```

---

<!-- PLAN_TASK6_PLACEHOLDER -->

### Task 6: 仪表盘页面

**Files:**
- Modify: `src/views/dashboard/index.vue`
- Create: `src/api/dashboard.ts`

- [ ] **Step 1: 创建仪表盘 API（mock）**

`src/api/dashboard.ts`:

```ts
export interface DashboardStats {
  userCount: number
  modelCount: number
  skillCount: number
  toolCount: number
}

export function getStatsApi(): Promise<DashboardStats> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ userCount: 128, modelCount: 15, skillCount: 42, toolCount: 23 })
    }, 300)
  })
}

export interface TrendItem {
  date: string
  value: number
}

export function getTrendApi(): Promise<TrendItem[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { date: '04-23', value: 120 },
        { date: '04-24', value: 132 },
        { date: '04-25', value: 101 },
        { date: '04-26', value: 134 },
        { date: '04-27', value: 90 },
        { date: '04-28', value: 230 },
        { date: '04-29', value: 210 },
      ])
    }, 300)
  })
}
```

- [ ] **Step 2: 实现仪表盘页面**

`src/views/dashboard/index.vue`:

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import {
  UserOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  ToolOutlined,
} from '@ant-design/icons-vue'
import { getStatsApi, getTrendApi } from '../../api/dashboard'
import type { DashboardStats, TrendItem } from '../../api/dashboard'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const stats = ref<DashboardStats>({ userCount: 0, modelCount: 0, skillCount: 0, toolCount: 0 })
const trend = ref<TrendItem[]>([])

const chartOption = ref({})

onMounted(async () => {
  stats.value = await getStatsApi()
  trend.value = await getTrendApi()
  chartOption.value = {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: trend.value.map((t) => t.date) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: trend.value.map((t) => t.value), smooth: true, areaStyle: {} }],
  }
})
</script>

<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 24px;">
      <a-col :span="6">
        <a-card>
          <a-statistic title="用户数" :value="stats.userCount">
            <template #prefix><UserOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="模型数" :value="stats.modelCount">
            <template #prefix><RobotOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="Skills 数" :value="stats.skillCount">
            <template #prefix><ThunderboltOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="工具数" :value="stats.toolCount">
            <template #prefix><ToolOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>
    <a-card title="近 7 天趋势">
      <v-chart :option="chartOption" style="height: 300px;" autoresize />
    </a-card>
  </div>
</template>
```

- [ ] **Step 3: 验证仪表盘**

浏览器登录后访问 `/dashboard`，确认 4 个统计卡片和折线图正常渲染。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/views/dashboard/ frontend/src/api/dashboard.ts
git commit -m "feat: 实现仪表盘页面（统计卡片 + 趋势图）"
```

---

### Task 7: 模型管理页面

**Files:**
- Modify: `src/views/model/index.vue`
- Create: `src/api/model.ts`

- [ ] **Step 1: 创建模型 API（mock）**

`src/api/model.ts`:

```ts
export interface ModelItem {
  id: number
  name: string
  provider: string
  status: 'active' | 'inactive'
  createdAt: string
}

const mockData: ModelItem[] = [
  { id: 1, name: 'GPT-4o', provider: 'OpenAI', status: 'active', createdAt: '2026-04-01' },
  { id: 2, name: 'Claude Opus 4', provider: 'Anthropic', status: 'active', createdAt: '2026-04-10' },
  { id: 3, name: 'Gemini 2.5', provider: 'Google', status: 'inactive', createdAt: '2026-04-15' },
]

export function getModelListApi(params?: { name?: string; provider?: string }): Promise<{ list: ModelItem[]; total: number }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params?.name) list = list.filter((i) => i.name.includes(params.name!))
      if (params?.provider) list = list.filter((i) => i.provider === params.provider)
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createModelApi(data: Omit<ModelItem, 'id' | 'createdAt'>): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { mockData.push({ ...data, id: Date.now(), createdAt: new Date().toISOString().slice(0, 10) }); resolve() }, 200)
  })
}

export function updateModelApi(id: number, data: Partial<ModelItem>): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { const item = mockData.find((i) => i.id === id); if (item) Object.assign(item, data); resolve() }, 200)
  })
}

export function deleteModelApi(id: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { const idx = mockData.findIndex((i) => i.id === id); if (idx > -1) mockData.splice(idx, 1); resolve() }, 200)
  })
}
```

- [ ] **Step 2: 实现模型管理页面**

`src/views/model/index.vue`:

```vue
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, ExclamationCircleOutlined } from '@ant-design/icons-vue'
import { getModelListApi, createModelApi, updateModelApi, deleteModelApi } from '../../api/model'
import type { ModelItem } from '../../api/model'

const loading = ref(false)
const dataSource = ref<ModelItem[]>([])
const total = ref(0)
const searchForm = reactive({ name: '', provider: '' })
const drawerVisible = ref(false)
const drawerTitle = ref('新增模型')
const formState = reactive<Partial<ModelItem>>({})
const editingId = ref<number | null>(null)

const columns = [
  { title: '模型名称', dataIndex: 'name' },
  { title: '提供商', dataIndex: 'provider' },
  { title: '状态', dataIndex: 'status' },
  { title: '创建时间', dataIndex: 'createdAt' },
  { title: '操作', key: 'action', width: 160 },
]

async function fetchData() {
  loading.value = true
  const res = await getModelListApi(searchForm)
  dataSource.value = res.list
  total.value = res.total
  loading.value = false
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增模型'
  Object.assign(formState, { name: '', provider: '', status: 'active' })
  drawerVisible.value = true
}

function handleEdit(record: ModelItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑模型'
  Object.assign(formState, { name: record.name, provider: record.provider, status: record.status })
  drawerVisible.value = true
}

function handleDelete(record: ModelItem) {
  Modal.confirm({
    title: '确认删除',
    icon: () => null,
    content: `确定删除模型「${record.name}」吗？`,
    async onOk() {
      await deleteModelApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

async function handleSubmit() {
  if (editingId.value) {
    await updateModelApi(editingId.value, formState)
    message.success('更新成功')
  } else {
    await createModelApi(formState as any)
    message.success('创建成功')
  }
  drawerVisible.value = false
  fetchData()
}

onMounted(fetchData)
</script>

<template>
  <div>
    <a-card style="margin-bottom: 16px;">
      <a-form layout="inline" :model="searchForm" @finish="fetchData">
        <a-form-item label="模型名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入" allow-clear />
        </a-form-item>
        <a-form-item label="提供商">
          <a-select v-model:value="searchForm.provider" placeholder="全部" allow-clear style="width: 140px;">
            <a-select-option value="OpenAI">OpenAI</a-select-option>
            <a-select-option value="Anthropic">Anthropic</a-select-option>
            <a-select-option value="Google">Google</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit">搜索</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card>
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增模型
        </a-button>
      </template>
      <a-table :columns="columns" :data-source="dataSource" :loading="loading" row-key="id" :pagination="{ total, pageSize: 10 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'default'">
              {{ record.status === 'active' ? '启用' : '停用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
            <a-button type="link" size="small" danger @click="handleDelete(record)">删除</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-drawer :title="drawerTitle" :open="drawerVisible" :width="400" @close="drawerVisible = false">
      <a-form :model="formState" layout="vertical" @finish="handleSubmit">
        <a-form-item label="模型名称" name="name" :rules="[{ required: true, message: '请输入模型名称' }]">
          <a-input v-model:value="formState.name" />
        </a-form-item>
        <a-form-item label="提供商" name="provider" :rules="[{ required: true, message: '请输入提供商' }]">
          <a-input v-model:value="formState.provider" />
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-select v-model:value="formState.status">
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="inactive">停用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block>保存</a-button>
        </a-form-item>
      </a-form>
    </a-drawer>
  </div>
</template>
```

- [ ] **Step 3: 验证模型管理**

浏览器访问 `/model`，确认表格渲染、搜索筛选、新增/编辑抽屉、删除确认弹窗均正常工作。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/views/model/ frontend/src/api/model.ts
git commit -m "feat: 实现模型管理页面（CRUD + 搜索筛选）"
```

---

### Task 8: Skills 管理页面

**Files:**
- Modify: `src/views/skill/index.vue`
- Create: `src/api/skill.ts`

- [ ] **Step 1: 创建 Skills API（mock）**

`src/api/skill.ts`:

```ts
export interface SkillItem {
  id: number
  name: string
  description: string
  status: 'active' | 'inactive'
  createdAt: string
}

const mockData: SkillItem[] = [
  { id: 1, name: '代码生成', description: '根据需求自动生成代码', status: 'active', createdAt: '2026-04-01' },
  { id: 2, name: '文档摘要', description: '自动提取文档关键信息', status: 'active', createdAt: '2026-04-05' },
  { id: 3, name: '数据分析', description: '对结构化数据进行统计分析', status: 'inactive', createdAt: '2026-04-12' },
]

export function getSkillListApi(params?: { name?: string; status?: string }): Promise<{ list: SkillItem[]; total: number }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params?.name) list = list.filter((i) => i.name.includes(params.name!))
      if (params?.status) list = list.filter((i) => i.status === params.status)
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createSkillApi(data: Omit<SkillItem, 'id' | 'createdAt'>): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { mockData.push({ ...data, id: Date.now(), createdAt: new Date().toISOString().slice(0, 10) }); resolve() }, 200)
  })
}

export function updateSkillApi(id: number, data: Partial<SkillItem>): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { const item = mockData.find((i) => i.id === id); if (item) Object.assign(item, data); resolve() }, 200)
  })
}

export function deleteSkillApi(id: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { const idx = mockData.findIndex((i) => i.id === id); if (idx > -1) mockData.splice(idx, 1); resolve() }, 200)
  })
}
```

- [ ] **Step 2: 实现 Skills 管理页面**

`src/views/skill/index.vue`:

```vue
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { getSkillListApi, createSkillApi, updateSkillApi, deleteSkillApi } from '../../api/skill'
import type { SkillItem } from '../../api/skill'

const loading = ref(false)
const dataSource = ref<SkillItem[]>([])
const total = ref(0)
const searchForm = reactive({ name: '', status: '' })
const drawerVisible = ref(false)
const drawerTitle = ref('新增 Skill')
const formState = reactive<Partial<SkillItem>>({})
const editingId = ref<number | null>(null)

const columns = [
  { title: '名称', dataIndex: 'name' },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '状态', dataIndex: 'status' },
  { title: '创建时间', dataIndex: 'createdAt' },
  { title: '操作', key: 'action', width: 160 },
]

async function fetchData() {
  loading.value = true
  const res = await getSkillListApi(searchForm)
  dataSource.value = res.list
  total.value = res.total
  loading.value = false
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增 Skill'
  Object.assign(formState, { name: '', description: '', status: 'active' })
  drawerVisible.value = true
}

function handleEdit(record: SkillItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑 Skill'
  Object.assign(formState, { name: record.name, description: record.description, status: record.status })
  drawerVisible.value = true
}

function handleDelete(record: SkillItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定删除 Skill「${record.name}」吗？`,
    async onOk() {
      await deleteSkillApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

async function handleSubmit() {
  if (editingId.value) {
    await updateSkillApi(editingId.value, formState)
    message.success('更新成功')
  } else {
    await createSkillApi(formState as any)
    message.success('创建成功')
  }
  drawerVisible.value = false
  fetchData()
}

onMounted(fetchData)
</script>

<template>
  <div>
    <a-card style="margin-bottom: 16px;">
      <a-form layout="inline" :model="searchForm" @finish="fetchData">
        <a-form-item label="名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入" allow-clear />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchForm.status" placeholder="全部" allow-clear style="width: 120px;">
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="inactive">停用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit">搜索</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card>
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增 Skill
        </a-button>
      </template>
      <a-table :columns="columns" :data-source="dataSource" :loading="loading" row-key="id" :pagination="{ total, pageSize: 10 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'default'">
              {{ record.status === 'active' ? '启用' : '停用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
            <a-button type="link" size="small" danger @click="handleDelete(record)">删除</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-drawer :title="drawerTitle" :open="drawerVisible" :width="400" @close="drawerVisible = false">
      <a-form :model="formState" layout="vertical" @finish="handleSubmit">
        <a-form-item label="名称" name="name" :rules="[{ required: true, message: '请输入名称' }]">
          <a-input v-model:value="formState.name" />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="formState.description" :rows="3" />
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-select v-model:value="formState.status">
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="inactive">停用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block>保存</a-button>
        </a-form-item>
      </a-form>
    </a-drawer>
  </div>
</template>
```

- [ ] **Step 3: 验证 Skills 管理**

浏览器访问 `/skill`，确认表格、搜索、新增/编辑/删除均正常。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/views/skill/ frontend/src/api/skill.ts
git commit -m "feat: 实现 Skills 管理页面"
```

---

### Task 9: 工具管理页面

**Files:**
- Modify: `src/views/tool/index.vue`
- Create: `src/api/tool.ts`

- [ ] **Step 1: 创建工具 API（mock）**

`src/api/tool.ts`:

```ts
export interface ToolItem {
  id: number
  name: string
  type: string
  status: 'active' | 'inactive'
  createdAt: string
}

const mockData: ToolItem[] = [
  { id: 1, name: 'Web Search', type: '搜索', status: 'active', createdAt: '2026-04-01' },
  { id: 2, name: 'Code Executor', type: '执行', status: 'active', createdAt: '2026-04-08' },
  { id: 3, name: 'File Reader', type: '文件', status: 'inactive', createdAt: '2026-04-15' },
]

export function getToolListApi(params?: { name?: string; type?: string }): Promise<{ list: ToolItem[]; total: number }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params?.name) list = list.filter((i) => i.name.includes(params.name!))
      if (params?.type) list = list.filter((i) => i.type === params.type)
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createToolApi(data: Omit<ToolItem, 'id' | 'createdAt'>): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { mockData.push({ ...data, id: Date.now(), createdAt: new Date().toISOString().slice(0, 10) }); resolve() }, 200)
  })
}

export function updateToolApi(id: number, data: Partial<ToolItem>): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { const item = mockData.find((i) => i.id === id); if (item) Object.assign(item, data); resolve() }, 200)
  })
}

export function deleteToolApi(id: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(() => { const idx = mockData.findIndex((i) => i.id === id); if (idx > -1) mockData.splice(idx, 1); resolve() }, 200)
  })
}
```

- [ ] **Step 2: 实现工具管理页面**

`src/views/tool/index.vue`:

```vue
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { getToolListApi, createToolApi, updateToolApi, deleteToolApi } from '../../api/tool'
import type { ToolItem } from '../../api/tool'

const loading = ref(false)
const dataSource = ref<ToolItem[]>([])
const total = ref(0)
const searchForm = reactive({ name: '', type: '' })
const drawerVisible = ref(false)
const drawerTitle = ref('新增工具')
const formState = reactive<Partial<ToolItem>>({})
const editingId = ref<number | null>(null)

const columns = [
  { title: '名称', dataIndex: 'name' },
  { title: '类型', dataIndex: 'type' },
  { title: '状态', dataIndex: 'status' },
  { title: '创建时间', dataIndex: 'createdAt' },
  { title: '操作', key: 'action', width: 160 },
]

async function fetchData() {
  loading.value = true
  const res = await getToolListApi(searchForm)
  dataSource.value = res.list
  total.value = res.total
  loading.value = false
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增工具'
  Object.assign(formState, { name: '', type: '', status: 'active' })
  drawerVisible.value = true
}

function handleEdit(record: ToolItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑工具'
  Object.assign(formState, { name: record.name, type: record.type, status: record.status })
  drawerVisible.value = true
}

function handleDelete(record: ToolItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定删除工具「${record.name}」吗？`,
    async onOk() {
      await deleteToolApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

async function handleSubmit() {
  if (editingId.value) {
    await updateToolApi(editingId.value, formState)
    message.success('更新成功')
  } else {
    await createToolApi(formState as any)
    message.success('创建成功')
  }
  drawerVisible.value = false
  fetchData()
}

onMounted(fetchData)
</script>

<template>
  <div>
    <a-card style="margin-bottom: 16px;">
      <a-form layout="inline" :model="searchForm" @finish="fetchData">
        <a-form-item label="名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入" allow-clear />
        </a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="searchForm.type" placeholder="全部" allow-clear style="width: 120px;">
            <a-select-option value="搜索">搜索</a-select-option>
            <a-select-option value="执行">执行</a-select-option>
            <a-select-option value="文件">文件</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit">搜索</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card>
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增工具
        </a-button>
      </template>
      <a-table :columns="columns" :data-source="dataSource" :loading="loading" row-key="id" :pagination="{ total, pageSize: 10 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'default'">
              {{ record.status === 'active' ? '启用' : '停用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
            <a-button type="link" size="small" danger @click="handleDelete(record)">删除</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-drawer :title="drawerTitle" :open="drawerVisible" :width="400" @close="drawerVisible = false">
      <a-form :model="formState" layout="vertical" @finish="handleSubmit">
        <a-form-item label="名称" name="name" :rules="[{ required: true, message: '请输入名称' }]">
          <a-input v-model:value="formState.name" />
        </a-form-item>
        <a-form-item label="类型" name="type" :rules="[{ required: true, message: '请输入类型' }]">
          <a-input v-model:value="formState.type" />
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-select v-model:value="formState.status">
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="inactive">停用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block>保存</a-button>
        </a-form-item>
      </a-form>
    </a-drawer>
  </div>
</template>
```

- [ ] **Step 3: 验证工具管理**

浏览器访问 `/tool`，确认表格、搜索、CRUD 均正常。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/views/tool/ frontend/src/api/tool.ts
git commit -m "feat: 实现工具管理页面"
```

---

### Task 10: 用户管理页面（系统设置）

**Files:**
- Modify: `src/views/setting/user/index.vue`

- [ ] **Step 1: 实现用户管理页面**

`src/views/setting/user/index.vue`:

```vue
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'

interface UserItem {
  id: number
  username: string
  email: string
  role: string
  status: 'active' | 'inactive'
  createdAt: string
}

const mockData: UserItem[] = [
  { id: 1, username: 'admin', email: 'admin@example.com', role: '超级管理员', status: 'active', createdAt: '2026-01-01' },
  { id: 2, username: 'editor', email: 'editor@example.com', role: '编辑', status: 'active', createdAt: '2026-03-15' },
  { id: 3, username: 'viewer', email: 'viewer@example.com', role: '访客', status: 'inactive', createdAt: '2026-04-10' },
]

const loading = ref(false)
const dataSource = ref<UserItem[]>([])
const searchForm = reactive({ username: '', status: '' })
const drawerVisible = ref(false)
const drawerTitle = ref('新增用户')
const formState = reactive<Partial<UserItem>>({})
const editingId = ref<number | null>(null)

const columns = [
  { title: '用户名', dataIndex: 'username' },
  { title: '邮箱', dataIndex: 'email' },
  { title: '角色', dataIndex: 'role' },
  { title: '状态', dataIndex: 'status' },
  { title: '创建时间', dataIndex: 'createdAt' },
  { title: '操作', key: 'action', width: 160 },
]

function fetchData() {
  loading.value = true
  setTimeout(() => {
    let list = [...mockData]
    if (searchForm.username) list = list.filter((i) => i.username.includes(searchForm.username))
    if (searchForm.status) list = list.filter((i) => i.status === searchForm.status)
    dataSource.value = list
    loading.value = false
  }, 300)
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增用户'
  Object.assign(formState, { username: '', email: '', role: '', status: 'active' })
  drawerVisible.value = true
}

function handleEdit(record: UserItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑用户'
  Object.assign(formState, { username: record.username, email: record.email, role: record.role, status: record.status })
  drawerVisible.value = true
}

function handleDelete(record: UserItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定删除用户「${record.username}」吗？`,
    onOk() {
      const idx = mockData.findIndex((i) => i.id === record.id)
      if (idx > -1) mockData.splice(idx, 1)
      message.success('删除成功')
      fetchData()
    },
  })
}

function handleSubmit() {
  if (editingId.value) {
    const item = mockData.find((i) => i.id === editingId.value)
    if (item) Object.assign(item, formState)
    message.success('更新成功')
  } else {
    mockData.push({ ...formState, id: Date.now(), createdAt: new Date().toISOString().slice(0, 10) } as UserItem)
    message.success('创建成功')
  }
  drawerVisible.value = false
  fetchData()
}

onMounted(fetchData)
</script>

<template>
  <div>
    <a-card style="margin-bottom: 16px;">
      <a-form layout="inline" :model="searchForm" @finish="fetchData">
        <a-form-item label="用户名">
          <a-input v-model:value="searchForm.username" placeholder="请输入" allow-clear />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchForm.status" placeholder="全部" allow-clear style="width: 120px;">
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="inactive">停用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit">搜索</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card>
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增用户
        </a-button>
      </template>
      <a-table :columns="columns" :data-source="dataSource" :loading="loading" row-key="id" :pagination="{ pageSize: 10 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'default'">
              {{ record.status === 'active' ? '启用' : '停用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
            <a-button type="link" size="small" danger @click="handleDelete(record)">删除</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-drawer :title="drawerTitle" :open="drawerVisible" :width="400" @close="drawerVisible = false">
      <a-form :model="formState" layout="vertical" @finish="handleSubmit">
        <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="formState.username" />
        </a-form-item>
        <a-form-item label="邮箱" name="email" :rules="[{ required: true, message: '请输入邮箱' }]">
          <a-input v-model:value="formState.email" />
        </a-form-item>
        <a-form-item label="角色" name="role" :rules="[{ required: true, message: '请选择角色' }]">
          <a-select v-model:value="formState.role">
            <a-select-option value="超级管理员">超级管理员</a-select-option>
            <a-select-option value="编辑">编辑</a-select-option>
            <a-select-option value="访客">访客</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-select v-model:value="formState.status">
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="inactive">停用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block>保存</a-button>
        </a-form-item>
      </a-form>
    </a-drawer>
  </div>
</template>
```

- [ ] **Step 2: 验证用户管理**

浏览器访问 `/setting/user`，确认 CRUD 正常。

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/setting/user/
git commit -m "feat: 实现用户管理页面"
```

---

### Task 11: 角色管理页面

**Files:**
- Modify: `src/views/setting/role/index.vue`
- Create: `src/api/role.ts`

- [ ] **Step 1: 创建角色 API（mock）并实现角色管理页面**

`src/api/role.ts` — 提供 `getRoleListApi`、`createRoleApi`、`updateRoleApi`、`deleteRoleApi` 四个 mock 函数。mock 数据包含：超级管理员（admin）、编辑（editor）、访客（viewer）三个角色，字段为 id、name、code、description、status、createdAt。

`src/views/setting/role/index.vue` — 与用户管理页面结构一致的 CRUD 页面：
- 搜索栏：角色名称 + 状态筛选
- 表格列：角色名称、角色编码、描述、状态、操作（编辑/删除/分配权限）
- 抽屉表单：角色名称、角色编码、描述、状态
- 分配权限按钮打开 `a-modal`，内含 `a-tree` 组件展示权限树（mock 权限数据），支持勾选保存

完整代码参照 Task 10 用户管理的 CRUD 模式，替换字段和 API 调用。额外添加「分配权限」按钮和权限树弹窗。

- [ ] **Step 2: 验证角色管理**

浏览器访问 `/setting/role`，确认 CRUD 和权限分配弹窗正常。

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/setting/role/ frontend/src/api/role.ts
git commit -m "feat: 实现角色管理页面（含权限分配）"
```

---

### Task 12: 权限管理页面

**Files:**
- Modify: `src/views/setting/permission/index.vue`
- Create: `src/api/permission.ts`

- [ ] **Step 1: 创建权限 API（mock）并实现权限管理页面**

`src/api/permission.ts` — 提供 CRUD mock 函数。mock 数据字段：id、name、identifier（权限标识如 `user:read`）、type（菜单/按钮/API）、status、createdAt。

`src/views/setting/permission/index.vue` — 标准 CRUD 页面：
- 搜索栏：权限名称 + 类型筛选
- 表格列：权限名称、权限标识、类型、状态、操作
- 抽屉表单：权限名称、权限标识、类型（下拉选择）、状态

- [ ] **Step 2: 验证并提交**

```bash
git add frontend/src/views/setting/permission/ frontend/src/api/permission.ts
git commit -m "feat: 实现权限管理页面"
```

---

### Task 13: 菜单配置页面（树形表格）

**Files:**
- Modify: `src/views/setting/menu/index.vue`
- Create: `src/api/menu.ts`

- [ ] **Step 1: 创建菜单 API（mock）并实现菜单配置页面**

`src/api/menu.ts` — mock 数据为树形结构，字段：id、name、path、permission、sort、status、parentId、children。包含仪表盘、模型管理、系统设置（含子菜单）等。

`src/views/setting/menu/index.vue` — 树形表格页面：
- 使用 `a-table` 的 `childrenColumnName="children"` 展示树形数据
- 表格列：菜单名称、路由、权限标识、排序、状态、操作（编辑/删除/新增子菜单）
- 抽屉表单：菜单名称、父菜单（`a-tree-select`）、路由、权限标识、排序、状态
- 新增子菜单时自动填充父菜单字段

- [ ] **Step 2: 验证并提交**

```bash
git add frontend/src/views/setting/menu/ frontend/src/api/menu.ts
git commit -m "feat: 实现菜单配置页面（树形表格）"
```

---

### Task 14: 系统配置页面

**Files:**
- Modify: `src/views/setting/config/index.vue`
- Create: `src/api/config.ts`

- [ ] **Step 1: 创建配置 API（mock）并实现系统配置页面**

`src/api/config.ts` — mock 数据字段：id、name、key、value、description。示例数据：站点名称（site.name / Max-Agent）、站点描述（site.description）、文件上传大小限制（upload.maxSize / 10MB）。

`src/views/setting/config/index.vue` — 标准 CRUD 页面：
- 搜索栏：按 key 搜索
- 表格列：配置项名称、key、value、描述、操作
- 抽屉表单：配置项名称、key、value、描述

- [ ] **Step 2: 验证并提交**

```bash
git add frontend/src/views/setting/config/ frontend/src/api/config.ts
git commit -m "feat: 实现系统配置页面"
```

---

### Task 15: 操作日志页面

**Files:**
- Modify: `src/views/setting/operation-log/index.vue`
- Create: `src/api/log.ts`

- [ ] **Step 1: 创建日志 API（mock）并实现操作日志页面**

`src/api/log.ts` — 提供 `getOperationLogApi` 和 `getLoginLogApi` 两个 mock 函数。

操作日志 mock 数据字段：id、operator、module、action、method（GET/POST/PUT/DELETE）、result（成功/失败）、time、detail。

`src/views/setting/operation-log/index.vue` — 只读表格页面：
- 搜索栏：操作人搜索 + 模块筛选 + `a-range-picker` 时间范围
- 表格列：操作人、模块、操作类型、请求方法（用 `a-tag` 着色）、结果、时间、操作（查看详情）
- 查看详情：`a-modal` 展示完整日志信息，不提供编辑/删除

- [ ] **Step 2: 验证并提交**

```bash
git add frontend/src/views/setting/operation-log/ frontend/src/api/log.ts
git commit -m "feat: 实现操作日志页面"
```

---

### Task 16: 登录日志页面

**Files:**
- Modify: `src/views/setting/login-log/index.vue`

- [ ] **Step 1: 实现登录日志页面**

登录日志 mock 数据字段：id、username、ip、location、device、result（成功/失败）、time。

`src/views/setting/login-log/index.vue` — 只读表格页面：
- 搜索栏：用户名搜索 + 登录结果筛选 + `a-range-picker` 时间范围
- 表格列：用户名、登录 IP、登录地点、设备/浏览器、登录结果（`a-tag` 绿色/红色）、登录时间、操作（查看详情）
- 查看详情：`a-modal` 展示完整信息

使用 Task 15 中 `src/api/log.ts` 的 `getLoginLogApi`。

- [ ] **Step 2: 验证并提交**

```bash
git add frontend/src/views/setting/login-log/
git commit -m "feat: 实现登录日志页面"
```

---

### Task 17: 全局验证与清理

**Files:**
- 无新文件

- [ ] **Step 1: 运行构建检查**

```bash
cd frontend && pnpm build
```

确认 TypeScript 编译和 Vite 构建无错误。

- [ ] **Step 2: 全流程验证**

```bash
cd frontend && pnpm dev
```

在浏览器中完整走一遍：
1. 访问 `/` → 重定向到 `/login`
2. 输入 admin / admin123 登录 → 跳转仪表盘
3. 仪表盘统计卡片和图表正常
4. 逐个点击侧边栏菜单，确认每个页面渲染正常
5. 在模型管理页测试新增、编辑、删除
6. 在系统设置下测试各子页面
7. 点击退出登录 → 回到登录页
8. 直接访问 `/dashboard` → 被守卫拦截到登录页

- [ ] **Step 3: 提交最终状态**

```bash
git add -A frontend/
git commit -m "chore: 全局验证通过，清理构建产物"
```
