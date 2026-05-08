<template>
  <div class="page-container">
    <!-- Search toolbar -->
    <div class="page-section">
      <div class="page-toolbar">
        <a-form layout="inline" :model="searchForm">
          <a-form-item label="接入名称">
            <a-input v-model:value="searchForm.name" placeholder="请输入接入名称" allow-clear style="width: 200px" />
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
            新增接入
          </a-button>
        </div>
      </div>
    </div>

    <!-- Provider table -->
    <div :ref="tableScroll.tableSectionRef" class="page-section page-table-section">
      <a-table
        size="middle"
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="{ total, pageSize: 10, showTotal: (t: number) => `共 ${t} 条` }"
        row-key="id"
        :scroll="{ y: tableScroll.tableScrollY }"
        :expandable="{
          expandedRowKeys,
          onExpand: handleExpand,
        }"
      >
        <template #expandedRowRender="{ record }">
          <div class="model-sub-table">
            <a-table
              :data-source="record.models"
              :columns="modelColumns"
              :pagination="false"
              row-key="id"
              size="small"
            >
              <template #bodyCell="{ column, record: modelRecord }">
                <template v-if="column.dataIndex === 'status'">
                  <a-switch
                    :checked="modelRecord.status === 'active'"
                    size="small"
                    disabled
                    checked-children="启用"
                    un-checked-children="停用"
                  />
                </template>
                <template v-if="column.key === 'action'">
                  <a-space>
                    <a-button type="link" size="small" @click="handleTest(modelRecord)">测试</a-button>
                    <a-button type="link" danger size="small" @click="handleDeleteModel(modelRecord)">删除</a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </div>
        </template>
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'type'">
            <a-tag :color="record.type === 'openai' ? 'blue' : 'green'">
              {{ record.type === 'openai' ? 'OpenAI' : 'Ollama' }}
            </a-tag>
          </template>
          <template v-if="column.dataIndex === 'status'">
            <a-switch
              :checked="record.status === 'active'"
              disabled
              checked-children="启用"
              un-checked-children="停用"
            />
          </template>
          <template v-if="column.key === 'action'">
            <a-dropdown>
              <a-button type="link" size="small">
                操作
              </a-button>
              <template #overlay>
                <a-menu @click="(info: { key: string }) => handleActionMenuClick(info, record)">
                  <a-menu-item key="edit"><EditOutlined /> 编辑</a-menu-item>
                  <a-menu-item key="delete" danger><DeleteOutlined /> 删除</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>
        </template>
      </a-table>
    </div>

    <!-- Add provider drawer -->
    <a-drawer
      :title="drawerTitle"
      :open="drawerVisible"
      :width="drawerWidth"
      @close="drawerVisible = false"
    >
      <a-form :model="addForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="类型" required>
          <a-radio-group v-model:value="addForm.type">
            <a-radio value="openai">OpenAI</a-radio>
            <a-radio value="ollama">Ollama</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="接入名称" required>
          <a-input v-model:value="addForm.name" placeholder="请输入接入名称" />
        </a-form-item>
        <a-form-item label="API 地址" required>
          <a-input v-model:value="addForm.api_url" placeholder="请输入 API 地址" />
        </a-form-item>
        <a-form-item label="API Key">
          <a-input-password v-model:value="addForm.api_key" placeholder="请输入 API Key（可选）" />
        </a-form-item>
        <a-form-item label=" ">
          <a-button :loading="fetchLoading" @click="handleFetchModels">
            获取模型列表
          </a-button>
        </a-form-item>
        <a-form-item label="选择模型" v-if="availableModels.length > 0">
          <a-checkbox-group v-model:value="selectedModels">
            <a-checkbox v-for="m in availableModels" :key="m.name" :value="m.name">
              {{ m.name }}
            </a-checkbox>
          </a-checkbox-group>
        </a-form-item>
      </a-form>
      <template #footer>
        <div style="text-align: right">
          <a-button style="margin-right: 8px" @click="drawerVisible = false">取消</a-button>
          <a-button type="primary" :loading="submitLoading" @click="handleSubmitAdd">确定</a-button>
        </div>
      </template>
    </a-drawer>

    <!-- Edit provider drawer -->
    <a-drawer
      title="编辑接入"
      :open="editDrawerVisible"
      :width="drawerWidth"
      @close="editDrawerVisible = false"
    >
      <a-form :model="editForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
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

    <!-- Test chat modal -->
    <a-modal
      :title="testModel ? `测试 - ${testModel.model_name}` : ''"
      :open="chatVisible"
      :footer="null"
      width="600px"
      @cancel="closeChat"
      :destroy-on-close="true"
    >
      <div class="chat-messages" ref="chatContainerRef">
        <div v-for="(msg, i) in messages" :key="i" :class="['chat-message', msg.role]">
          {{ msg.content }}
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
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import { useTableScrollY } from '@/composables/useTableScrollY'
import {
  getProviderListApi,
  createProviderApi,
  updateProviderApi,
  deleteProviderApi,
  fetchRemoteModelsApi,
  deleteModelApi,
  getChatStreamUrl,
  type ProviderItem,
  type LlmModelItem,
} from '@/api/model'
import { useUserStore } from '@/stores/user'

