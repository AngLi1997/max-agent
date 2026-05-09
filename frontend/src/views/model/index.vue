<template>
  <div class="page-container">
    <!-- Search toolbar -->
    <div class="page-section">
      <div class="page-toolbar">
        <a-form layout="inline" :model="searchForm">
          <a-form-item label="模型名称">
            <a-input v-model:value="searchForm.name" placeholder="请输入模型名称" allow-clear style="width: 200px" />
          </a-form-item>
          <a-form-item label="类型">
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

    <!-- Flat model table -->
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
            <a-tag :color="record.provider_type === 'openai' ? 'blue' : 'green'">
              {{ record.provider_type === 'openai' ? 'OpenAI' : 'Ollama' }}
            </a-tag>
          </template>
          <template v-if="column.dataIndex === 'status'">
            <a-switch
              :checked="record.status === 'active'"
              @change="(checked: boolean) => handleToggleStatus(record, checked)"
              checked-children="启用"
              un-checked-children="停用"
            />
          </template>
          <template v-if="column.dataIndex === 'created_at'">
            {{ formatDate(record.created_at) }}
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

    <!-- Add model drawer -->
    <a-drawer
      title="新增模型"
      :open="drawerVisible"
      :width="drawerWidth"
      @close="drawerVisible = false"
    >
      <a-form :model="addForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="类型" required>
          <a-select v-model:value="addForm.type" placeholder="请选择类型">
            <a-select-option value="openai">OpenAI</a-select-option>
            <a-select-option value="ollama">Ollama</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="API 地址" required>
          <div style="display: flex; gap: 8px;">
            <a-input
              v-model:value="addForm.api_url"
              placeholder="请输入 API 地址"
              :addonAfter="addForm.type === 'openai' ? '/v1' : ''"
              style="flex: 1"
            />
            <a-button :loading="fetchLoading" @click="handleFetchModels">获取模型列表</a-button>
          </div>
        </a-form-item>
        <a-form-item label="API Key">
          <a-input-password v-model:value="addForm.api_key" placeholder="请输入 API Key（可选）" />
        </a-form-item>
        <a-form-item label="模型名称" required>
          <a-auto-complete
            v-model:value="addForm.modelName"
            placeholder="可选择或输入模型名称"
            style="width: 100%"
            :options="availableModels.map(m => ({ value: m }))"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="备注">
          <a-input v-model:value="addForm.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
      <template #footer>
        <div style="text-align: right">
          <a-button style="margin-right: 8px" @click="drawerVisible = false">取消</a-button>
          <a-button type="primary" :loading="submitLoading" @click="handleSubmitAdd">确定</a-button>
        </div>
      </template>
    </a-drawer>

    <!-- Edit model drawer -->
    <a-drawer
      title="编辑模型"
      :open="editDrawerVisible"
      :width="drawerWidth"
      @close="editDrawerVisible = false"
    >
      <a-form :model="editForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="模型名称">
          <a-input v-model:value="editForm.modelName" disabled />
        </a-form-item>
        <a-form-item label="API 地址" required>
          <a-input v-model:value="editForm.api_url" placeholder="请输入 API 地址" />
        </a-form-item>
        <a-form-item label="API Key">
          <a-input-password v-model:value="editForm.api_key" placeholder="请输入 API Key（可选）" />
        </a-form-item>
        <a-form-item label="备注">
          <a-input v-model:value="editForm.remark" placeholder="请输入备注" />
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

    <!-- Test chat modal -->
    <a-modal
      :title="testModel ? `测试 - ${testModel.model_name}` : ''"
      :open="chatVisible"
      :footer="null"
      width="600px"
      @cancel="closeChat"
      :destroy-on-close="true"
    >
      <div ref="chatMessagesRef" class="chat-messages">
        <div v-for="(msg, i) in messages" :key="i" :class="['chat-message', msg.role]">
          <template v-if="msg.role === 'assistant'">
            <div v-for="(part, j) in renderMessageParts(msg.content)" :key="j">
              <div v-if="part.type === 'think'" class="think-block">
                <details>
                  <summary class="think-summary">💭 思考过程</summary>
                  <div class="think-content" v-html="part.html" />
                </details>
              </div>
              <div v-else v-html="part.html" />
            </div>
          </template>
          <template v-else>
            {{ msg.content }}
          </template>
        </div>
      </div>
      <div class="chat-input-area">
        <a-textarea
          v-model:value="chatInput"
          placeholder="请输入消息..."
          :rows="2"
          :disabled="chatLoading"
          @keydown.enter.prevent="sendChatMessage"
        />
        <a-button type="primary" :loading="chatLoading" @click="sendChatMessage">发送</a-button>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'Model' })

