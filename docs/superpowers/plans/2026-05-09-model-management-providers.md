# 模型管理重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将模型管理从 provider 维度重构为模型维度——扁平模型表格、支持新增模型（选择+手输模型名）、增强测试对话（消息历史、自动滚动、关闭中断）

**Architecture:** 后端新增 `GET /api/models` 扁平模型列表接口 + 模型更新接口；前端完全重写模型管理页面为扁平表格，使用 `a-select` 下拉框代替 `a-radio-group` 类型选择，测试对话增强 SSE 流式体验

**Tech Stack:** Python FastAPI + SQLAlchemy + Pydantic, Vue 3 + TypeScript + Ant Design Vue + SSE streaming

---

### Task 1: 后端—新增 GET /api/models 扁平模型列表接口

**Files:**
- Modify: `backend/app/schemas/llm_provider.py`
- Modify: `backend/app/services/llm_providers.py`
- Modify: `backend/app/api/routes/providers.py`

- [ ] **Step 1: 新增 ModelListItem Schema**

在 `backend/app/schemas/llm_provider.py` 中新增：

```python
class ModelListItem(BaseModel):
    id: int
    provider_id: int
    model_name: str
    provider_name: str
    provider_type: str
    provider_api_url: str
    status: str
    created_at: datetime
```

- [ ] **Step 2: 新增 get_models 服务**

在 `backend/app/services/llm_providers.py` 中新增：

```python
async def get_models(
    session: AsyncSession,
    name: str | None = None,
    type_: str | None = None,
) -> tuple[Sequence[dict], int]:
    """Get flat model list with provider info joined."""
    q = (
        select(LlmModel, LlmProvider.name, LlmProvider.type, LlmProvider.api_url)
        .join(LlmProvider, LlmModel.provider_id == LlmProvider.id)
        .order_by(LlmModel.created_at.desc())
    )
    if name:
        q = q.where(LlmModel.model_name.ilike(f"%{name}%"))
    if type_:
        q = q.where(LlmProvider.type == type_)

    rows = (await session.execute(q)).all()
    result = []
    for model, p_name, p_type, p_url in rows:
        result.append({
            "id": model.id,
            "provider_id": model.provider_id,
            "model_name": model.model_name,
            "provider_name": p_name,
            "provider_type": p_type,
            "provider_api_url": p_url,
            "status": model.status,
            "created_at": model.created_at,
        })
    return result, len(result)
```

- [ ] **Step 3: 新增 GET /api/models 路由**

在 `backend/app/api/routes/providers.py` 中 新增路由（放在文件末尾，`router` 定义上方之前）：

```python
@router.get("/models", response_model=ListResponse[ModelListItem])
async def list_models(
    name: str | None = None,
    type: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("model:view")),
) -> ListResponse[ModelListItem]:
    rows, total = await get_models(session, name=name, type_=type)
    return ListResponse(list=[ModelListItem(**r) for r in rows], total=total)
```

注意：此路由必须在 `/{provider_id}` 路由之前，或者 `{provider_id}` 路由要限制类型以避免路径冲突。由于 `GET /models` 在前缀 `/providers` 下，实际路径是 `/api/providers/models`，而 `GET /{provider_id}` 是 `/api/providers/{provider_id}`，两者不会冲突因为 `models` 不是数字。

- [ ] **Step 4: 新增 ModelUpdateRequest Schema**

在 `backend/app/schemas/llm_provider.py` 中新增：

```python
class ModelUpdateRequest(BaseModel):
    status: str | None = None
```

- [ ] **Step 5: 新增 update_model 服务**

在 `backend/app/services/llm_providers.py` 中新增：

```python
async def update_model(
    session: AsyncSession,
    model: LlmModel,
    status: str | None,
) -> LlmModel:
    if status is not None:
        model.status = status
    session.add(model)
    await session.flush()
    return model
```

- [ ] **Step 6: 新增 PUT /api/providers/models/{model_id} 路由**

在 `backend/app/api/routes/providers.py` 中新增：

```python
@router.put("/models/{model_id}")
async def update_model_endpoint(
    model_id: int,
    payload: ModelUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("model:update")),
) -> dict[str, str]:
    model = await session.get(LlmModel, model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")
    await update_model(session, model, status=payload.status)
    await session.commit()
    return {"message": "更新成功"}
```

