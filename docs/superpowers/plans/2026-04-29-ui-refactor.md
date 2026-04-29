# UI 改造实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 对前端管理系统进行 6 项 UI 改造：紧凑表格、操作列下拉、状态 Switch 独立列、表单状态默认值、抽屉响应式、浏览器风格 Tab 页。

**Architecture:** 新增 composable (`useDrawerWidth`) 处理抽屉响应式宽度，新增 Pinia store (`tabStore`) 管理 Tab 状态，新增 `TabBar.vue` 组件。各页面模板统一改造表格和表单。所有页面需添加 `defineOptions({ name })` 以配合 `keep-alive`。

**Tech Stack:** Vue 3 (script setup), Ant Design Vue 4.x, Pinia, Vue Router 4, TypeScript

---

## 文件结构

### 新建文件
- `frontend/src/composables/useDrawerWidth.ts` — 抽屉响应式宽度 composable
- `frontend/src/stores/tab.ts` — Tab 页状态管理
- `frontend/src/components/TabBar.vue` — Tab 栏组件

### 修改文件
- `frontend/src/layouts/BasicLayout.vue` — 集成 TabBar + keep-alive
- `frontend/src/router/index.ts` — 路由 meta 添加 title 字段
- `frontend/src/views/setting/user/index.vue` — 表格+操作列+switch+表单+抽屉
- `frontend/src/views/setting/role/index.vue` — 同上 + modal→drawer 迁移
- `frontend/src/views/setting/permission/index.vue` — 表格+操作列+switch+表单+抽屉
- `frontend/src/views/setting/menu/index.vue` — 表格+操作列+switch+表单+抽屉
- `frontend/src/views/setting/config/index.vue` — 表格+操作列+抽屉（无 status）
- `frontend/src/views/setting/operation-log/index.vue` — 表格+操作列+modal→drawer
- `frontend/src/views/setting/login-log/index.vue` — 表格+操作列+modal→drawer
- `frontend/src/views/model/index.vue` — 表格+操作列+switch+表单+抽屉
- `frontend/src/views/skill/index.vue` — 表格+操作列+switch+表单+抽屉
- `frontend/src/views/tool/index.vue` — 表格+操作列+switch+表单+抽屉
- `frontend/src/views/dashboard/index.vue` — 仅添加 defineOptions name

---

## Task 1: 创建 useDrawerWidth composable

**Files:**
- Create: `frontend/src/composables/useDrawerWidth.ts`

- [ ] **Step 1: 创建 composable 文件**

```typescript
import { ref, onMounted, onUnmounted } from 'vue'

export function useDrawerWidth() {
  const drawerWidth = ref(getWidth())

  function getWidth() {
    const w = window.innerWidth
    if (w <= 768) return '100%'
    if (w <= 1200) return '50%'
    return 520
  }

  function onResize() {
    drawerWidth.value = getWidth()
  }

  onMounted(() => window.addEventListener('resize', onResize))
  onUnmounted(() => window.removeEventListener('resize', onResize))

  return { drawerWidth }
}
```

- [ ] **Step 2: 验证构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功，无错误

- [ ] **Step 3: 提交**

```bash
git add frontend/src/composables/useDrawerWidth.ts
git commit -m "feat: add useDrawerWidth composable for responsive drawer width"
```

---

## Task 2: 创建 Tab Store

**Files:**
- Create: `frontend/src/stores/tab.ts`

- [ ] **Step 1: 创建 tab store**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import type { RouteLocationNormalized } from 'vue-router'

export interface TabItem {
  path: string
  title: string
  name: string
}

