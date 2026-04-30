# Admin Workbench UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 调整后台工作台布局，让 Tabs 外提、标题区变轻、表格稳定撑满剩余高度，并先从权限配置链路修复管理员看不到模型管理、Skills 管理、工具管理入口的问题。

**Architecture:** 后端只做权限配置链路的最小修复与回归保护：为 seed 补齐缺失的菜单权限，并加测试保证 seeded menu 的 `permission` 都有对应权限定义。前端保留现有页面与路由结构，重点改 `BasicLayout.vue`、`TabBar.vue`、`useTableScrollY.ts` 和公共样式，再将各列表页接入统一的高度刷新与蓝系 Tag 主题。

**Tech Stack:** FastAPI seed script, pytest, Vue 3, TypeScript, Pinia, Vue Router 4, Ant Design Vue 4, Vite

---

## File Map

### Create
- `backend/tests/test_seed_menu_permissions.py` — 回归测试：每个 seed 菜单权限都必须有对应权限定义

### Modify
- `backend/app/db/seed.py` — 补齐 `dashboard:view`、`model:view`、`skill:view`、`tool:view` 权限定义
- `frontend/src/layouts/BasicLayout.vue` — 将 Tabs 移到内容壳层外，压缩页面标识区
- `frontend/src/components/TabBar.vue` — 调整为工作台顶部导航带样式
- `frontend/src/composables/useTableScrollY.ts` — 改为基于真实容器高度计算表格滚动区
- `frontend/src/style.css` — 全局工作台骨架、高度链路、蓝系 Tag 主题
- `frontend/src/views/model/index.vue` — 接入表格高度刷新
- `frontend/src/views/skill/index.vue` — 接入表格高度刷新
- `frontend/src/views/tool/index.vue` — 接入表格高度刷新
- `frontend/src/views/setting/user/index.vue` — 接入表格高度刷新，统一内置用户 Tag 主题
- `frontend/src/views/setting/role/index.vue` — 接入表格高度刷新
- `frontend/src/views/setting/permission/index.vue` — 接入表格高度刷新
- `frontend/src/views/setting/menu/index.vue` — 接入表格高度刷新
- `frontend/src/views/setting/config/index.vue` — 接入表格高度刷新
- `frontend/src/views/setting/operation-log/index.vue` — 接入表格高度刷新，统一方法/结果 Tag 主题
- `frontend/src/views/setting/login-log/index.vue` — 接入表格高度刷新，统一结果 Tag 主题

---

### Task 1: 修复后台菜单权限配置并加回归测试

**Files:**
- Create: `backend/tests/test_seed_menu_permissions.py`
- Modify: `backend/app/db/seed.py`

- [ ] **Step 1: 写失败的权限配置回归测试**

创建 `backend/tests/test_seed_menu_permissions.py`：

```python
from app.db.seed import ALL_MENUS, PERMISSIONS



def test_every_seeded_menu_permission_has_a_permission_definition() -> None:
    permission_ids = {item["identifier"] for item in PERMISSIONS}
    menu_permissions = {item["permission"] for item in ALL_MENUS if item["permission"]}

    assert menu_permissions <= permission_ids
```

- [ ] **Step 2: 运行测试，确认当前先失败**

Run:

```bash
cd /Users/liang/code/max-agent/backend && uv sync --group dev && uv run pytest tests/test_seed_menu_permissions.py -q
```

Expected: `AssertionError`，并显示缺失的权限至少包含 `dashboard:view`、`model:view`、`skill:view`、`tool:view`。

- [ ] **Step 3: 在 seed 中补齐缺失权限定义**

修改 `backend/app/db/seed.py` 的 `PERMISSIONS` 常量，在现有系统设置权限之前插入这 4 项：