- [ ] **Step 7: 修改 ChatRequest 支持消息历史**

将 `backend/app/schemas/llm_provider.py` 中的 `ChatRequest` 修改为：

```python
class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
```

保留或删除旧的 `message: str` 字段（建议删除）。

- [ ] **Step 8: 修改 chat_with_model_stream 支持消息历史**

修改 `backend/app/services/llm_providers.py` 中的 `chat_with_model_stream` 函数，接受 `messages: list[dict]` 参数代替 `user_message: str`，并直接透传给上游 API：

```python
async def chat_with_model_stream(
    provider: LlmProvider,
    model_name: str,
    messages: list[dict],
):
```

移除 `_build_openai_messages` 和 `_build_ollama_messages` 函数，改用传入的 `messages`。

修改路由 `POST /api/providers/models/{model_id}/chat` 来适配新参数：

```python
@router.post("/models/{model_id}/chat")
async def chat_with_model(
    model_id: int,
    payload: ChatRequest,
    ...
) -> StreamingResponse:
    ...
    return StreamingResponse(
        chat_with_model_stream(model.provider, model.model_name, [m.model_dump() for m in payload.messages]),
        ...
    )
```

- [ ] **Step 9: 后端导入更新**

确保 `backend/app/schemas/__init__.py` 或路由文件正确导入了新增的 schema。

- [ ] **Step 10: 验证后端编译通过**

```bash
cd /Users/liang/code/max-agent/backend && uv run python -c "from app.api.routes.providers import router; print('OK')"
```

### Task 2: 前端—更新 API 层

**Files:**
- Modify: `frontend/src/api/model.ts`

- [ ] **Step 1: 新增类型定义和 API 函数**

```typescript
// 扁平模型列表项
export interface ModelListItem {
  id: number
  provider_id: number
  model_name: string
  provider_name: string
  provider_type: string
  provider_api_url: string
  status: string
  created_at: string
}

// 模型列表响应
export interface ModelListResult {
  list: ModelListItem[]
  total: number
}

// 模型更新参数
export interface ModelUpdateParams {
  status?: string
}

// 聊天消息
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// 聊天请求参数
export interface ChatRequestParams {
  messages: ChatMessage[]
}
```

- [ ] **Step 2: 新增 API 函数**

```typescript
export function getModelListApi(params?: { name?: string; type?: string }): Promise<ModelListResult> {
  return request.get('/providers/models', { params })
}

export function updateModelApi(id: number, data: ModelUpdateParams): Promise<void> {
  return request.put(`/providers/models/${id}`, data)
}
```

- [ ] **Step 3: 修改 getChatStreamUrl 为 POST 请求函数**

由于我们需要发送 `messages` 数组而不是简单的 URL，改为完整的 POST 请求函数：

```typescript
export function chatWithModelApi(modelId: number, data: ChatRequestParams, signal?: AbortSignal): Promise<Response> {
  const token = getToken()  // 需要一个获取 token 的方式
  return fetch(`/api/providers/models/${modelId}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
    signal,
  })
}

