<template>
  <div>
    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="权限名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入权限名称" allow-clear style="width: 200px" />
        </a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="searchForm.type" placeholder="请选择类型" allow-clear style="width: 160px">
            <a-select-option value="菜单">菜单</a-select-option>
            <a-select-option value="按钮">按钮</a-select-option>
            <a-select-option value="API">API</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchData">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="权限列表">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增权限
        </a-button>
      </template>
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="{ total, pageSize: 10, showTotal: (t: number) => `共 ${t} 条` }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'default'">
              {{ record.status === 'active' ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleEdit(record)">编辑</a-button>
            <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-drawer
      :title="drawerTitle"
      :open="drawerVisible"
      width="480"
      @close="drawerVisible = false"
    >
      <a-form :model="formState" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="权限名称" required>
          <a-input v-model:value="formState.name" placeholder="请输入权限名称" />
        </a-form-item>
        <a-form-item label="权限标识" required>
          <a-input v-model:value="formState.identifier" placeholder="例如：user:read" />
        </a-form-item>
        <a-form-item label="类型" required>
          <a-select v-model:value="formState.type" placeholder="请选择类型">
            <a-select-option value="菜单">菜单</a-select-option>
            <a-select-option value="按钮">按钮</a-select-option>
            <a-select-option value="API">API</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态" required>
          <a-select v-model:value="formState.status">
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="inactive">禁用</a-select-option>
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
defineOptions({ name: 'SettingPermission' })

import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import {
  getPermissionListApi,
  createPermissionApi,
  updatePermissionApi,
  deletePermissionApi,
  type PermissionItem,
} from '../../../api/permission'

const columns = [
  { title: '权限名称', dataIndex: 'name', key: 'name' },
  { title: '权限标识', dataIndex: 'identifier', key: 'identifier' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '操作', key: 'action', width: 120 },
]

const loading = ref(false)
const dataSource = ref<PermissionItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const drawerTitle = ref('新增权限')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)

const searchForm = reactive({ name: '', type: undefined as string | undefined })
const formState = reactive({
  name: '',
  identifier: '',
  type: undefined as '菜单' | '按钮' | 'API' | undefined,
  status: 'active' as 'active' | 'inactive',
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getPermissionListApi({ name: searchForm.name, type: searchForm.type })
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
  drawerTitle.value = '新增权限'
  formState.name = ''
  formState.identifier = ''
  formState.type = undefined
  formState.status = 'active'
  drawerVisible.value = true
}

function handleEdit(record: PermissionItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑权限'
  formState.name = record.name
  formState.identifier = record.identifier
  formState.type = record.type
  formState.status = record.status
  drawerVisible.value = true
}

function handleDelete(record: PermissionItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除权限「${record.name}」吗？`,
    okType: 'danger',
    async onOk() {
      await deletePermissionApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

async function handleSubmit() {
  if (!formState.name || !formState.identifier || !formState.type) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    const data = { name: formState.name, identifier: formState.identifier, type: formState.type, status: formState.status }
    if (editingId.value !== null) {
      await updatePermissionApi(editingId.value, data)
      message.success('更新成功')
    } else {
      await createPermissionApi(data)
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
