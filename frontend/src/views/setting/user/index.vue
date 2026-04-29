<template>
  <div>
    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="用户名">
          <a-input v-model:value="searchForm.username" placeholder="请输入用户名" allow-clear style="width: 200px" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchForm.status" placeholder="请选择状态" allow-clear style="width: 160px">
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="inactive">禁用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchData">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="用户列表">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增用户
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
        <a-form-item label="用户名" required>
          <a-input v-model:value="formState.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="邮箱" required>
          <a-input v-model:value="formState.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="角色" required>
          <a-select v-model:value="formState.role" placeholder="请选择角色">
            <a-select-option value="超级管理员">超级管理员</a-select-option>
            <a-select-option value="编辑">编辑</a-select-option>
            <a-select-option value="访客">访客</a-select-option>
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
defineOptions({ name: 'SettingUser' })

import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'

const { drawerWidth } = useDrawerWidth()

interface UserItem {
  id: number
  username: string
  email: string
  role: string
  status: 'active' | 'inactive'
  createdAt: string
}

const mockData: UserItem[] = [
  { id: 1, username: 'admin', email: 'admin@example.com', role: '超级管理员', status: 'active', createdAt: '2024-01-01 10:00:00' },
  { id: 2, username: 'editor', email: 'editor@example.com', role: '编辑', status: 'active', createdAt: '2024-02-01 10:00:00' },
  { id: 3, username: 'viewer', email: 'viewer@example.com', role: '访客', status: 'inactive', createdAt: '2024-03-01 10:00:00' },
]
let nextId = 4

const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '角色', dataIndex: 'role', key: 'role' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<UserItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const drawerTitle = ref('新增用户')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)

const searchForm = reactive({ username: '', status: undefined as string | undefined })
const formState = reactive({
  username: '',
  email: '',
  role: undefined as string | undefined,
  status: undefined as 'active' | 'inactive' | undefined,
})

function fetchData() {
  loading.value = true
  setTimeout(() => {
    let list = [...mockData]
    if (searchForm.username) {
      list = list.filter((item) => item.username.includes(searchForm.username))
    }
    if (searchForm.status) {
      list = list.filter((item) => item.status === searchForm.status)
    }
    dataSource.value = list
    total.value = list.length
    loading.value = false
  }, 300)
}

function handleReset() {
  searchForm.username = ''
  searchForm.status = undefined
  fetchData()
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增用户'
  formState.username = ''
  formState.email = ''
  formState.role = undefined
  formState.status = undefined
  drawerVisible.value = true
}

function handleEdit(record: UserItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑用户'
  formState.username = record.username
  formState.email = record.email
  formState.role = record.role
  formState.status = record.status
  drawerVisible.value = true
}

function handleDelete(record: UserItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户「${record.username}」吗？`,
    okType: 'danger',
    onOk() {
      const index = mockData.findIndex((item) => item.id === record.id)
      if (index !== -1) mockData.splice(index, 1)
      message.success('删除成功')
      fetchData()
    },
  })
}

function handleActionMenuClick({ key }: { key: string }, record: UserItem) {
  handleMenuClick(key, record)
}

function handleMenuClick(key: string, record: UserItem) {
  switch (key) {
    case 'edit': handleEdit(record); break
    case 'delete': handleDelete(record); break
  }
}

function handleStatusChange(record: UserItem) {
  const newStatus = record.status === 'active' ? 'inactive' : 'active'
  const index = mockData.findIndex((item) => item.id === record.id)
  if (index !== -1) {
    mockData[index].status = newStatus
    record.status = newStatus
  }
  message.success('状态更新成功')
  fetchData()
}

function handleSubmit() {
  if (!formState.username || !formState.email || !formState.role) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  const data = { ...formState }
  if (editingId.value === null && !data.status) {
    data.status = 'inactive'
  }
  setTimeout(() => {
    if (editingId.value !== null) {
      const index = mockData.findIndex((item) => item.id === editingId.value)
      if (index !== -1) {
        mockData[index] = { ...mockData[index], username: data.username, email: data.email, role: data.role!, status: data.status as 'active' | 'inactive' }
      }
      message.success('更新成功')
    } else {
      mockData.push({
        id: nextId++,
        username: data.username,
        email: data.email,
        role: data.role!,
        status: data.status as 'active' | 'inactive',
        createdAt: new Date().toLocaleString('zh-CN').replace(/\//g, '-'),
      })
      message.success('创建成功')
    }
    submitLoading.value = false
    drawerVisible.value = false
    fetchData()
  }, 300)
}

onMounted(fetchData)
</script>