// 仍然保留 getChatStreamUrl 用于 URL 获取，但主要使用 chatWithModelApi
export function getChatStreamUrl(modelId: number): string {
  return `/api/providers/models/${modelId}/chat`
}
```

注意需要引入 token 获取方式，当前代码中使用 `useUserStore()` 获取 token：

```typescript
// 从文件中 import
import { useUserStore } from '@/stores/user'
```

### Task 3: 前端—重写模型管理页面（主表格和搜索栏）

**Files:**
- Rewrite: `frontend/src/views/model/index.vue`

- [ ] **Step 1: 修改模板—表格和搜索栏**

将模板改为扁平模型表格：

```html
<template>
  <div class="page-container">
    <!-- Search toolbar -->
    <div class="page-section">
      <div class="page-toolbar">
        <a-form layout="inline" :model="searchForm">
          <a-form-item label="模型名称">
            <a-input v-model:value="searchForm.name" placeholder="请输入模型名称" allow-clear style="width: 200px" />
          </a-form-item>
          <a-form-item label="接入类型">
            <a-select v-model:value="searchForm.type" placeholder="请选择类型" allow-clear style="width: 160px">
              <a-select-option value="openai">OpenAI</a-select-option>
              <a-select-option value="ollama">Ollama</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="fetchData">查询</a-button>
            <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
          </a-form-item>
        </a-form>
        <div class="page-toolbar-actions">
          <a-button type="primary" @click="handleAdd">
            <template #icon><PlusOutlined /></template>
            新增模型
          </a-button>
        </div>
      </div>
    </div>

    <!-- Model table -->
    <div :ref="tableScroll.tableSectionRef" class="page-section page-table-section">
      <a-table
        size="middle"
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="{ total, pageSize: 10, showTotal: (t: number) => `共 ${t} 条` }"
        row-key="id"
        :scroll="{ y: tableScroll.tableScrollY }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'provider_type'">
            <a-select
              :value="record.provider_type"
              size="small"
              style="width: 100px"
              disabled
            >
              <a-select-option value="openai">OpenAI</a-select-option>
              <a-select-option value="ollama">Ollama</a-select-option>
            </a-select>
          </template>
          <template v-if="column.dataIndex === 'status'">
            <a-switch
              :checked="record.status === 'active'"
              size="small"
              :loading="statusLoadingMap[record.id]"
              @change="(checked: boolean) => handleToggleStatus(record, checked)"
              checked-children="启用"
              un-checked-children="停用"
            />
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleTest(record)">测试</a-button>
              <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
              <a-button type="link" danger size="small" @click="handleDelete(record)">删除</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>
    ...
  </div>
</template>
```

- [ ] **Step 2: 更新 script setup—数据定义和表格列**

```typescript
const columns = [
  { title: '模型名称', dataIndex: 'model_name', key: 'model_name', width: 200, ellipsis: { showTitle: true } },
  { title: '接入类型', dataIndex: 'provider_type', key: 'provider_type', width: 120 },
  { title: '接入名称', dataIndex: 'provider_name', key: 'provider_name', width: 150, ellipsis: { showTitle: true } },
  { title: 'API 地址', dataIndex: 'provider_api_url', key: 'provider_api_url', width: 250, ellipsis: { showTitle: true } },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 200, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<ModelListItem[]>([])
const total = ref(0)
const statusLoadingMap = reactive<Record<number, boolean>>({})

// search form
const searchForm = reactive({ name: '', type: undefined as string | undefined })

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.type) params.type = searchForm.type
    const res = await getModelListApi(Object.keys(params).length > 0 ? params : undefined)
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
    await nextTick()
    tableScroll.updateTableScrollY()
  }
}
```

- [ ] **Step 3: 实现状态切换**

```typescript
async function handleToggleStatus(record: ModelListItem, checked: boolean) {
  statusLoadingMap[record.id] = true
  try {
    await updateModelApi(record.id, { status: checked ? 'active' : 'inactive' })
    record.status = checked ? 'active' : 'inactive'
    message.success('状态更新成功')
  } catch {
    message.error('状态更新失败')
  } finally {
    statusLoadingMap[record.id] = false
  }
}
```

### Task 4: 前端—重写新增/编辑 Drawer 和测试对话框

**Files:**
- Modify: `frontend/src/views/model/index.vue`

- [ ] **Step 1: 新增模型 Drawer（下拉类型 + 选择+手输模型名）**

```html
<!-- Add model drawer -->
<a-drawer
  title="新增模型"
  :open="drawerVisible"
  :width="drawerWidth"
  @close="drawerVisible = false"
