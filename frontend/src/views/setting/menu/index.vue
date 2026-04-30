<template>
  <div class="page-container">
    <div class="page-section">
      <div class="page-toolbar">
        <div></div>
        <div v-if="canCreate" class="page-toolbar-actions">
          <a-button type="primary" @click="handleAdd">
            <template #icon><PlusOutlined /></template>
            新增菜单
          </a-button>
        </div>
      </div>
    </div>

    <div :ref="tableScroll.tableSectionRef" class="page-section page-table-section">
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        row-key="id"
        :pagination="false"
        childrenColumnName="children"
        size="middle"
        :scroll="{ y: tableScroll.tableScrollY }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
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
                  <a-menu-item v-if="canCreate" key="addChild"><PlusOutlined /> 新增子菜单</a-menu-item>
                  <a-menu-divider />
                  <a-menu-item v-if="canDelete" key="delete" danger><DeleteOutlined /> 删除</a-menu-item>
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
        <a-form-item label="菜单名称" required>
          <a-input v-model:value="formState.name" placeholder="请输入菜单名称" />
        </a-form-item>
        <a-form-item label="父菜单">
          <a-tree-select
            v-model:value="formState.parentId"
            :tree-data="menuTreeOptions"
            allow-clear
            placeholder="请选择父菜单"
            style="width: 100%"
            :field-names="{ label: 'name', value: 'id', children: 'children' }"
            tree-default-expand-all
          />
        </a-form-item>
        <a-form-item label="路由" required>
          <a-input v-model:value="formState.path" placeholder="请输入路由" />
        </a-form-item>
        <a-form-item label="权限标识">
          <a-input v-model:value="formState.permission" placeholder="请输入权限标识" />
        </a-form-item>
        <a-form-item label="图标">
          <a-input v-model:value="formState.icon" placeholder="请输入图标名" />
        </a-form-item>
        <a-form-item label="组件路径">
          <a-input v-model:value="formState.component" placeholder="请输入组件路径" />
        </a-form-item>
        <a-form-item label="排序" required>
          <a-input-number v-model:value="formState.sort" :min="1" style="width: 100%" />
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
defineOptions({ name: 'SettingMenu' })

import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { getMenuTreeApi, createMenuApi, updateMenuApi, deleteMenuApi, updateMenuStatusApi, type MenuItem } from '../../../api/menu'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import { useTableScrollY } from '@/composables/useTableScrollY'
import { useUserStore } from '@/stores/user'

const { drawerWidth } = useDrawerWidth()
const tableScroll = useTableScrollY()
const userStore = useUserStore()

const canCreate = computed(() => userStore.hasPermission('menu:create'))
const canEdit = computed(() => userStore.hasPermission('menu:update'))
const canDelete = computed(() => userStore.hasPermission('menu:delete'))
const canStatus = computed(() => userStore.hasPermission('menu:status'))

const columns = [
  { title: '菜单名称', dataIndex: 'name', key: 'name', width: 180, ellipsis: { showTitle: true } },
  { title: '路由', dataIndex: 'path', key: 'path', width: 180, ellipsis: { showTitle: true } },
  { title: '权限标识', dataIndex: 'permission', key: 'permission', width: 150, ellipsis: { showTitle: true } },
  { title: '排序', dataIndex: 'sort', key: 'sort', width: 80 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100, align: 'center' as const },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<MenuItem[]>([])
const drawerVisible = ref(false)
const drawerTitle = ref('新增菜单')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)

const formState = reactive({
  name: '',
  parentId: null as number | null,
  path: '',
  permission: '',
  icon: '',
  component: '',
  sort: 1,
  status: '' as 'active' | 'inactive' | '',
})

const menuTreeOptions = computed(() => dataSource.value)

async function fetchData() {
  loading.value = true
  try {
    dataSource.value = await getMenuTreeApi()
  } finally {
    loading.value = false
    await nextTick()
    tableScroll.updateTableScrollY()
  }
}

function resetForm() {
  formState.name = ''
  formState.parentId = null
  formState.path = ''
  formState.permission = ''
  formState.icon = ''
  formState.component = ''
  formState.sort = 1
  formState.status = ''
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增菜单'
  resetForm()
  drawerVisible.value = true
}

function handleAddChild(record: MenuItem) {
  editingId.value = null
  drawerTitle.value = '新增子菜单'
  resetForm()
  formState.parentId = record.id
  drawerVisible.value = true
}

function handleEdit(record: MenuItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑菜单'
  formState.name = record.name
  formState.parentId = record.parentId
  formState.path = record.path
  formState.permission = record.permission
  formState.icon = record.icon
  formState.component = record.component
  formState.sort = record.sort
  formState.status = record.status
  drawerVisible.value = true
}

function handleDelete(record: MenuItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除菜单「${record.name}」吗？`,
    okType: 'danger',
    okText: '删除',
    cancelText: '取消',
    async onOk() {
      await deleteMenuApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

async function handleStatusChange(record: MenuItem) {
  const newStatus = record.status === 'active' ? 'inactive' : 'active'
  try {
    await updateMenuStatusApi(record.id, newStatus)
    message.success('状态更新成功')
    await fetchData()
  } catch {
    message.error('状态更新失败')
  }
}

function handleMenuClick(key: string, record: MenuItem) {
  switch (key) {
    case 'edit': handleEdit(record); break
    case 'addChild': handleAddChild(record); break
    case 'delete': handleDelete(record); break
  }
}

function handleActionMenuClick({ key }: { key: string }, record: MenuItem) {
  handleMenuClick(key, record)
}

async function handleSubmit() {
  if (!formState.name || !formState.path) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    const status = (editingId.value === null && !formState.status)
      ? 'inactive'
      : (formState.status as 'active' | 'inactive')
    const data = {
      name: formState.name,
      parentId: formState.parentId,
      path: formState.path,
      permission: formState.permission,
      icon: formState.icon,
      component: formState.component,
      sort: formState.sort,
      status,
    }
    if (editingId.value !== null) {
      await updateMenuApi(editingId.value, data)
      message.success('更新成功')
    } else {
      await createMenuApi(data)
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
