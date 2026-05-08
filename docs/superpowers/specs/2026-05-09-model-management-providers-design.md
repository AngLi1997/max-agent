# 模型管理设计

## 概述

模型管理模块，以模型为维度的管理模式。支持 OpenAI 兼容 API 和 Ollama 两种接入类型，可接入任意模型进行测试对话。

## 数据模型

### `llm_providers` — 接入点表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | 主键 |
| name | varchar(100) | 接入名称（如"我的OpenAI"） |
| type | varchar(20) | 类型：`openai` / `ollama` |
| api_url | varchar(500) | API 地址 |
| api_key | varchar(500), nullable | API 密钥，OpenAI 可选，Ollama 无需填写 |
| status | varchar(20) | `active` / `inactive`，默认 `active` |
| created_at | datetime | TimestampMixin |
| updated_at | datetime | TimestampMixin |

### `llm_models` — 模型表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | 主键 |
| provider_id | int FK | 关联 `llm_providers.id`，级联删除 |
| model_name | varchar(200) | 模型标识（如 gpt-4o、llama3.1） |
| status | varchar(20) | `active` / `inactive`，默认 `active` |
| created_at | datetime | TimestampMixin |
| updated_at | datetime | TimestampMixin |

## 页面交互

### 主表格（扁平模型表格）

以模型为维度，每行一个模型，同时显示其所属接入点信息。

**表格列定义：** 模型名称、接入类型、接入名称、API 地址、状态、创建时间（格式 `yyyy-MM-dd HH:mm:ss`）、操作

**操作列：** 测试 / 编辑 / 删除

**搜索栏：** 模型名称、接入类型（下拉选择）

### "新增模型" Drawer

点击"新增模型"按钮打开 Drawer，表单：

- **类型**（`a-select` 下拉框：OpenAI / Ollama）
- **接入名称**（`a-input`，placeholder "请输入接入名称"）
- **API 地址**（`a-input`，必填，placeholder "请输入 API 地址"）
- **API Key**（`a-input-password`，非必填）
- **获取模型列表**：点击后调用后端 `POST /providers/fetch-models` 返回远程模型列表（左侧无冒号标签）。同时支持手动输入模型名称（如果远程获取不到需要的模型，可以手输）。选择模型或手动输入模型名称后确认提交。

**后端处理：** 事务性创建 provider + 关联的 model 记录。

### "编辑" Drawer

点击模型行的"编辑"打开 Drawer，可修改：

- 模型状态（启用/停用）
- 接入名称
- API 地址
- API Key

### 测试对话

点击模型行的"测试"弹出 Modal 聊天框：

- 标题显示被测试的模型名称
- 使用 SSE 流式响应
- **对话记忆：** 发送消息时携带完整消息历史，后端透传给上游 API
- **自动滚动：** 消息区域在收到新 token 时自动滚动到底部
- **关闭中断：** 关闭弹窗时前端 `abortController.abort()` + 后端取消流式请求

## 后端 API 设计

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/api/providers` | 接入点列表（含关联模型） | require_permission |
| POST | `/api/providers` | 新建接入点 + 初始模型 | require_permission |
| GET | `/api/providers/{id}` | 接入点详情 | require_permission |
| PUT | `/api/providers/{id}` | 更新接入点 | require_permission |
| DELETE | `/api/providers/{id}` | 删除接入点及关联模型 | require_permission |
| POST | `/api/providers/fetch-models` | 拉取远程模型列表（不持久化） | require_permission |
| GET | `/api/models` | 获取扁平模型列表（含 provider 信息） | require_permission |
| POST | `/api/providers/models/{model_id}/chat` | 模型测试对话（SSE 流式） | require_permission |
| PUT | `/api/providers/models/{model_id}` | 更新单个模型 | require_permission |
| DELETE | `/api/providers/models/{model_id}` | 删除单个模型 | require_permission |

### `POST /api/providers/models/{model_id}/chat` 新增对话记忆

请求体增加 `messages` 字段替代 `message`：

```json
{
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
    {"role": "user", "content": "今天天气怎么样？"}
  ]
}
```

## 涉及的文件

### 前端修改

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/views/model/index.vue` | 重写为扁平模型表格、新增模型 Drawer、增强测试对话 |
| `frontend/src/api/model.ts` | 新增 `getModelListApi`、`updateModelApi` 接口 |

### 后端修改

| 文件 | 修改内容 |
|------|----------|
| `backend/app/api/routes/providers.py` | 新增 `GET /models`、`PUT /models/{id}` 路由；`POST /models/{id}/chat` 支持消息历史 |
| `backend/app/services/llm_providers.py` | 新增 `get_models`、`update_model`、修改 `chat_with_model_stream` 支持消息历史 |
| `backend/app/schemas/llm_provider.py` | 新增 `ModelListResult`、`ModelUpdateRequest`、修改 `ChatRequest` 支持消息列表 |