export const useTabStore = defineStore('tab', () => {
  const tabs = ref<TabItem[]>([])
  const activeTab = ref('')

  function addTab(route: RouteLocationNormalized) {
    const title = (route.meta?.title as string) || route.path
    const name = (route.name as string) || ''
    if (!name) return
    const exists = tabs.value.find(t => t.path === route.path)
    if (!exists) {
      tabs.value.push({ path: route.path, title, name })
    }
    activeTab.value = route.path
  }

  function removeTab(path: string, router: ReturnType<typeof useRouter>) {
    const idx = tabs.value.findIndex(t => t.path === path)
    if (idx === -1) return
    tabs.value.splice(idx, 1)
    if (activeTab.value === path) {
      const next = tabs.value[idx] || tabs.value[idx - 1]
      if (next) {
        activeTab.value = next.path
        router.push(next.path)
      }
    }
  }

  function closeLeft(path: string) {
    const idx = tabs.value.findIndex(t => t.path === path)
    if (idx > 0) tabs.value.splice(0, idx)
  }

  function closeRight(path: string) {
    const idx = tabs.value.findIndex(t => t.path === path)
    if (idx < tabs.value.length - 1) tabs.value.splice(idx + 1)
  }

  function closeOthers(path: string) {
    tabs.value = tabs.value.filter(t => t.path === path)
  }

  function closeAll(router: ReturnType<typeof useRouter>) {
    tabs.value = []
    activeTab.value = ''
    router.push('/dashboard')
  }

  const cachedNames = ref<string[]>([])
  function updateCachedNames() {
    cachedNames.value = tabs.value.map(t => t.name).filter(Boolean)
  }

  return {
    tabs, activeTab, cachedNames,
    addTab, removeTab, closeLeft, closeRight, closeOthers, closeAll, updateCachedNames,
  }
})
```

- [ ] **Step 2: 验证构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/stores/tab.ts
git commit -m "feat: add tab store for multi-tab navigation state"
```

---

## Task 3: 创建 TabBar 组件

**Files:**
- Create: `frontend/src/components/TabBar.vue`

- [ ] **Step 1: 创建 TabBar 组件**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTabStore } from '@/stores/tab'

const router = useRouter()
const tabStore = useTabStore()

const contextMenu = ref({ visible: false, x: 0, y: 0, path: '' })

function onTabClick(path: string) {
  tabStore.activeTab = path
  router.push(path)
}

function onClose(path: string, e: Event) {
  e.stopPropagation()
  tabStore.removeTab(path, router)
  tabStore.updateCachedNames()
}

function onContextMenu(e: MouseEvent, path: string) {
  e.preventDefault()
  contextMenu.value = { visible: true, x: e.clientX, y: e.clientY, path }
}

function closeContextMenu() {
  contextMenu.value.visible = false
}

function handleContextAction(action: string) {
  const path = contextMenu.value.path
  switch (action) {
    case 'closeCurrent': tabStore.removeTab(path, router); break
    case 'closeLeft': tabStore.closeLeft(path); break
    case 'closeRight': tabStore.closeRight(path); break
    case 'closeOthers': tabStore.closeOthers(path); break
    case 'closeAll': tabStore.closeAll(router); break
  }
  tabStore.updateCachedNames()
  closeContextMenu()
}
</script>

<template>
  <div class="tab-bar" @click="closeContextMenu">
    <div class="tab-bar-scroll">
      <div
        v-for="tab in tabStore.tabs"
        :key="tab.path"
        class="tab-item"
        :class="{ active: tabStore.activeTab === tab.path }"
        @click="onTabClick(tab.path)"
        @contextmenu="onContextMenu($event, tab.path)"
      >
        <span class="tab-title">{{ tab.title }}</span>
        <span class="tab-close" @click="onClose(tab.path, $event)">&times;</span>
      </div>
    </div>
    <teleport to="body">
      <div
        v-if="contextMenu.visible"
        class="tab-context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      >
        <div class="menu-item" @click="handleContextAction('closeCurrent')">关闭当前</div>
        <div class="menu-item" @click="handleContextAction('closeLeft')">关闭左侧</div>
        <div class="menu-item" @click="handleContextAction('closeRight')">关闭右侧</div>
        <div class="menu-item" @click="handleContextAction('closeOthers')">关闭其他</div>
        <div class="menu-item" @click="handleContextAction('closeAll')">关闭全部</div>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