>
  <a-form :model="addForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
    <a-form-item label="类型" required>
      <a-select v-model:value="addForm.type" placeholder="请选择类型" style="width: 100%">
        <a-select-option value="openai">OpenAI</a-select-option>
        <a-select-option value="ollama">Ollama</a-select-option>
      </a-select>
    </a-form-item>
    <a-form-item label="接入名称" required>
      <a-input v-model:value="addForm.name" placeholder="请输入接入名称" />
    </a-form-item>
    <a-form-item label="API 地址" required>
      <a-input
        v-model:value="addForm.api_url"
        placeholder="请输入 API 地址"
        :addonAfter="addForm.type === 'openai' ? '/v1' : ''"
      />
    </a-form-item>
    <a-form-item label="API Key">
      <a-input-password v-model:value="addForm.api_key" placeholder="请输入 API Key（可选）" />
    </a-form-item>
    <a-form-item label=" ">
      <a-button :loading="fetchLoading" @click="handleFetchModels">
        获取模型列表
      </a-button>
    </a-form-item>
    <template v-if="availableModels.length > 0">
      <a-form-item label="模型列表">
        <a-select
          v-model:value="selectedModel"
          placeholder="请选择模型"
          style="width: 100%"
        >
          <a-select-option v-for="m in availableModels" :key="m" :value="m">{{ m }}</a-select-option>
        </a-select>
      </a-form-item>
    </template>
    <a-form-item label="模型名称" required>
      <a-input v-model:value="addForm.modelName" placeholder="可选择模型后自动填入，或手动输入" />
    </a-form-item>
  </a-form>
  <template #footer>
    <div style="text-align: right">
      <a-button style="margin-right: 8px" @click="drawerVisible = false">取消</a-button>
      <a-button type="primary" :loading="submitLoading" @click="handleSubmitAdd">确定</a-button>
    </div>
  </template>
</a-drawer>
```

这一步的关键设计：
- "模型列表"这个 form-item 没有 required 标记和冒号（label 留空或使用 `label="模型列表"` 正常显示）
- 选择模型后自动填充 addForm.modelName
- "模型名称"输入框既是选择结果的展示，也支持手动输入

- [ ] **Step 2: 新增模型相关数据和逻辑**

```typescript
const drawerVisible = ref(false)
const submitLoading = ref(false)

const addForm = reactive({
  type: 'openai',
  name: '',
  api_url: '',
  api_key: '',
  modelName: '',
})
const fetchLoading = ref(false)
const availableModels = ref<string[]>([])
const selectedModel = ref<string>('')

function handleAdd() {
  addForm.type = 'openai'
  addForm.name = ''
  addForm.api_url = ''
  addForm.api_key = ''
  addForm.modelName = ''
  availableModels.value = []
  selectedModel.value = ''
  drawerVisible.value = true
}

async function handleFetchModels() {
  if (!addForm.api_url) {
    message.warning('请先填写 API 地址')
    return
  }
  fetchLoading.value = true
  availableModels.value = []
  selectedModel.value = ''
  try {
    const res = await fetchRemoteModelsApi({
      type: addForm.type,
      api_url: addForm.api_url,
      api_key: addForm.api_key || undefined,
    })
    availableModels.value = res.models
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '获取模型列表失败')
  } finally {
    fetchLoading.value = false
  }
}

// 选择模型时自动填入模型名称
watch(selectedModel, (val) => {
  if (val) {
    addForm.modelName = val
  }
})
```

- [ ] **Step 3: 提交新增模型**

```typescript
async function handleSubmitAdd() {
  if (!addForm.name || !addForm.api_url || !addForm.modelName) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    await createProviderApi({
      name: addForm.name,
      type: addForm.type,
      api_url: addForm.api_url,
      api_key: addForm.api_key || undefined,
      models: [addForm.modelName],
    })
    message.success('创建成功')
    drawerVisible.value = false
    fetchData()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '创建失败')
  } finally {
    submitLoading.value = false
  }
}
```

- [ ] **Step 4: 编辑 Drawer（包含模型名称和状态）**

```html
<a-drawer
  title="编辑模型"
  :open="editDrawerVisible"
  :width="drawerWidth"
  @close="editDrawerVisible = false"
