<template>
  <div>
    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="角色名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入角色名称" allow-clear style="width: 200px" />
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

    <a-card title="角色列表">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增角色
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
                操作 <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu @click="(info: { key: string }) => handleActionMenuClick(info, record)">
                  <a-menu-item key="edit"><EditOutlined /> 编辑</a-menu-item>
                  <a-menu-item key="permission"><SafetyOutlined /> 分配权限</a-menu-item>
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
        <a-form-item label="角色名称" required>
          <a-input v-model:value="formState.name" placeholder="请输入角色名称" />
        </a-form-item>
        <a-form-item label="角色编码" required>
          <a-input v-model:value="formState.code" placeholder="请输入角色编码" />
        </a-form-item>
        <a-form-item label="描述">
          <a-input v-model:value="formState.description" placeholder="请输入描述" />
        </a-form-item>
      </a-form>
      <template #footer>
        <div style="text-align: right">
          <a-button style="margin-right: 8px" @click="drawerVisible = false">取消</a-button>
          <a-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</a-button>
        </div>
      </template>
    </a-drawer>

    <a-drawer
      v-model:open="permissionModalVisible"
      :title="`分配权限 - ${permissionRoleName}`"
      :width="drawerWidth"
    >
      <a-tree
        v-model:checkedKeys="checkedPermissions"
        checkable
        :tree-data="permissionTree"
        :field-names="{ title: 'title', key: 'key', children: 'children' }"
        default-expand-all
      />
      <template #footer>
        <div style="text-align: right;">
          <a-button style="margin-right: 8px;" @click="permissionModalVisible = false">取消</a-button>
          <a-button type="primary" @click="handlePermissionOk">确定</a-button>
        </div>
      </template>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'SettingRole' })

import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, DownOutlined, EditOutlined, DeleteOutlined, SafetyOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import {
  getRoleListApi,
  createRoleApi,
  updateRoleApi,
  deleteRoleApi,
  type RoleItem,
} from '../../../api/role'

const permissionTree = [
  { title: '仪表盘', key: 'dashboard' },
  {
    title: '模型管理', key: 'model',
    children: [
      { title: '查看', key: 'model:read' },
      { title: '新增', key: 'model:create' },
      { title: '编辑', key: 'model:update' },
      { title: '删除', key: 'model:delete' },
    ],
  },
  {
    title: 'Skills管理', key: 'skill',
    children: [
      { title: '查看', key: 'skill:read' },
      { title: '新增', key: 'skill:create' },
      { title: '编辑', key: 'skill:update' },
      { title: '删除', key: 'skill:delete' },
    ],
  },
  {
    title: '工具管理', key: 'tool',
    children: [
      { title: '查看', key: 'tool:read' },
      { title: '新增', key: 'tool:create' },
      { title: '编辑', key: 'tool:update' },
      { title: '删除', key: 'tool:delete' },
    ],
  },
  {
    title: '系统设置', key: 'setting',
    children: [
      { title: '用户管理', key: 'setting:user' },
      { title: '角色管理', key: 'setting:role' },
      { title: '权限管理', key: 'setting:permission' },
      { title: '菜单配置', key: 'setting:menu' },
      { title: '系统配置', key: 'setting:config' },
      { title: '操作日志', key: 'setting:operation-log' },
      { title: '登录日志', key: 'setting:login-log' },
    ],
  },
]

const columns = [
  { title: '角色名称', dataIndex: 'name', key: 'name' },
  { title: '角色编码', dataIndex: 'code', key: 'code' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<RoleItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const drawerTitle = ref('新增角色')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)
const permissionModalVisible = ref(false)
const permissionRoleName = ref('')
const checkedPermissions = ref<string[]>([])
const { drawerWidth } = useDrawerWidth()

const searchForm = reactive({ name: '', status: undefined as string | undefined })
const formState = reactive({
  name: '',
  code: '',
  description: '',
  status: undefined as 'active' | 'inactive' | undefined,
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getRoleListApi({ name: searchForm.name, status: searchForm.status })
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.name = ''
  searchForm.status = undefined
  fetchData()
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增角色'
  formState.name = ''
  formState.code = ''
  formState.description = ''
  formState.status = undefined
  drawerVisible.value = true
}

function handleEdit(record: RoleItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑角色'
  formState.name = record.name
  formState.code = record.code
  formState.description = record.description
  formState.status = record.status
  drawerVisible.value = true
}

function handleDelete(record: RoleItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除角色「${record.name}」吗？`,
    okType: 'danger',
    async onOk() {
      await deleteRoleApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

function handleActionMenuClick({ key }: { key: string }, record: RoleItem) {
  handleMenuClick(key, record)
}

function handleMenuClick(key: string, record: RoleItem) {
  if (key === 'edit') {
    handleEdit(record)
    return
  }
  if (key === 'delete') {
    handleDelete(record)
    return
  }
  if (key === 'permission') {
    handleAssignPermission(record)
  }
}

async function handleStatusChange(record: RoleItem) {
  const newStatus = record.status === 'active' ? 'inactive' : 'active'
  try {
    await updateRoleApi(record.id, {
      name: record.name,
      code: record.code,
      description: record.description,
      status: newStatus,
    })
    message.success('状态更新成功')
    await fetchData()
  } catch {
    message.error('状态更新失败')
  }
}

function handleAssignPermission(record: RoleItem) {
  permissionRoleName.value = record.name
  checkedPermissions.value = []
  permissionModalVisible.value = true
}

function handlePermissionOk() {
  message.success('权限分配成功')
  permissionModalVisible.value = false
}

async function handleSubmit() {
  if (!formState.name || !formState.code) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    const status = (editingId.value !== null ? formState.status : (formState.status ?? 'inactive')) ?? 'inactive'
    const data = { name: formState.name, code: formState.code, description: formState.description, status }
    if (editingId.value !== null) {
      await updateRoleApi(editingId.value, data)
      message.success('更新成功')
    } else {
      await createRoleApi(data)
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
