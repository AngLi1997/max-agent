<template>
  <div>
    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入工具名称" allow-clear style="width: 200px" />
        </a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="searchForm.type" placeholder="请选择类型" allow-clear style="width: 140px">
            <a-select-option value="搜索">搜索</a-select-option>
            <a-select-option value="执行">执行</a-select-option>
            <a-select-option value="文件">文件</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchData">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="工具列表">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增工具
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
      <a-form :model="formState" :label-col="{ span: 5 }" :wrapper-col="{ span: 17 }">
        <a-form-item label="名称" required>
          <a-input v-model:value="formState.name" placeholder="请输入工具名称" />
        </a-form-item>
        <a-form-item label="类型" required>
          <a-select v-model:value="formState.type" placeholder="请选择类型">
            <a-select-option value="搜索">搜索</a-select-option>
            <a-select-option value="执行">执行</a-select-option>
            <a-select-option value="文件">文件</a-select-option>
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
defineOptions({ name: 'Tool' })

import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, DownOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import {
  getToolListApi,
  createToolApi,
  updateToolApi,
  deleteToolApi,
  type ToolItem,
} from '../../api/tool'

const columns = [
  { title: '名称', dataIndex: 'name', key: 'name', width: 160 },
  { title: '类型', dataIndex: 'type', key: 'type', width: 100 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt', width: 180 },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<ToolItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const drawerTitle = ref('新增工具')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)
const { drawerWidth } = useDrawerWidth()

const searchForm = reactive({ name: '', type: undefined as '搜索' | '执行' | '文件' | undefined })
const formState = reactive({
  name: '',
  type: undefined as '搜索' | '执行' | '文件' | undefined,
  status: undefined as 'active' | 'inactive' | undefined,
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getToolListApi({ name: searchForm.name, type: searchForm.type })
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.name = ''
  searchForm.type = undefined
  fetchData()
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增工具'
  formState.name = ''
  formState.type = undefined
  formState.status = undefined
  drawerVisible.value = true
}

function handleEdit(record: ToolItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑工具'
  formState.name = record.name
  formState.type = record.type
  formState.status = record.status
  drawerVisible.value = true
}

function handleActionMenuClick({ key }: { key: string }, record: ToolItem) {
  handleMenuClick(key, record)
}

function handleMenuClick(key: string, record: ToolItem) {
  if (key === 'edit') {
    handleEdit(record)
    return
  }
  if (key === 'delete') {
    handleDelete(record)
  }
}

async function handleStatusChange(record: ToolItem) {
  const newStatus = record.status === 'active' ? 'inactive' : 'active'
  try {
    await updateToolApi(record.id, {
      name: record.name,
      type: record.type,
      status: newStatus,
    })
    message.success('状态更新成功')
    await fetchData()
  } catch {
    message.error('状态更新失败')
  }
}

function handleDelete(record: ToolItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除工具「${record.name}」吗？`,
    okType: 'danger',
    async onOk() {
      await deleteToolApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

async function handleSubmit() {
  if (!formState.name || !formState.type) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    const status = (editingId.value !== null ? formState.status : (formState.status ?? 'inactive')) ?? 'inactive'
    const data = { name: formState.name, type: formState.type!, status }
    if (editingId.value !== null) {
      await updateToolApi(editingId.value, data)
      message.success('更新成功')
    } else {
      await createToolApi(data)
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
