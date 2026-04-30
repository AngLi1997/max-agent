---
title: UI 全局规范
type: concept
created: 2026-04-30
updated: 2026-04-30
sources: [style-css, frontend-components]
tags: [frontend, ui, convention]
related: [[concepts/frontend-architecture]], [[concepts/table-layout-convention]]
---

# UI 全局规范

## Drawer / Modal 标题蓝色矩形装饰

所有 `a-drawer` 和 `a-modal` 的标题左侧自动显示蓝色矩形装饰条（4px × 18px，圆角，#1677ff），与页面标题 `.page-shell-accent` 风格一致。

通过全局 CSS `::before` 伪元素实现，无需在每个组件中手动添加。

```css
.ant-drawer-header .ant-drawer-title::before,
.ant-modal-header .ant-modal-title::before {
  content: '';
  width: 4px;
  height: 18px;
  border-radius: 999px;
  background: #1677ff;
}
```

## 表单按钮右对齐

Drawer / Modal 中表单的最后一个 `a-form-item`（按钮区域）统一右对齐，通过全局 CSS 实现：

```css
.ant-modal-body .ant-form > .ant-form-item:last-child .ant-form-item-control-input-content,
.ant-drawer-body .ant-form > .ant-form-item:last-child .ant-form-item-control-input-content {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
```

Drawer 的 `#footer` slot 中按钮也应使用 `text-align: right`（各页面已遵循）。

## 中文化要求

- 所有 placeholder 使用中文（如"请输入…"、"请选择…"）
- 表单确认/取消按钮使用中文（"确认"、"取消"）
- 提示信息、校验消息均使用中文