const { drawerWidth } = useDrawerWidth()
const tableScroll = useTableScrollY()

const columns = [
  { title: '接入名称', dataIndex: 'name', key: 'name', width: 150, ellipsis: { showTitle: true } },
  { title: '类型', dataIndex: 'type', key: 'type', width: 100 },
  { title: 'API 地址', dataIndex: 'api_url', key: 'api_url', width: 250, ellipsis: { showTitle: true } },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 100, align: 'center' as const },
]

const modelColumns = [
  { title: '模型名称', dataIndex: 'model_name', key: 'model_name', width: 200 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '操作', key: 'action', width: 150, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<ProviderItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const editDrawerVisible = ref(false)
const drawerTitle = ref('新增接入')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)
const expandedRowKeys = ref<number[]>([])

// search form
const searchForm = reactive({ name: '', type: undefined as string | undefined })

// add provider form (in drawer)
const addForm = reactive({
  type: 'openai',
  name: '',
  api_url: '',
  api_key: '',
})
const fetchLoading = ref(false)
const availableModels = ref<{ name: string; checked: boolean }[]>([])
const selectedModels = ref<string[]>([])

// edit provider form
const editForm = reactive({
  name: '',
  api_url: '',
  api_key: '',
  status: 'active',
})

// test model state (placeholder for chat modal in Task 8)
const testModel = ref<{ id: number; model_name: string } | null>(null)
const chatVisible = ref(false)
const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([])
const chatInput = ref('')
const chatLoading = ref(false)
const abortController = ref<AbortController | null>(null)
const chatContainerRef = ref<HTMLElement | null>(null)

async function fetchData() {
  loading.value = true
  try {
    const res = await getProviderListApi()
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

function handleAdd() {
  drawerTitle.value = '新增接入'
  addForm.type = 'openai'
  addForm.name = ''
  addForm.api_url = ''
  addForm.api_key = ''
  availableModels.value = []
  selectedModels.value = []
  drawerVisible.value = true
}

function handleEdit(record: ProviderItem) {
  editingId.value = record.id
  editForm.name = record.name
  editForm.api_url = record.api_url
  editForm.api_key = record.api_key || ''
  editForm.status = record.status
  editDrawerVisible.value = true
}

function handleDeleteProvider(record: ProviderItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除接入点「${record.name}」及其所有模型吗？`,
    okType: 'danger',
    okText: '删除',
    cancelText: '取消',
    async onOk() {
      await deleteProviderApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

function handleActionMenuClick({ key }: { key: string }, record: ProviderItem) {
  switch (key) {
    case 'edit':
      handleEdit(record)
      break
    case 'delete':
      handleDeleteProvider(record)
      break
  }
}

function handleExpand(expanded: boolean, record: ProviderItem) {
  if (expanded) {
    expandedRowKeys.value = [...expandedRowKeys.value, record.id]
  } else {
    expandedRowKeys.value = expandedRowKeys.value.filter((k) => k !== record.id)
  }
}

async function handleFetchModels() {
  if (!addForm.api_url) {
    message.warning('请先填写 API 地址')
    return
  }
  fetchLoading.value = true
  availableModels.value = []
  selectedModels.value = []
  try {
    const res = await fetchRemoteModelsApi({
      type: addForm.type,
      api_url: addForm.api_url,
      api_key: addForm.api_key || undefined,
    })
    availableModels.value = res.models.map((name) => ({ name, checked: false }))
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '获取模型列表失败')
  } finally {
    fetchLoading.value = false
  }
}

async function handleSubmitAdd() {
  if (!addForm.name || !addForm.api_url) {
    message.warning('请填写完整信息')
    return
  }
  if (selectedModels.value.length === 0) {
    message.warning('请至少选择一个模型')
    return
  }
  submitLoading.value = true
  try {
    await createProviderApi({
      name: addForm.name,
      type: addForm.type,
      api_url: addForm.api_url,
      api_key: addForm.api_key || undefined,
      models: selectedModels.value,
    })
    message.success('创建成功')
    drawerVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

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
  } finally {
    submitLoading.value = false
  }
}

async function handleDeleteModel(model: LlmModelItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除模型「${model.model_name}」吗？`,
    okType: 'danger',
    okText: '删除',
    cancelText: '取消',
    async onOk() {
      await deleteModelApi(model.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

function handleTest(model: LlmModelItem) {
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
    const response = await fetch(getChatStreamUrl(testModel.value.id), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`,
      },
      body: JSON.stringify({ message: userMsg }),
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
          if (chunk.done) break
        } catch { /* skip malformed chunk */ }
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
.model-sub-table {
  padding: 8px 0 8px 40px;
}
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
</style>