```python
PERMISSIONS = [
    {"name": "仪表盘", "identifier": "dashboard:view", "type": "菜单", "status": "active"},
    {"name": "模型管理", "identifier": "model:view", "type": "菜单", "status": "active"},
    {"name": "Skills管理", "identifier": "skill:view", "type": "菜单", "status": "active"},
    {"name": "工具管理", "identifier": "tool:view", "type": "菜单", "status": "active"},
    {"name": "系统设置查看", "identifier": "setting:view", "type": "菜单", "status": "active"},
    {"name": "用户管理", "identifier": "setting:user", "type": "菜单", "status": "active"},
    {"name": "角色管理", "identifier": "setting:role", "type": "菜单", "status": "active"},
    {"name": "权限管理", "identifier": "setting:permission", "type": "菜单", "status": "active"},
    {"name": "菜单配置", "identifier": "setting:menu", "type": "菜单", "status": "active"},
    {"name": "系统配置", "identifier": "setting:config", "type": "菜单", "status": "active"},
    {"name": "操作日志", "identifier": "setting:operation-log", "type": "菜单", "status": "active"},
    {"name": "登录日志", "identifier": "setting:login-log", "type": "菜单", "status": "active"},
    {"name": "用户新增", "identifier": "user:create", "type": "按钮", "status": "active"},
    {"name": "用户编辑", "identifier": "user:update", "type": "按钮", "status": "active"},
    {"name": "用户删除", "identifier": "user:delete", "type": "按钮", "status": "active"},
    {"name": "用户状态", "identifier": "user:status", "type": "按钮", "status": "active"},
    {"name": "角色新增", "identifier": "role:create", "type": "按钮", "status": "active"},
    {"name": "角色编辑", "identifier": "role:update", "type": "按钮", "status": "active"},
    {"name": "角色删除", "identifier": "role:delete", "type": "按钮", "status": "active"},
    {"name": "角色状态", "identifier": "role:status", "type": "按钮", "status": "active"},
    {"name": "角色分配权限", "identifier": "role:assign-permission", "type": "按钮", "status": "active"},
    {"name": "权限新增", "identifier": "permission:create", "type": "按钮", "status": "active"},
    {"name": "权限编辑", "identifier": "permission:update", "type": "按钮", "status": "active"},
    {"name": "权限删除", "identifier": "permission:delete", "type": "按钮", "status": "active"},
    {"name": "权限状态", "identifier": "permission:status", "type": "按钮", "status": "active"},
    {"name": "菜单新增", "identifier": "menu:create", "type": "按钮", "status": "active"},
    {"name": "菜单编辑", "identifier": "menu:update", "type": "按钮", "status": "active"},
    {"name": "菜单删除", "identifier": "menu:delete", "type": "按钮", "status": "active"},
    {"name": "菜单状态", "identifier": "menu:status", "type": "按钮", "status": "active"},
    {"name": "配置新增", "identifier": "config:create", "type": "按钮", "status": "active"},
    {"name": "配置编辑", "identifier": "config:update", "type": "按钮", "status": "active"},
    {"name": "配置删除", "identifier": "config:delete", "type": "按钮", "status": "active"},
    {"name": "操作日志查看", "identifier": "operation-log:read", "type": "API", "status": "active"},
    {"name": "登录日志查看", "identifier": "login-log:read", "type": "API", "status": "active"},
]
```

- [ ] **Step 4: 重跑测试并重新执行 seed**

Run:

```bash
cd /Users/liang/code/max-agent/backend && uv run pytest tests/test_seed_menu_permissions.py -q && uv run python app/db/seed.py
```

Expected: 先输出 `1 passed`，随后输出 `Seed completed.`。

- [ ] **Step 5: 手工验证管理员登录返回菜单**

Run:

```bash
curl -s http://127.0.0.1:8000/api/auth/me -H "Authorization: Bearer <admin-token>"
```

Expected: 返回 JSON 中的 `menus` 包含 `/model`、`/skill`、`/tool`。

- [ ] **Step 6: Commit**

```bash
git add backend/app/db/seed.py backend/tests/test_seed_menu_permissions.py
git commit -m "fix: seed missing menu permissions for admin menus"
```

---

### Task 2: 外提 Tabs 并压缩页面标识区

**Files:**
- Modify: `frontend/src/layouts/BasicLayout.vue`
- Modify: `frontend/src/components/TabBar.vue`

- [ ] **Step 1: 先在浏览器里确认现状**

Run:

```bash
cd /Users/liang/code/max-agent/frontend && pnpm dev
```

Expected: 打开后台后能复现当前结构问题：Tabs 在内容卡片内部，标题区偏高，占用了表格空间。

- [ ] **Step 2: 调整 `BasicLayout.vue` 的层级，让 Tabs 脱离内容卡片**

把 `frontend/src/layouts/BasicLayout.vue` 的内容区调整成下面结构：

