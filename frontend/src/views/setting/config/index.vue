<template>
  <div>
    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="配置key">
          <a-input v-model:value="searchForm.key" placeholder="请输入配置key" allow-clear style="width: 220px" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchData">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="配置列表">
      <template #extra>
        <a-button v-if="canCreate" type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增配置
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
          <template v-if="column.key === 'action'">
            <a-dropdown>
              <a-button type="link" size="small">
                操作
              </a-button>
              <template #overlay>
                <a-menu @click="(info: { key: string }) => handleActionMenuClick(info, record)">
                  <a-menu-item v-if="canEdit" key="edit"><EditOutlined /> 编辑</a-menu-item>
                  <a-menu-item v-if="canDelete" key="delete" danger><DeleteOutlined /> 删除</a-menu-item>
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
        <a-form-item label="配置项名称" required>
          <a-input v-model:value="formState.name" placeholder="请输入配置项名称" />
        </a-form-item>
        <a-form-item label="key" required>
          <a-input v-model:value="formState.key" placeholder="请输入key" />
        </a-form-item>
        <a-form-item label="value" required>
          <a-input v-model:value="formState.value" placeholder="请输入value" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="formState.description" :rows="4" placeholder="请输入描述" />
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
defineOptions({ name: 'SettingConfig' })

import { ref, reactive, onMounted, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import { useUserStore } from '@/stores/user'
import {
  getConfigListApi,
  createConfigApi,
  updateConfigApi,
  deleteConfigApi,
  type ConfigItem,
} from '../../../api/config'

const columns = [
  { title: '配置项名称', dataIndex: 'name', key: 'name' },
  { title: 'key', dataIndex: 'key', key: 'key' },
  { title: 'value', dataIndex: 'value', key: 'value' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<ConfigItem[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const drawerTitle = ref('新增配置')
const editingId = ref<number | null>(null)
const submitLoading = ref(false)
const { drawerWidth } = useDrawerWidth()
const userStore = useUserStore()

const canCreate = computed(() => userStore.hasPermission('config:create'))
const canEdit = computed(() => userStore.hasPermission('config:update'))
const canDelete = computed(() => userStore.hasPermission('config:delete'))

const searchForm = reactive({ key: '' })
const formState = reactive({ name: '', key: '', value: '', description: '' })

async function fetchData() {
  loading.value = true
  try {
    const res = await getConfigListApi({ key: searchForm.key })
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.key = ''
  fetchData()
}

function handleAdd() {
  editingId.value = null
  drawerTitle.value = '新增配置'
  formState.name = ''
  formState.key = ''
  formState.value = ''
  formState.description = ''
  drawerVisible.value = true
}

function handleActionMenuClick({ key }: { key: string }, record: ConfigItem) {
  handleMenuClick(key, record)
}

function handleMenuClick(key: string, record: ConfigItem) {
  if (key === 'edit') {
    handleEdit(record)
    return
  }
  if (key === 'delete') {
    handleDelete(record)
  }
}

function handleEdit(record: ConfigItem) {
  editingId.value = record.id
  drawerTitle.value = '编辑配置'
  formState.name = record.name
  formState.key = record.key
  formState.value = record.value
  formState.description = record.description
  drawerVisible.value = true
}

function handleDelete(record: ConfigItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除配置项「${record.name}」吗？`,
    okType: 'danger',
    async onOk() {
      await deleteConfigApi(record.id)
      message.success('删除成功')
      fetchData()
    },
  })
}

async function handleSubmit() {
  if (!formState.name || !formState.key || !formState.value) {
    message.warning('请填写完整信息')
    return
  }
  submitLoading.value = true
  try {
    const data = { name: formState.name, key: formState.key, value: formState.value, description: formState.description }
    if (editingId.value !== null) {
      await updateConfigApi(editingId.value, data)
      message.success('更新成功')
    } else {
      await createConfigApi(data)
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
