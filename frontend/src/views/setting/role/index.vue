<template>
  <div class="page-container">
    <div class="page-section">
      <div class="page-toolbar">
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
        <div v-if="canCreate" class="page-toolbar-actions">
          <a-button type="primary" @click="handleAdd">
            <template #icon><PlusOutlined /></template>
            新增角色
          </a-button>
        </div>
      </div>
    </div>

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
          <template v-if="column.dataIndex === 'status'">
            <a-switch
              :checked="record.status === 'active'"
              checked-children="启用"
              un-checked-children="停用"
              :disabled="!canStatus"
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
                  <a-menu-item v-if="canEdit" key="edit"><EditOutlined /> 编辑</a-menu-item>
                  <a-menu-item v-if="canAssignPermission" key="permission"><SafetyOutlined /> 分配权限</a-menu-item>
                  <a-menu-item v-if="canDelete && !record.isBuiltin" key="delete" danger><DeleteOutlined /> 删除</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>
        </template>
      </a-table>
    </div>

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
          <a-button type="primary" :loading="permissionSubmitLoading" @click="handlePermissionOk">确定</a-button>
        </div>
      </template>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'SettingRole' })

import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined, SafetyOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import { useTableScrollY } from '@/composables/useTableScrollY'
import { useUserStore } from '@/stores/user'
import {
  getRoleListApi,
  createRoleApi,
  updateRoleApi,
  deleteRoleApi,
  updateRoleStatusApi,
  getRolePermissionsApi,
  updateRolePermissionsApi,
  type RoleItem,
} from '@/api/role'
import { getPermissionListApi } from '@/api/permission'

interface PermissionTreeNode {
  title: string
  key: number
  children?: PermissionTreeNode[]
}

const columns = [
  { title: '角色名称', dataIndex: 'name', key: 'name', width: 120, ellipsis: { showTitle: true } },
  { title: '角色编码', dataIndex: 'code', key: 'code', width: 120, ellipsis: { showTitle: true } },
  { title: '描述', dataIndex: 'description', key: 'description', width: 200, ellipsis: { showTitle: true } },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '内置角色', dataIndex: 'isBuiltin', key: 'isBuiltin', width: 100, align: 'center' as const },
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
const permissionRoleId = ref<number | null>(null)
const checkedPermissions = ref<number[]>([])
const permissionTree = ref<PermissionTreeNode[]>([])
const permissionSubmitLoading = ref(false)
const { drawerWidth } = useDrawerWidth()
const tableScroll = useTableScrollY()
const userStore = useUserStore()

const canCreate = computed(() => userStore.hasPermission('role:create'))
const canEdit = computed(() => userStore.hasPermission('role:update'))
const canDelete = computed(() => userStore.hasPermission('role:delete'))
const canStatus = computed(() => userStore.hasPermission('role:status'))
const canAssignPermission = computed(() => userStore.hasPermission('role:assign-permission'))

const searchForm = reactive({ name: '', status: undefined as string | undefined })
const formState = reactive({
  name: '',
  code: '',
  description: '',
  status: undefined as 'active' | 'inactive' | undefined,
})

function buildPermissionTree() {
  const groups = new Map<string, PermissionTreeNode>()
  for (const permission of permissionTree.value.flatMap((node) => node.children ?? [])) {
    const prefix = String(permission.title).split(':')[0] || '其他'
    if (!groups.has(prefix)) {
      groups.set(prefix, { title: prefix, key: -Math.floor(Math.random() * 1_000_000), children: [] })
    }
    groups.get(prefix)!.children!.push(permission)
  }
  permissionTree.value = Array.from(groups.values())
}

async function loadPermissionTree() {
  const res = await getPermissionListApi({})
  permissionTree.value = [{ title: '权限列表', key: 0, children: res.list.map((item) => ({ title: `${item.name} (${item.identifier})`, key: item.id })) }]
  buildPermissionTree()
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getRoleListApi({ name: searchForm.name, status: searchForm.status })
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
    okText: '删除',
    cancelText: '取消',
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
    await updateRoleStatusApi(record.id, newStatus)
    message.success('状态更新成功')
    await fetchData()
  } catch {
    message.error('状态更新失败')
  }
}

async function handleAssignPermission(record: RoleItem) {
  permissionRoleName.value = record.name
  permissionRoleId.value = record.id
  const [permissionRes, rolePermissionRes] = await Promise.all([
    getPermissionListApi({}),
    getRolePermissionsApi(record.id),
  ])
  const grouped = new Map<string, PermissionTreeNode>()
  for (const item of permissionRes.list) {
    const prefix = item.identifier.split(':')[0] || '其他'
    if (!grouped.has(prefix)) {
      grouped.set(prefix, { title: prefix, key: -item.id - 100000, children: [] })
    }
    grouped.get(prefix)!.children!.push({ title: `${item.name} (${item.identifier})`, key: item.id })
  }
  permissionTree.value = Array.from(grouped.values())
  checkedPermissions.value = rolePermissionRes.permissionIds
  permissionModalVisible.value = true
}

async function handlePermissionOk() {
  if (permissionRoleId.value === null) {
    return
  }
  permissionSubmitLoading.value = true
  try {
    const permissionIds = checkedPermissions.value.filter((id) => Number.isInteger(id) && id > 0)
    await updateRolePermissionsApi(permissionRoleId.value, permissionIds)
    message.success('权限分配成功')
    permissionModalVisible.value = false
  } finally {
    permissionSubmitLoading.value = false
  }
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

onMounted(async () => {
  await Promise.all([fetchData(), loadPermissionTree()])
})
</script>