import { ref, reactive, onMounted, nextTick } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { marked } from 'marked'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import { useTableScrollY } from '@/composables/useTableScrollY'
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
import { useUserStore } from '@/stores/user'

const { drawerWidth } = useDrawerWidth()
const tableScroll = useTableScrollY()

const columns = [
  { title: '模型名称', dataIndex: 'model_name', key: 'model_name', width: 180, ellipsis: { showTitle: true } },
  { title: '类型', dataIndex: 'provider_type', key: 'provider_type', width: 100 },
  { title: '备注', dataIndex: 'remark', key: 'remark', width: 150, ellipsis: { showTitle: true } },
  { title: 'API 地址', dataIndex: 'provider_api_url', key: 'provider_api_url', width: 250, ellipsis: { showTitle: true } },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 200, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<ModelListItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const editDrawerVisible = ref(false)
const submitLoading = ref(false)

// search form
const searchForm = reactive({ name: '', type: undefined as string | undefined })

// add model form
const addForm = reactive({
  type: 'openai',
  api_url: '',
  api_key: '',
  modelName: '',
  remark: '',
})
const fetchLoading = ref(false)
const availableModels = ref<string[]>([])

// edit model form
const editForm = reactive({
  providerId: 0,
  modelId: 0,
  modelName: '',
  api_url: '',
  api_key: '',
  status: 'active',
  remark: '',
})

// test model state
const testModel = ref<{ id: number; model_name: string } | null>(null)
const chatVisible = ref(false)
const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([])
const chatInput = ref('')
const chatLoading = ref(false)
const abortController = ref<AbortController | null>(null)
const chatMessagesRef = ref<HTMLElement | null>(null)

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr.slice(0, 19).replace('T', ' ')
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  const s = String(d.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}:${s}`
}

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

function handleReset() {
  searchForm.name = ''
  searchForm.type = undefined
  fetchData()
}

async function handleToggleStatus(record: ModelListItem, checked: boolean) {
  try {
    await updateModelApi(record.id, { status: checked ? 'active' : 'inactive' })
    message.success('状态更新成功')
    fetchData()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '状态更新失败')
  }
}

function handleAdd() {
  addForm.type = 'openai'
  addForm.api_url = ''
  addForm.api_key = ''
  addForm.modelName = ''
  addForm.remark = ''
  availableModels.value = []
  drawerVisible.value = true
}

async function handleEdit(record: ModelListItem) {
  editForm.modelId = record.id
  editForm.providerId = record.provider_id
  editForm.modelName = record.model_name
  editForm.status = record.status
  editForm.remark = record.remark || ''
  try {
    const provider = await getProviderApi(record.provider_id)
    editForm.api_url = provider.api_url
    editForm.api_key = provider.api_key || ''
  } catch (e: any) {
    message.error('获取接入信息失败')
    return
  }
  editDrawerVisible.value = true
}

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

async function handleFetchModels() {
  if (!addForm.api_url) {
    message.warning('请先填写 API 地址')
    return
  }
  fetchLoading.value = true
  availableModels.value = []
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

async function handleSubmitAdd() {
  if (!addForm.api_url || !addForm.modelName) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    await createProviderApi({
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

async function handleSubmitEdit() {
  if (!editForm.api_url) {
    message.warning('请填写 API 地址')
    return
  }
  submitLoading.value = true
  try {
    await updateProviderApi(editForm.providerId, {
      api_url: editForm.api_url,
      api_key: editForm.api_key || undefined,
    })
    await updateModelApi(editForm.modelId, { status: editForm.status, remark: editForm.remark || undefined })
    message.success('更新成功')
    editDrawerVisible.value = false
    fetchData()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '更新失败')
  } finally {
    submitLoading.value = false
  }
}

function handleTest(model: ModelListItem) {
  testModel.value = { id: model.id, model_name: model.model_name }
  messages.value = []
  chatInput.value = ''
  chatVisible.value = true
}

function closeChat() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
  chatVisible.value = false
  chatLoading.value = false
}

function renderMessageParts(content: string): { type: 'think' | 'text'; html: string }[] {
  if (!content) return []
  const parts: { type: 'think' | 'text'; html: string }[] = []
  const openTag = '<think>'
  const closeTag = '</think>'

  // Handle unclosed <think> during streaming: if there's an open tag without close,
  // treat everything from open tag onward as think content
  let processed = content
  const lastOpen = processed.lastIndexOf(openTag)
  const lastClose = processed.lastIndexOf(closeTag)
  if (lastOpen > lastClose) {
    // Unclosed <think> tag - close it for parsing
    processed = processed.slice(0, lastOpen) + openTag + processed.slice(lastOpen + openTag.length) + closeTag
  }

  const regex = /<think>([\s\S]*?)<\/think>/g
  let lastIndex = 0
  let match: RegExpExecArray | null
  while ((match = regex.exec(processed)) !== null) {
    if (match.index > lastIndex) {
      const text = processed.slice(lastIndex, match.index)
      parts.push({ type: 'text', html: marked.parse(text, { async: false }) as string })
    }
    parts.push({ type: 'think', html: marked.parse(match[1], { async: false }) as string })
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < processed.length) {
    const text = processed.slice(lastIndex)
    parts.push({ type: 'text', html: marked.parse(text, { async: false }) as string })
  }
  if (parts.length === 0) {
    parts.push({ type: 'text', html: marked.parse(content, { async: false }) as string })
  }
  return parts
}

function scrollChatToBottom() {
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

  const assistantMsg = { role: 'assistant' as const, content: '' }
  messages.value.push(assistantMsg)
  abortController.value = new AbortController()

  try {
    const userStore = useUserStore()
    // Send full message history for conversation context
    const chatMessages = messages.value
      .filter((m) => m.content)
      .map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content }))

    const response = await fetch(getChatStreamUrl(testModel.value.id), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userStore.token}`,
      },
      body: JSON.stringify({ messages: chatMessages }),
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
          // Force reactivity
          messages.value = [...messages.value]
          scrollChatToBottom()
          if (chunk.done) break
        } catch {
          // skip malformed chunk
        }
      }
    }
  } catch (err: any) {
    if (err.name !== 'AbortError') {
      assistantMsg.content += '\n[连接错误]'
      messages.value = [...messages.value]
    }
  } finally {
    chatLoading.value = false
    abortController.value = null
  }
}

onMounted(fetchData)
</script>

<style scoped>
.chat-messages {
  height: 400px;
  overflow-y: auto;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 12px;
}
.chat-message {
  margin-bottom: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  max-width: 80%;
  white-space: pre-wrap;
  word-break: break-word;
}
.chat-message.user {
  background: #1677ff;
  color: #fff;
  margin-left: auto;
}
.chat-message.assistant {
  background: #fff;
  color: #333;
  border: 1px solid #e8e8e8;
}
.chat-input-area {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}
.chat-input-area .ant-btn {
  flex-shrink: 0;
}
.think-block {
  margin: 8px 0;
  border-left: 3px solid #d9d9d9;
  padding-left: 8px;
}
.think-summary {
  color: #999;
  font-size: 12px;
  cursor: pointer;
  user-select: none;
}
.think-content {
  margin-top: 4px;
  font-size: 13px;
  color: #888;
  line-height: 1.6;
}
.think-content p {
  margin-bottom: 4px;
}
</style>