```vue
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

  <TabBar class="layout-tabbar" />

  <a-layout-content class="layout-content-shell">
    <div class="workspace-shell">
      <div class="page-shell" :style="pageAccentStyle">
        <div class="page-shell-header">
          <span class="page-shell-accent"></span>
          <span>{{ currentPageTitle }}</span>
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
```

同时把样式改成更轻的页面标识：

```vue
<style scoped>
.layout-tabbar {
  padding: 12px 16px 0;
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
  border: 1px solid #eef1f6;
  border-radius: 16px;
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

.page-shell-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  background: #fff;
}
</style>
```

- [ ] **Step 3: 把 `TabBar.vue` 调整成工作台导航带样式**

将 `frontend/src/components/TabBar.vue` 的样式段替换为：

```vue
<style scoped>
.tab-bar {
  border-radius: 16px 16px 0 0;
  background: linear-gradient(180deg, #f8fbff 0%, #fdfefe 100%);
  border: 1px solid #e7edf6;
  border-bottom: none;
  padding: 10px 14px 0;
}

.tab-bar-scroll {
  display: flex;
  overflow-x: auto;
  gap: 8px;
}

.tab-bar-scroll::-webkit-scrollbar {
  height: 0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  white-space: nowrap;
  font-size: 13px;
  color: #667085;
  background: #edf3ff;
  transition: all 0.2s;
}

.tab-item:hover {
  color: #1677ff;
  background: #f3f7ff;
}

.tab-item.active {
  color: #1677ff;
  background: #fff;
  border-color: #dbe7ff;
  box-shadow: 0 -1px 0 #dbe7ff, 0 10px 24px rgba(22, 119, 255, 0.08);
}

.tab-title {
  line-height: 1;
}

.tab-close {
  font-size: 14px;
  line-height: 1;
  color: #98a2b3;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-close:hover {
  background: #dbe7ff;
  color: #344054;
}

.tab-context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
  z-index: 1050;
  padding: 6px 0;
}

.menu-item {
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}

.menu-item:hover {
  background: #eef4ff;
  color: #1677ff;
}
</style>
```

- [ ] **Step 4: 构建确认层级调整没有破坏页面**

Run:

```bash
cd /Users/liang/code/max-agent/frontend && pnpm build
```

Expected: Vite 构建成功，没有 TypeScript 报错。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/layouts/BasicLayout.vue frontend/src/components/TabBar.vue
git commit -m "feat: move tabs above workspace shell"
```

---

### Task 3: 重做动态表格高度与全局工作台样式

**Files:**
- Modify: `frontend/src/composables/useTableScrollY.ts`
- Modify: `frontend/src/style.css`

- [ ] **Step 1: 写出当前高度算法的失败点**

在浏览器里打开任意列表页，缩放窗口高度，确认当前 `reservedBottomSpace = 88` 会出现“表格没撑满”或“页面总高度超出屏幕”的情况。

- [ ] **Step 2: 用真实容器高度重写 `useTableScrollY.ts`**

将 `frontend/src/composables/useTableScrollY.ts` 替换为：

```ts
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

export function useTableScrollY(minHeight = 240) {
  const tableSectionRef = ref<HTMLElement | null>(null)
  const scrollY = ref(minHeight)
  let resizeObserver: ResizeObserver | null = null
  let frameId = 0

  const updateScrollY = () => {
    cancelAnimationFrame(frameId)
    frameId = requestAnimationFrame(() => {
      nextTick(() => {
        const section = tableSectionRef.value
        if (!section) {
          return
        }

        const tableWrapper = section.querySelector<HTMLElement>('.ant-table-wrapper')
        const tableHeader = tableWrapper?.querySelector<HTMLElement>('.ant-table-thead')
        const pagination = tableWrapper?.querySelector<HTMLElement>('.ant-pagination')
        const sectionStyle = window.getComputedStyle(section)
        const sectionPaddingTop = Number.parseFloat(sectionStyle.paddingTop || '0')
        const sectionPaddingBottom = Number.parseFloat(sectionStyle.paddingBottom || '0')
        const availableHeight =
          section.clientHeight -
          sectionPaddingTop -
          sectionPaddingBottom -
          (tableHeader?.offsetHeight ?? 0) -
          (pagination?.offsetHeight ?? 0) -
          (pagination ? 16 : 0)

        scrollY.value = Math.max(minHeight, availableHeight)
      })
    })
  }

  onMounted(() => {
    updateScrollY()
    window.addEventListener('resize', updateScrollY)
    resizeObserver = new ResizeObserver(updateScrollY)
    if (tableSectionRef.value) {
      resizeObserver.observe(tableSectionRef.value)
    }
  })

  onBeforeUnmount(() => {
    cancelAnimationFrame(frameId)
    window.removeEventListener('resize', updateScrollY)
    resizeObserver?.disconnect()
  })

  return {
    tableSectionRef,
    tableScrollY: computed(() => scrollY.value),
    updateTableScrollY: updateScrollY,
  }
}
```

- [ ] **Step 3: 在 `style.css` 中补全高度链路与蓝系 Tag 基础样式**

将 `frontend/src/style.css` 的相关段落调整为：

```css
body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  background: #f5f7fa;
}