>
  <a-form :model="editForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
    <a-form-item label="模型名称">
      <a-input v-model:value="editForm.model_name" placeholder="模型名称" disabled />
    </a-form-item>
    <a-form-item label="接入名称" required>
      <a-input v-model:value="editForm.name" placeholder="请输入接入名称" />
    </a-form-item>
    <a-form-item label="API 地址" required>
      <a-input v-model:value="editForm.api_url" placeholder="请输入 API 地址" />
    </a-form-item>
    <a-form-item label="API Key">
      <a-input-password v-model:value="editForm.api_key" placeholder="请输入 API Key（可选）" />
    </a-form-item>
    <a-form-item label="状态">
      <a-switch
        v-model:checked="editForm.status"
        checked-value="active"
        un-checked-value="inactive"
        checked-children="启用"
        un-checked-children="停用"
      />
    </a-form-item>
  </a-form>
  <template #footer>
    <div style="text-align: right">
      <a-button style="margin-right: 8px" @click="editDrawerVisible = false">取消</a-button>
      <a-button type="primary" :loading="submitLoading" @click="handleSubmitEdit">确定</a-button>
    </div>
  </template>
</a-drawer>
```

编辑表单也需要更新 provider 信息（因为编辑模型时可能修改接入配置）：

```typescript
const editDrawerVisible = ref(false)
const editingId = ref<number | null>(null)
const editForm = reactive({
  model_name: '',
  name: '',
  api_url: '',
  api_key: '',
  status: 'active',
})

function handleEdit(record: ModelListItem) {
  editingId.value = record.id
  editForm.model_name = record.model_name
  editForm.name = record.provider_name
  editForm.api_url = record.provider_api_url
  editForm.api_key = ''
  editForm.status = record.status
  editDrawerVisible.value = true
}
```

- [ ] **Step 5: 提交编辑**

```typescript
async function handleSubmitEdit() {
  if (!editForm.name || !editForm.api_url) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    await updateProviderApi(editingId.value!, {
      name: editForm.name,
      api_url: editForm.api_url,
      api_key: editForm.api_key || undefined,
      status: editForm.status,
    })
    message.success('更新成功')
    editDrawerVisible.value = false
    fetchData()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '更新失败')
  } finally {
    submitLoading.value = false
  }
}
```

注意：编辑时需要先通过 provider_id 找到对应的 provider 来更新。由于 ModelListItem 不直接包含 provider_id... 实际上它直接包含了 provider_id。需要新增加一个通过 provider_id 更新 Provider 的机制，或者简化编辑流程。

更简单的方法：前端先调用 `getProviderApi(record.provider_id)` 获取完整 Provider 信息再编辑。

或者，更直接的方案：在 ModelListItem 中包含 `provider_id`（已在 schema 中定义），编辑时直接使用 `getProviderApi(provider_id)` 获取 provider 数据进行编辑。

但更简单的方案是：编辑 Drawer 直接调用 `updateProviderApi`，因为它保存的是 provider 层级的数据。这里还需要加一步：获取 provider_id。

让我重新设计——编辑模型时，使用 provider_id 更新 provider 信息，同时如果有状态变化也更新模型状态。

实际上用现在的 API：
1. 获取 model 的 provider_id
2. 调用 getProviderApi(provider_id) 获取完整 provider
3. 编辑时更新 provider

或者干脆：在 ModelListItem 中也保留 provider_id，编辑时直接获取 provider，然后更新 provider info + model status。

在前端简化：编辑时先获取 provider 详情。

还可以更简单：修改实际后端代码，让 `PUT /api/providers/models/{model_id}` 也能更新 provider 的这些字段（需要修改 backend 逻辑）。

不过这样会复杂化。最简单的方案：

**编辑 Drawer 只修改已存在的 provider 信息 + 模型状态**，因为模型名称和 provider 是直接关联的。

具体：
1. 前端 `handleEdit` 时从 `record` 拿到 `provider_id`
2. 调用 `getProviderApi(provider_id)` 获取完整 provider 数据（含 api_key 等）
3. 编辑表单预填充
4. 提交时：先 `updateProviderApi(provider_id, { name, api_url, api_key })`，再 `updateModelApi(model_id, { status })`
5. 或者如果 provider 信息不变，只更新模型状态

但是为了简化实现，最初的 plan 中编辑 Drawer 只允许修改模型状态。
实际上用户需求是 "编辑接入信息 + 模型状态"。

最简单的方案：后端 PUT /api/providers/models/{model_id} 增加可选的 name/api_url/api_key 字段，更新时级联更新 provider。

嗯，这又是一个设计决策。还是让实现更简单：直接用 provider_id 调用现有 updateProviderApi。

好的，让我重新组织 plan 中的编辑部分：

```typescript
function handleEdit(record: ModelListItem) {
  editingId.value = record.id
  editingProviderId.value = record.provider_id
  editForm.model_name = record.model_name
  editForm.status = record.status
  // Load provider details
  loadProviderDetail(record.provider_id)
}

