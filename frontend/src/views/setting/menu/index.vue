<template>
  <div>
    <a-card title="菜单列表">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增菜单
        </a-button>
      </template>
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        row-key="id"
        :pagination="false"
        childrenColumnName="children"
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
            <a-button type="link" @click="handleAddChild(record)">新增子菜单</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-drawer
      :title="drawerTitle"
      :open="drawerVisible"
      width="520"
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
        <a-form-item label="排序" required>
          <a-input-number v-model:value="formState.sort" :min="1" style="width: 100%" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { getMenuTreeApi, createMenuApi, updateMenuApi, deleteMenuApi, type MenuItem } from '../../../api/menu'

const columns = [
  { title: '菜单名称', dataIndex: 'name', key: 'name' },
  { title: '路由', dataIndex: 'path', key: 'path' },
  { title: '权限标识', dataIndex: 'permission', key: 'permission' },
  { title: '排序', dataIndex: 'sort', key: 'sort', width: 80 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 220 },
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
  sort: 1,
  status: 'active' as 'active' | 'inactive',
})

const menuTreeOptions = computed(() => dataSource.value)

async function fetchData() {
  loading.value = true
  try {
    dataSource.value = await getMenuTreeApi()
  } finally {
    loading.value = false
  }
}

function resetForm() {
  formState.name = ''
  formState.parentId = null
  formState.path = ''
  formState.permission = ''
  formState.sort = 1
  formState.status = 'active'
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
  formState.sort = record.sort
  formState.status = record.status
  drawerVisible.value = true
}

function handleDelete(record: MenuItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除菜单「${record.name}」吗？`,
    okType: 'danger',
    async onOk() {
      await deleteMenuApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

async function handleSubmit() {
  if (!formState.name || !formState.path) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    const data = {
      name: formState.name,
      parentId: formState.parentId,
      path: formState.path,
      permission: formState.permission,
      sort: formState.sort,
      status: formState.status,
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