#app {
  height: 100vh;
}

.page-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.page-section {
  padding: 20px;
}

.page-section + .page-section {
  border-top: 1px solid #f2f4f7;
}

.page-toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.page-toolbar .ant-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 0;
  flex: 1;
}

.page-toolbar .ant-form-item {
  margin-bottom: 0;
}

.page-toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.page-table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-table-section > .ant-table-wrapper,
.page-table-section > .ant-spin-nested-loading {
  flex: 1;
  min-height: 0;
}

.page-status-tag.ant-tag {
  color: #1d4ed8;
  background: #eef4ff;
  border-color: #c7d7fe;
}

.page-status-tag--muted.ant-tag {
  color: #3558b7;
  background: #f5f8ff;
  border-color: #d9e3ff;
}

.page-method-tag.ant-tag {
  color: #2146a6;
  background: #edf3ff;
  border-color: #cbd8ff;
}

.page-method-tag--soft.ant-tag {
  color: #4964c8;
  background: #f5f8ff;
  border-color: #dce5ff;
}
```

- [ ] **Step 4: 构建确认共享样式和 composable 可通过**

Run:

```bash
cd /Users/liang/code/max-agent/frontend && pnpm build
```

Expected: 构建成功。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/composables/useTableScrollY.ts frontend/src/style.css
git commit -m "feat: rebuild table scroll height for workbench layout"
```

---

### Task 4: 让所有列表页接入统一高度刷新与蓝系 Tag 主题

**Files:**
- Modify: `frontend/src/views/model/index.vue`
- Modify: `frontend/src/views/skill/index.vue`
- Modify: `frontend/src/views/tool/index.vue`
- Modify: `frontend/src/views/setting/user/index.vue`
- Modify: `frontend/src/views/setting/role/index.vue`
- Modify: `frontend/src/views/setting/permission/index.vue`
- Modify: `frontend/src/views/setting/menu/index.vue`
- Modify: `frontend/src/views/setting/config/index.vue`
- Modify: `frontend/src/views/setting/operation-log/index.vue`
- Modify: `frontend/src/views/setting/login-log/index.vue`

- [ ] **Step 1: 给所有列表页的 `fetchData()` 加高度刷新**

在每个页面的 `<script setup>` 导入 `nextTick`，然后把 `fetchData()` 的 `finally` 改成下面结构；以 `frontend/src/views/model/index.vue` 为例：

```ts
import { ref, reactive, onMounted, nextTick } from 'vue'

async function fetchData() {
  loading.value = true
  try {
    const res = await getModelListApi({ name: searchForm.name, provider: searchForm.provider })
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
    await nextTick()
    tableScroll.updateTableScrollY()
  }
}
```

同样的 `await nextTick(); tableScroll.updateTableScrollY()` 要加到下面文件的 `fetchData()` 里：
- `frontend/src/views/skill/index.vue`
- `frontend/src/views/tool/index.vue`
- `frontend/src/views/setting/user/index.vue`
- `frontend/src/views/setting/role/index.vue`
- `frontend/src/views/setting/permission/index.vue`
- `frontend/src/views/setting/menu/index.vue`
- `frontend/src/views/setting/config/index.vue`
- `frontend/src/views/setting/operation-log/index.vue`
- `frontend/src/views/setting/login-log/index.vue`

- [ ] **Step 2: 把登录日志结果 Tag 改成蓝系主题**

修改 `frontend/src/views/setting/login-log/index.vue` 的表格单元格模板：

