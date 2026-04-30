---
title: 表格页面布局规范
type: concept
created: 2026-04-30
updated: 2026-04-30
sources: [style-css, useTableScrollY-composable]
tags: [frontend, convention, layout, table]
related: [[concepts/frontend-architecture]]
---

# 表格页面布局规范

## 背景

所有包含 Ant Design Table 的管理页面（用户、角色、权限、菜单、配置、日志、模型、技能、工具等）共享统一的表格布局模式，确保表格在任意视口高度下都不会溢出屏幕，分页栏固定在底部，表体区域自动滚动。

## HTML 结构

```html
<div class="page-container">
  <div class="page-section">
    <div class="page-toolbar">
      <!-- 搜索表单 + 操作按钮 -->
    </div>
  </div>
  <div :ref="tableScroll.tableSectionRef" class="page-section page-table-section">
    <a-table
      size="middle"
      :scroll="{ y: tableScroll.tableScrollY }"
      :pagination="{ total, pageSize: 10, showTotal: (t) => `共 ${t} 条` }"
      ...
    />
  </div>
</div>
```

## useTableScrollY 组合式函数

文件：`frontend/src/composables/useTableScrollY.ts`

```ts
import { useTableScrollY } from '@/composables/useTableScrollY'
const tableScroll = useTableScrollY()
```

提供三个返回值：
- `tableSectionRef` — 绑定到 `.page-table-section` 容器的 ref
- `tableScrollY` — 计算后的表体滚动高度（computed）
- `updateTableScrollY()` — 手动触发重新计算（数据加载后调用）

内部通过 ResizeObserver 监听容器尺寸变化，自动计算可用高度 = 容器高度 - padding - 表头高度 - 分页栏高度及 margin。

## CSS flex 链路

定义在 `frontend/src/style.css`，全局生效，页面中不需要重复声明。

完整链路（每一层都必须有 `flex: 1; min-height: 0; display: flex; flex-direction: column`）：

```
.page-table-section           overflow: hidden
  └── .ant-table-wrapper
       └── .ant-spin-nested-loading
            └── .ant-spin-container
                 ├── .ant-table
                 │    └── .ant-table-container   ← 关键：不可遗漏
                 │         ├── .ant-table-header  (自然高度)
                 │         └── .ant-table-body    flex: 1; overflow-y: auto
                 └── .ant-pagination              flex-shrink: 0
```

### 关键教训

Ant Design Vue 4.x 在 `.ant-table` 和 `.ant-table-header`/`.ant-table-body` 之间插入了 `.ant-table-container` 层。如果 flex 链路中遗漏此层，表体会按自然内容高度渲染，导致在小视口下溢出屏幕。

## 新增表格页面检查清单

1. 使用 `.page-container` > `.page-section` + `.page-table-section` 结构
2. 引入 `useTableScrollY` 并绑定 ref 和 scroll
3. 数据加载完成后调用 `updateTableScrollY()`
4. 不要在页面 scoped style 中覆盖 `.page-table-section` 相关的 flex 样式
5. 不要给 `.ant-table-body` 设置固定高度