.tab-bar {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 4px 8px 0;
}
.tab-bar-scroll {
  display: flex;
  overflow-x: auto;
  gap: 4px;
}
.tab-bar-scroll::-webkit-scrollbar { height: 0; }
.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #f0f0f0;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  white-space: nowrap;
  font-size: 13px;
  color: #666;
  background: #fafafa;
  transition: all 0.2s;
}
.tab-item:hover { color: #1890ff; background: #e6f7ff; }
.tab-item.active {
  color: #1890ff;
  background: #fff;
  border-color: #d9d9d9;
  border-bottom-color: #fff;
}
.tab-close {
  font-size: 14px;
  line-height: 1;
  color: #999;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tab-close:hover { background: #ddd; color: #333; }
.tab-context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 1050;
  padding: 4px 0;
}
.menu-item {
  padding: 6px 16px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}
.menu-item:hover { background: #e6f7ff; color: #1890ff; }
</style>
```

- [ ] **Step 2: 验证构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/TabBar.vue
git commit -m "feat: add TabBar component with context menu"
```

---

## Task 4: 更新路由 meta 和 BasicLayout

**Files:**
- Modify: `frontend/src/router/index.ts` — 每个路由添加 `meta: { title: '...' }`
- Modify: `frontend/src/layouts/BasicLayout.vue` — 集成 TabBar + keep-alive + 路由监听

- [ ] **Step 1: 更新路由 meta**

在 `router/index.ts` 中，为每个业务路由添加 `meta.title`：

```typescript
{ path: '/dashboard', name: 'Dashboard', meta: { title: '仪表盘' }, component: () => import('@/views/dashboard/index.vue') },
{ path: '/model', name: 'Model', meta: { title: '模型管理' }, component: () => import('@/views/model/index.vue') },
{ path: '/skill', name: 'Skill', meta: { title: '技能管理' }, component: () => import('@/views/skill/index.vue') },
{ path: '/tool', name: 'Tool', meta: { title: '工具管理' }, component: () => import('@/views/tool/index.vue') },
```

setting 子路由同理：
```typescript
{ path: '/setting/user', name: 'User', meta: { title: '用户管理' }, ... },
{ path: '/setting/role', name: 'Role', meta: { title: '角色管理' }, ... },
{ path: '/setting/permission', name: 'Permission', meta: { title: '权限管理' }, ... },
{ path: '/setting/menu', name: 'Menu', meta: { title: '菜单管理' }, ... },
{ path: '/setting/config', name: 'Config', meta: { title: '系统配置' }, ... },
{ path: '/setting/operation-log', name: 'OperationLog', meta: { title: '操作日志' }, ... },
{ path: '/setting/login-log', name: 'LoginLog', meta: { title: '登录日志' }, ... },
```

- [ ] **Step 2: 更新 BasicLayout.vue**

在 `BasicLayout.vue` 中：

1. 导入 TabBar 和 tabStore：
```typescript
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import TabBar from '@/components/TabBar.vue'
import { useTabStore } from '@/stores/tab'

const route = useRoute()
const tabStore = useTabStore()

watch(() => route.path, () => {
  if (route.path !== '/login') {
    tabStore.addTab(route)
    tabStore.updateCachedNames()
  }
}, { immediate: true })
```

2. 修改 `<a-layout-content>` 区域，在 `<router-view>` 上方添加 `<TabBar />`，并用 `keep-alive` 包裹：
```vue
<a-layout-content style="margin: 16px; padding: 16px; background: #fff; min-height: 280px;">
  <TabBar />
  <router-view v-slot="{ Component }">
    <keep-alive :include="tabStore.cachedNames">
      <component :is="Component" />
    </keep-alive>
  </router-view>
</a-layout-content>
```

- [ ] **Step 3: 验证构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功

- [ ] **Step 4: 提交**

```bash
git add frontend/src/router/index.ts frontend/src/layouts/BasicLayout.vue
git commit -m "feat: integrate TabBar with keep-alive in BasicLayout"
```

---

## Task 5: 为所有页面组件添加 defineOptions name

**Files:**
- Modify: 所有 `views/` 下的页面组件

`keep-alive` 的 `include` 依赖组件 `name`。所有 `<script setup>` 页面需要添加 `defineOptions`。

- [ ] **Step 1: 在每个页面的 `<script setup>` 块顶部添加 defineOptions**

```typescript
// views/dashboard/index.vue
defineOptions({ name: 'Dashboard' })

// views/model/index.vue
defineOptions({ name: 'Model' })

// views/skill/index.vue
defineOptions({ name: 'Skill' })

// views/tool/index.vue
defineOptions({ name: 'Tool' })

// views/setting/user/index.vue
defineOptions({ name: 'User' })

// views/setting/role/index.vue
defineOptions({ name: 'Role' })

// views/setting/permission/index.vue
defineOptions({ name: 'Permission' })

// views/setting/menu/index.vue
defineOptions({ name: 'Menu' })

// views/setting/config/index.vue
defineOptions({ name: 'Config' })

// views/setting/operation-log/index.vue
defineOptions({ name: 'OperationLog' })

// views/setting/login-log/index.vue
defineOptions({ name: 'LoginLog' })
```

name 值必须与 `router/index.ts` 中对应路由的 `name` 字段完全一致。

- [ ] **Step 2: 验证构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/
git commit -m "feat: add defineOptions name to all page components for keep-alive"
```

---

## Task 6: 改造有状态字段的 CRUD 页面（user, role, permission, model, skill, tool）

**Files:**
- Modify: 6 个有 status 字段的 CRUD 页面

对每个页面统一执行以下改造：

### 6a. 表格紧凑化

- [ ] **Step 1: 所有 `<a-table>` 添加 `size="small"`**

```vue
<!-- Before -->
<a-table :columns="columns" :data-source="dataSource" ...>

<!-- After -->
<a-table size="small" :columns="columns" :data-source="dataSource" ...>
```

### 6b. 操作列改为下拉按钮

- [ ] **Step 2: 替换操作列模板**

将每个页面的操作列 slot 从独立按钮改为 `a-dropdown`：

```vue
<!-- Before -->
<template #bodyCell="{ column, record }">
  <template v-if="column.key === 'action'">
    <a-button type="link" @click="handleEdit(record)">编辑</a-button>
    <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
  </template>
</template>

<!-- After -->
<template #bodyCell="{ column, record }">
  <template v-if="column.dataIndex === 'status'">
    <a-switch
      :checked="record.status === 'active'"
      checked-children="启用"
      un-checked-children="停用"
      @change="handleStatusChange(record)"
    />
  </template>
  <template v-if="column.key === 'action'">
    <a-dropdown>
      <a-button type="primary" size="small">
        操作 <DownOutlined />
      </a-button>
      <template #overlay>
        <a-menu @click="({ key }) => handleMenuClick(key, record)">
          <a-menu-item key="edit"><EditOutlined /> 编辑</a-menu-item>
          <a-menu-item key="delete" danger><DeleteOutlined /> 删除</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </template>
</template>
```

对于角色管理页面，菜单中额外添加：
```vue
<a-menu-item key="permission"><SafetyOutlined /> 分配权限</a-menu-item>
```

对于菜单管理页面，菜单中额外添加：
```vue
<a-menu-item key="addChild"><PlusOutlined /> 新增子菜单</a-menu-item>
```

- [ ] **Step 3: 添加 handleMenuClick 和 handleStatusChange 方法**

```typescript
import { DownOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { Modal, message } from 'ant-design-vue'

function handleMenuClick(key: string, record: any) {
  switch (key) {
    case 'edit': handleEdit(record); break
    case 'delete': handleDelete(record); break
    // 角色页面额外: case 'permission': handlePermission(record); break
    // 菜单页面额外: case 'addChild': handleAddChild(record); break
  }
}

async function handleStatusChange(record: any) {
  const newStatus = record.status === 'active' ? 'inactive' : 'active'
  try {
    await updateXxxApi({ ...record, status: newStatus })
    record.status = newStatus
    message.success('状态更新成功')
  } catch {
    message.error('状态更新失败')
  }
}
```

### 6c. 状态列独立 + columns 调整

- [ ] **Step 4: 修改 columns 定义**

在操作列之前插入状态列，操作列宽度缩减：

```typescript
// 在操作列之前添加
{ title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' },
// 操作列宽度改为 90
{ title: '操作', key: 'action', width: 90, align: 'center' },
```

移除原来用 `a-tag` 渲染 status 的模板代码（已被 switch 替代）。

### 6d. 表单状态字段默认值

- [ ] **Step 5: 修改新增表单的状态字段**

```vue
<!-- 表单中的状态字段 -->
<a-form-item label="状态" name="status">
  <a-select v-model:value="formState.status" placeholder="请选择状态">
    <a-select-option value="active">启用</a-select-option>
    <a-select-option value="inactive">停用</a-select-option>
  </a-select>
</a-form-item>
```

新增时 formState 初始化不设置 status 默认值：
```typescript
function handleAdd() {
  formState.value = { name: '', /* 其他字段 */ }  // 不包含 status
  drawerVisible.value = true
}
```

提交时自动补充默认值：
```typescript
async function handleSubmit() {
  await formRef.value.validate()
  const data = { ...formState.value }
  if (!editingRecord.value && !data.status) {
    data.status = 'inactive'
  }
  // 调用 API...
}
```

### 6e. 抽屉响应式宽度

- [ ] **Step 6: 引入 useDrawerWidth 并绑定**

```typescript
import { useDrawerWidth } from '@/composables/useDrawerWidth'
const { drawerWidth } = useDrawerWidth()
```

```vue
<!-- Before -->
<a-drawer :width="480" ...>

<!-- After -->
<a-drawer :width="drawerWidth" ...>
```

- [ ] **Step 7: 验证构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功

- [ ] **Step 8: 提交**

```bash
git add frontend/src/views/
git commit -m "feat: refactor CRUD pages with compact table, dropdown actions, switch status, responsive drawer"
```

---

## Task 7: 改造无状态字段的页面（config, operation-log, login-log）

**Files:**
- Modify: `frontend/src/views/setting/config/index.vue`
- Modify: `frontend/src/views/setting/operation-log/index.vue`
- Modify: `frontend/src/views/setting/login-log/index.vue`

### ConfigManagement（无 status，有 CRUD）

- [ ] **Step 1: config 页面改造**

1. `a-table` 添加 `size="small"`
2. 操作列改为 `a-dropdown` 下拉按钮（编辑、删除）
3. 操作列宽度改为 90
4. `a-drawer` 的 `:width` 改为 `drawerWidth`（引入 useDrawerWidth）
5. 添加 `handleMenuClick` 方法
6. 导入图标：`DownOutlined, EditOutlined, DeleteOutlined`

### OperationLog（只读，详情用 Modal → Drawer）

- [ ] **Step 2: operation-log 页面改造**

1. `a-table` 添加 `size="small"`
2. 操作列「查看详情」按钮改为下拉按钮（只有一项「查看详情」，但保持统一风格）
3. 将 `a-modal` 替换为 `a-drawer`：

```vue
<!-- Before -->
<a-modal v-model:open="detailVisible" title="操作日志详情" :width="640" :footer="null">
  <a-descriptions bordered>...</a-descriptions>
</a-modal>

<!-- After -->
<a-drawer v-model:open="detailVisible" title="操作日志详情" :width="drawerWidth">
  <a-descriptions bordered>...</a-descriptions>
</a-drawer>
```

4. 引入 `useDrawerWidth`

### LoginLog（只读，详情用 Modal → Drawer）

- [ ] **Step 3: login-log 页面改造**

与 operation-log 相同的改造：
1. `a-table` 添加 `size="small"`
2. 操作列改为下拉按钮
3. `a-modal` → `a-drawer`，宽度用 `drawerWidth`
4. 引入 `useDrawerWidth`

- [ ] **Step 4: 验证构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功

- [ ] **Step 5: 提交**

```bash
git add frontend/src/views/setting/config/index.vue frontend/src/views/setting/operation-log/index.vue frontend/src/views/setting/login-log/index.vue
git commit -m "feat: refactor config and log pages with compact table, dropdown actions, modal to drawer"
```

---

## Task 8: 角色管理页面 Modal → Drawer 迁移

**Files:**
- Modify: `frontend/src/views/setting/role/index.vue`

角色管理页面有一个额外的 `a-modal` 用于分配权限（内含 `a-tree`），需要迁移为 `a-drawer`。

- [ ] **Step 1: 将权限分配 Modal 改为 Drawer**

```vue
<!-- Before -->
<a-modal v-model:open="permissionVisible" title="分配权限" @ok="handlePermissionSubmit">
  <a-tree checkable default-expand-all .../>
</a-modal>

<!-- After -->
<a-drawer v-model:open="permissionVisible" title="分配权限" :width="drawerWidth">
  <a-tree checkable default-expand-all .../>
  <template #footer>
    <div style="text-align: right;">
      <a-button style="margin-right: 8px;" @click="permissionVisible = false">取消</a-button>
      <a-button type="primary" :loading="permissionLoading" @click="handlePermissionSubmit">确定</a-button>
    </div>
  </template>
</a-drawer>
```

- [ ] **Step 2: 验证构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/setting/role/index.vue
git commit -m "feat: migrate role permission modal to drawer"
```

---

## Task 9: 菜单管理页面特殊处理

**Files:**
- Modify: `frontend/src/views/setting/menu/index.vue`

菜单管理是树形表格（无分页），操作列有三个按钮（编辑、删除、新增子菜单），需要确保下拉菜单包含所有三项。

- [ ] **Step 1: 确认菜单页面的下拉菜单包含三项**

```vue
<a-menu @click="({ key }) => handleMenuClick(key, record)">
  <a-menu-item key="edit"><EditOutlined /> 编辑</a-menu-item>
  <a-menu-item key="addChild"><PlusOutlined /> 新增子菜单</a-menu-item>
  <a-menu-divider />
  <a-menu-item key="delete" danger><DeleteOutlined /> 删除</a-menu-item>
</a-menu>
```

handleMenuClick 中添加：
```typescript
case 'addChild': handleAddChild(record); break
```

此改造已在 Task 6 中覆盖，此 Task 仅做确认和验证。

- [ ] **Step 2: 验证构建并手动检查菜单页面**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功

- [ ] **Step 3: 提交（如有额外修改）**

---

## Task 10: 全量构建验证 + 手动测试

- [ ] **Step 1: 全量构建**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm build`
Expected: 构建成功，无 warning

- [ ] **Step 2: 启动开发服务器手动验证**

Run: `cd /Users/liang/code/max-agent/frontend && pnpm dev`

验证清单：
1. 所有表格显示为紧凑尺寸
2. 操作列为「操作 ▾」下拉按钮，点击展开菜单
3. 有状态字段的页面显示 Switch 列，可切换
4. 新增表单中状态字段无默认值
5. 抽屉宽度随窗口大小变化
6. Tab 栏正常显示，点击菜单新增 tab
7. Tab 右键菜单功能正常（关闭左侧/右侧/其他/全部）
8. 页面切换后 keep-alive 保持状态
9. 日志页面详情改为抽屉展示
10. 角色权限分配改为抽屉展示

- [ ] **Step 3: 最终提交（如有修复）**
