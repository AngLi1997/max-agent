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
        <a-button v-if="canCreate" type="primary" @click="handleAdd">
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
          <template v-if="column.dataIndex === 'roles'">
            {{ record.roles.map((item: { name: string }) => item.name).join('、') }}
          </template>
          <template v-if="column.dataIndex === 'status'">
            <a-switch
              :checked="record.status === 'active'"
              checked-children="启用"
              un-checked-children="停用"
              :disabled="!canStatus"
              @change="handleStatusChange(record)"
            />
          </template>
          <template v-if="column.dataIndex === 'isBuiltin'">
            <a-tag :color="record.isBuiltin ? 'blue' : 'default'">{{ record.isBuiltin ? '是' : '否' }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-dropdown>
              <a-button type="link" size="small">
                操作
              </a-button>
              <template #overlay>
                <a-menu @click="(info: { key: string }) => handleActionMenuClick(info, record)">
                  <a-menu-item v-if="canEdit" key="edit"><EditOutlined /> 编辑</a-menu-item>
                  <a-menu-item v-if="canDelete && !record.isBuiltin" key="delete" danger><DeleteOutlined /> 删除</a-menu-item>
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
          <a-select v-model:value="formState.roleIds" mode="multiple" placeholder="请选择角色" :options="roleOptions" />
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

import { ref, reactive, onMounted, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import { useUserStore } from '@/stores/user'
import {
  getUserListApi,
  createUserApi,
  updateUserApi,
  deleteUserApi,
  updateUserStatusApi,
  type UserListItem,
} from '@/api/user'
import { getRoleListApi } from '@/api/role'

const { drawerWidth } = useDrawerWidth()
const userStore = useUserStore()

const canCreate = computed(() => userStore.hasPermission('setting:user:create'))
const canEdit = computed(() => userStore.hasPermission('setting:user:update'))
const canDelete = computed(() => userStore.hasPermission('setting:user:delete'))
const canStatus = computed(() => userStore.hasPermission('setting:user:status'))

const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '角色', dataIndex: 'roles', key: 'roles' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '内置用户', dataIndex: 'isBuiltin', key: 'isBuiltin', width: 100, align: 'center' as const },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<UserListItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const drawerTitle = ref('新增用户')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)
const roleOptions = ref<{ label: string; value: number }[]>([])

const searchForm = reactive({ username: '', status: undefined as string | undefined })
const formState = reactive({
  username: '',
  email: '',
  roleIds: [] as number[],
  status: undefined as 'active' | 'inactive' | undefined,
})

async function fetchRoleOptions() {
  const res = await getRoleListApi({})
  roleOptions.value = res.list.map((item) => ({ label: item.name, value: item.id }))
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getUserListApi({ username: searchForm.username, status: searchForm.status })
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
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
  formState.roleIds = []
  formState.status = undefined
  drawerVisible.value = true
}

function handleEdit(record: UserListItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑用户'
  formState.username = record.username
  formState.email = record.email
  formState.roleIds = [...record.roleIds]
  formState.status = record.status
  drawerVisible.value = true
}

function handleDelete(record: UserListItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户「${record.username}」吗？`,
    okType: 'danger',
    async onOk() {
      await deleteUserApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

function handleActionMenuClick({ key }: { key: string }, record: UserListItem) {
  handleMenuClick(key, record)
}

function handleMenuClick(key: string, record: UserListItem) {
  switch (key) {
    case 'edit': handleEdit(record); break
    case 'delete': handleDelete(record); break
  }
}

async function handleStatusChange(record: UserListItem) {
  const newStatus = record.status === 'active' ? 'inactive' : 'active'
  try {
    await updateUserStatusApi(record.id, newStatus)
    message.success('状态更新成功')
    await fetchData()
  } catch {
    message.error('状态更新失败')
  }
}

async function handleSubmit() {
  if (!formState.username || !formState.email || formState.roleIds.length === 0) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    const status = (editingId.value !== null ? formState.status : (formState.status ?? 'inactive')) ?? 'inactive'
    const data = {
      username: formState.username,
      email: formState.email,
      roleIds: formState.roleIds,
      status,
    }
    if (editingId.value !== null) {
      await updateUserApi(editingId.value, data)
      message.success('更新成功')
    } else {
      const res = await createUserApi(data)
      message.success('创建成功')
      Modal.success({
        title: '用户创建成功',
        content: `临时密码：${res.temporaryPassword}`,
      })
    }
    drawerVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

onMounted(async () => {
  await Promise.all([fetchRoleOptions(), fetchData()])
})
</script>