```vue
<template #bodyCell="{ column, record }">
  <template v-if="column.key === 'result'">
    <a-tag class="page-status-tag">{{ record.result }}</a-tag>
  </template>
  <template v-if="column.key === 'action'">
    <a-dropdown>
      <a-button type="link" size="small">
        操作
      </a-button>
      <template #overlay>
        <a-menu @click="(info: { key: string }) => handleActionMenuClick(info, record)">
          <a-menu-item v-if="canRead" key="detail"><EyeOutlined /> 查看详情</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </template>
</template>
```

- [ ] **Step 3: 把操作日志方法/结果 Tag 改成蓝系主题**

修改 `frontend/src/views/setting/operation-log/index.vue`：

```ts
const methodClassMap: Record<string, string> = {
  GET: 'page-method-tag',
  POST: 'page-method-tag',
  PUT: 'page-method-tag page-method-tag--soft',
  PATCH: 'page-method-tag page-method-tag--soft',
  DELETE: 'page-method-tag page-method-tag--soft',
}
```

```vue
<template #bodyCell="{ column, record }">
  <template v-if="column.key === 'method'">
    <a-tag :class="methodClassMap[record.method] || 'page-method-tag'">{{ record.method }}</a-tag>
  </template>
  <template v-if="column.key === 'result'">
    <a-tag class="page-status-tag">{{ record.result }}</a-tag>
  </template>
  <template v-if="column.key === 'action'">
    <a-dropdown>
      <a-button type="link" size="small">
        操作
      </a-button>
      <template #overlay>
        <a-menu @click="(info: { key: string }) => handleActionMenuClick(info, record)">
          <a-menu-item v-if="canRead" key="detail"><EyeOutlined /> 查看详情</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </template>
</template>
```

- [ ] **Step 4: 把用户页内置用户 Tag 改成统一蓝系**

修改 `frontend/src/views/setting/user/index.vue` 的单元格模板：

```vue
<template #bodyCell="{ column, record }">
  <template v-if="column.dataIndex === 'roles'">
    {{ record.roles.map((item: { name: string }) => item.name).join('、') }}
  </template>
  <template v-if="column.dataIndex === 'status'">
    <a-switch
      :checked="record.status === 'active'"
      checked-children="启用"
      un-checked-children="停用"
      :disabled="!canStatus"
      @change="handleStatusChange(record)"
    />
  </template>
  <template v-if="column.dataIndex === 'isBuiltin'">
    <a-tag :class="record.isBuiltin ? 'page-status-tag' : 'page-status-tag page-status-tag--muted'">
      {{ record.isBuiltin ? '是' : '否' }}
    </a-tag>
  </template>
  <template v-if="column.key === 'action'">
    <a-dropdown>
      <a-button type="link" size="small">
        操作
      </a-button>
      <template #overlay>
        <a-menu @click="(info: { key: string }) => handleActionMenuClick(info, record)">
          <a-menu-item v-if="canEdit" key="edit"><EditOutlined /> 编辑</a-menu-item>
          <a-menu-item v-if="canDelete && !record.isBuiltin" key="delete" danger><DeleteOutlined /> 删除</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </template>
</template>
```

- [ ] **Step 5: 构建并逐页验证列表页显示**

Run:

```bash
cd /Users/liang/code/max-agent/frontend && pnpm build
```

Expected: 构建成功。