async function loadProviderDetail(providerId: number) {
  try {
    const provider = await getProviderApi(providerId)
    editForm.name = provider.name
    editForm.api_url = provider.api_url
    editForm.api_key = provider.api_key || ''
  } catch {
    message.error('获取接入点信息失败')
  }
}
```

And for submit, call both `updateProviderApi` and `updateModelApi`. Actually, this is getting too complex for the plan. Let me simplify:

The edit drawer locks the model_name, and allows editing provider name, api_url, api_key, model status. On submit:
1. Call `updateProviderApi(provider_id, { name, api_url, api_key })`
2. Call `updateModelApi(model_id, { status })`

That's clean.

- [ ] **Step 6: 删除模型**

```typescript
function handleDelete(record: ModelListItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除模型「${record.model_name}」吗？`,
    okType: 'danger',
    okText: '删除',
    cancelText: '取消',
    async onOk() {
      await deleteModelApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}
```

- [ ] **Step 7: 测试对话增强（自动滚动 + 消息历史）**

```typescript
// 在 chat-messages div 上添加 ref
const chatMessagesRef = ref<HTMLElement | null>(null)
// 使用 nextTick 在每次消息更新后滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

async function sendChatMessage() {
  if (!chatInput.value.trim() || !testModel.value) return
  const userMsg = chatInput.value.trim()
  messages.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  chatLoading.value = true
  scrollToBottom()

  const assistantMsg = { role: 'assistant' as const, content: '' }
  messages.value.push(assistantMsg)
  abortController.value = new AbortController()
  scrollToBottom()

  try {
    const userStore = useUserStore()
    const response = await fetch(getChatStreamUrl(testModel.value.id), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`,
      },
      body: JSON.stringify({
        messages: messages.value.map(m => ({ role: m.role, content: m.content }))
      }),
      signal: abortController.value.signal,
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const chunk = JSON.parse(line.slice(6))
          assistantMsg.content += chunk.content || ''
          messages.value = [...messages.value]  // 触发响应式更新
          scrollToBottom()
          if (chunk.done) break
        } catch { /* skip */ }
      }
    }
  } catch (err: any) {
    if (err.name !== 'AbortError') {
      assistantMsg.content += '\n[连接错误]'
      messages.value = [...messages.value]
      scrollToBottom()
    }
  } finally {
    chatLoading.value = false
    abortController.value = null
    // 确保最后一次滚动
    scrollToBottom()
  }
}

function closeChat() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
  chatVisible.value = false
  chatLoading.value = false
}
```

- [ ] **Step 8: 时间格式化**

在 `frontend/src/views/model/index.vue` 中添加时间格式化函数：

```typescript
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}
```

在表格列定义中把 `created_at` 的 `dataIndex` 改为使用 customRender 或直接在 template 中格式化。

最佳方案：移除 `created_at` 列的 `dataIndex`，用模板渲染：

```html
<template #bodyCell="{ column, record }">
  ...
  <template v-if="column.dataIndex === 'created_at'">
    {{ formatDate(record.created_at) }}
  </template>
  ...
</template>
```

- [ ] **Step 9: 导入更新**

```typescript
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import {
  getModelListApi,
  createProviderApi,
  updateProviderApi,
  getProviderApi,
  fetchRemoteModelsApi,
  deleteModelApi,
  updateModelApi,
  getChatStreamUrl,
  type ModelListItem,
} from '@/api/model'
```

### Task 5: 更新文档

**Files:**
- Modify: `docs/superpowers/plans/2026-05-09-model-management-providers.md`

- [ ] **Step 1: 更新计划文档**

当前 plan 已重写为新设计。

- [ ] **Step 2: 验证构建**

```bash
cd /Users/liang/code/max-agent/frontend && npx vue-tsc --noEmit && npx vite build
```

预期：通过，无类型错误。
