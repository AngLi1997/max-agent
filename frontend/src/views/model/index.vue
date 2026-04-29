<template>
  <div>
    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="模型名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入模型名称" allow-clear style="width: 200px" />
        </a-form-item>
        <a-form-item label="提供商">
          <a-select v-model:value="searchForm.provider" placeholder="请选择提供商" allow-clear style="width: 160px">
            <a-select-option value="OpenAI">OpenAI</a-select-option>
            <a-select-option value="Anthropic">Anthropic</a-select-option>
            <a-select-option value="Google">Google</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchData">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="模型列表">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增模型
        </a-button>
      </template>
      <a-table
        size="small"
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="{ total, pageSize: 10, showTotal: (t: number) => `共 ${t} 条` }"
        row-key="id"
      >
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
    </a-card>

    <a-drawer
      :title="drawerTitle"
      :open="drawerVisible"
      :width="drawerWidth"
      @close="drawerVisible = false"
    >
      <a-form :model="formState" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="模型名称" required>
          <a-input v-model:value="formState.name" placeholder="请输入模型名称" />
        </a-form-item>
        <a-form-item label="提供商" required>
          <a-select v-model:value="formState.provider" placeholder="请选择提供商">
            <a-select-option value="OpenAI">OpenAI</a-select-option>
            <a-select-option value="Anthropic">Anthropic</a-select-option>
            <a-select-option value="Google">Google</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
      <template #footer>
        <div style="text-align: right">
          <a-button style="margin-right: 8px" @click="drawerVisible = false">取消</a-button>
          <a-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</a-button>
        </div>
      </template>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'Model' })

import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import {
  getModelListApi,
  createModelApi,
  updateModelApi,
  deleteModelApi,
  type ModelItem,
} from '../../api/model'

const { drawerWidth } = useDrawerWidth()

const columns = [
  { title: '模型名称', dataIndex: 'name', key: 'name' },
  { title: '提供商', dataIndex: 'provider', key: 'provider' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<ModelItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const drawerTitle = ref('新增模型')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)

const searchForm = reactive({ name: '', provider: undefined as string | undefined })
const formState = reactive({ name: '', provider: undefined as string | undefined, status: undefined as 'active' | 'inactive' | undefined })

async function fetchData() {
  loading.value = true
  try {
    const res = await getModelListApi({ name: searchForm.name, provider: searchForm.provider })
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.name = ''
  searchForm.provider = undefined
  fetchData()
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增模型'
  formState.name = ''
  formState.provider = undefined
  formState.status = undefined
  drawerVisible.value = true
}

function handleEdit(record: ModelItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑模型'
  formState.name = record.name
  formState.provider = record.provider
  formState.status = record.status
  drawerVisible.value = true
}

function handleDelete(record: ModelItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除模型「${record.name}」吗？`,
    okType: 'danger',
    async onOk() {
      await deleteModelApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

function handleActionMenuClick({ key }: { key: string }, record: ModelItem) {
  handleMenuClick(key, record)
}

function handleMenuClick(key: string, record: ModelItem) {
  switch (key) {
    case 'edit': handleEdit(record); break
    case 'delete': handleDelete(record); break
  }
}

async function handleStatusChange(record: ModelItem) {
  const newStatus = record.status === 'active' ? 'inactive' : 'active'
  try {
    await updateModelApi(record.id, { ...record, status: newStatus })
    message.success('状态更新成功')
    await fetchData()
  } catch {
    message.error('状态更新失败')
  }
}

async function handleSubmit() {
  if (!formState.name || !formState.provider) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    const data = { ...formState }
    if (editingId.value === null && !data.status) {
      data.status = 'inactive'
    }
    if (editingId.value !== null) {
      await updateModelApi(editingId.value, { name: data.name, provider: data.provider!, status: data.status as 'active' | 'inactive' })
      message.success('更新成功')
    } else {
      await createModelApi({ name: data.name, provider: data.provider!, status: data.status as 'active' | 'inactive' })
      message.success('创建成功')
    }
    drawerVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

onMounted(fetchData)
</script>