随后在浏览器中逐页检查：
1. 模型管理、Skills 管理、工具管理页面能正常打开。
2. Tabs 在页面壳层外部顶部，不在内容卡片内部。
3. 页面标识行明显变轻，左侧装饰条宽度约为原来的一半。
4. 表格高度跟随窗口变化，既不会超出视口，也不会留下大块空白。
5. 登录日志与操作日志的 Tag 不再出现绿色/红色常规状态色。

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/model/index.vue frontend/src/views/skill/index.vue frontend/src/views/tool/index.vue frontend/src/views/setting/user/index.vue frontend/src/views/setting/role/index.vue frontend/src/views/setting/permission/index.vue frontend/src/views/setting/menu/index.vue frontend/src/views/setting/config/index.vue frontend/src/views/setting/operation-log/index.vue frontend/src/views/setting/login-log/index.vue
git commit -m "feat: align admin list pages with workbench layout"
```

---

### Task 5: 全链路验证与截图回归

**Files:**
- Modify: `frontend/src/layouts/BasicLayout.vue`
- Modify: `frontend/src/components/TabBar.vue`
- Modify: `frontend/src/composables/useTableScrollY.ts`
- Modify: `frontend/src/style.css`
- Modify: `frontend/src/views/model/index.vue`
- Modify: `frontend/src/views/skill/index.vue`
- Modify: `frontend/src/views/tool/index.vue`
- Modify: `frontend/src/views/setting/login-log/index.vue`
- Modify: `frontend/src/views/setting/operation-log/index.vue`
- Modify: `frontend/src/views/setting/user/index.vue`
- Modify: `backend/app/db/seed.py`
- Create: `backend/tests/test_seed_menu_permissions.py`

- [ ] **Step 1: 跑后端回归测试**

Run:

```bash
cd /Users/liang/code/max-agent/backend && uv run pytest tests/test_seed_menu_permissions.py -q
```

Expected: `1 passed`。

- [ ] **Step 2: 跑前端构建**

Run:

```bash
cd /Users/liang/code/max-agent/frontend && pnpm build
```

Expected: Vite 输出 `built in`，并且没有 TypeScript 报错。

- [ ] **Step 3: 浏览器走黄金路径**

Run:

```bash
cd /Users/liang/code/max-agent/frontend && pnpm dev
```

验证清单：
```text
1. 管理员登录后，左侧菜单能看到模型管理、Skills 管理、工具管理入口。
2. 点击模型管理、Skills 管理、工具管理后，页面内容正常渲染，不会跳回其他页面。
3. Tabs 位于整个内容区上方，不在白色工作区内部。
4. 轻页面标识区仍可辨识当前页面，但不再明显挤压表格空间。
5. 调整浏览器窗口高度后，表格主体仍然填满剩余空间。
6. 登录日志页面中的“成功”“失败”“退出”都使用蓝系 Tag。
7. 操作日志页面中的 method/result Tag 也为蓝系，不再有绿色/红色主导状态色。
8. 用户页“内置用户” Tag 也使用同一套主题样式。
```

- [ ] **Step 4: 保存对比截图**

截图以下页面用于回归记录：
```text
- 模型管理
- Skills 管理
- 工具管理
- 登录日志
- 操作日志
```

Expected: 每张截图都能清楚展示 Tabs 外提、轻页面标识和表格高度正常。

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/seed.py backend/tests/test_seed_menu_permissions.py frontend/src/layouts/BasicLayout.vue frontend/src/components/TabBar.vue frontend/src/composables/useTableScrollY.ts frontend/src/style.css frontend/src/views/model/index.vue frontend/src/views/skill/index.vue frontend/src/views/tool/index.vue frontend/src/views/setting/user/index.vue frontend/src/views/setting/role/index.vue frontend/src/views/setting/permission/index.vue frontend/src/views/setting/menu/index.vue frontend/src/views/setting/config/index.vue frontend/src/views/setting/operation-log/index.vue frontend/src/views/setting/login-log/index.vue
git commit -m "feat: tighten admin workbench layout and restore menu visibility"
```

---

## Self-Review

### Spec coverage
- Tabs 外提：Task 2 覆盖。
- 标题左侧矩形缩窄 50%：Task 2 覆盖。
- 动态表格高度重做：Task 3 + Task 4 覆盖。
- Tag 统一蓝系主题：Task 3 + Task 4 覆盖。
- 模型管理、Skills 管理、工具管理入口优先按权限配置修复：Task 1 + Task 5 覆盖。
- 不做管理员前端菜单特判：整份计划没有引入对应步骤，符合 spec。

### Placeholder scan
- 没有 `TODO`、`TBD`、`implement later`。
- 每个代码步骤都给了明确代码块。
- 每个验证步骤都有具体命令和预期结果。

### Type consistency
- 后端权限标识统一使用 `dashboard:view`、`model:view`、`skill:view`、`tool:view`。
- 前端统一使用 `tableScroll.updateTableScrollY()` 作为高度刷新入口。
- Tag 统一使用 `page-status-tag`、`page-status-tag--muted`、`page-method-tag`、`page-method-tag--soft` 这 4 个类名。
- 所有列表页的验证都基于现有 `useTableScrollY()` 返回结构，没有引入新的 composable 名称。

一致性通过。
