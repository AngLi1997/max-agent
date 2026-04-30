<template>
  <div class="page-container">
    <div class="page-section">
      <div class="page-toolbar">
        <a-form layout="inline" :model="searchForm">
          <a-form-item label="操作人">
            <a-input v-model:value="searchForm.operator" placeholder="请输入操作人" allow-clear style="width: 180px" />
          </a-form-item>
          <a-form-item label="模块">
            <a-select v-model:value="searchForm.module" placeholder="请选择模块" allow-clear style="width: 180px">
              <a-select-option value="用户管理">用户管理</a-select-option>
              <a-select-option value="角色管理">角色管理</a-select-option>
              <a-select-option value="权限管理">权限管理</a-select-option>
              <a-select-option value="菜单管理">菜单管理</a-select-option>
              <a-select-option value="系统配置">系统配置</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="时间范围">
            <a-range-picker v-model:value="searchForm.timeRange" show-time />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="fetchData">查询</a-button>
            <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
          </a-form-item>
        </a-form>
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
          <template v-if="column.key === 'method'">
            <a-tag :class="methodClassMap[record.method] || 'page-method-tag'">{{ record.method }}</a-tag>
          </template>
          <template v-if="column.key === 'result'">
            <a-tag class="page-status-tag">{{ record.result }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-dropdown>
              <a-button type="link" size="small">
                操作
              </a-button>
              <template #overlay>
                <a-menu @click="(info: { key: string }) => handleActionMenuClick(info, record)">
                  <a-menu-item v-if="canRead" key="detail"><EyeOutlined /> 查看详情</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>
        </template>
      </a-table>
    </div>

    <a-drawer
      v-model:open="detailVisible"
      title="日志详情"
      :width="drawerWidth"
    >
      <a-descriptions bordered :column="1" size="small">
        <a-descriptions-item label="操作人">{{ currentDetail?.operator }}</a-descriptions-item>
        <a-descriptions-item label="模块">{{ currentDetail?.module }}</a-descriptions-item>
        <a-descriptions-item label="操作类型">{{ currentDetail?.action }}</a-descriptions-item>
        <a-descriptions-item label="请求方法">{{ currentDetail?.method }}</a-descriptions-item>
        <a-descriptions-item label="结果">{{ currentDetail?.result }}</a-descriptions-item>
        <a-descriptions-item label="时间">{{ currentDetail?.time }}</a-descriptions-item>
        <a-descriptions-item label="详情">{{ currentDetail?.detail }}</a-descriptions-item>
      </a-descriptions>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'SettingOperationLog' })

import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { EyeOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import { useTableScrollY } from '@/composables/useTableScrollY'
import { useUserStore } from '@/stores/user'
import { getOperationLogApi, type OperationLogItem } from '../../../api/log'

const columns = [
  { title: '操作人', dataIndex: 'operator', key: 'operator', width: 100, ellipsis: { showTitle: true } },
  { title: '模块', dataIndex: 'module', key: 'module', width: 100, ellipsis: { showTitle: true } },
  { title: '操作类型', dataIndex: 'action', key: 'actionType', width: 100, ellipsis: { showTitle: true } },
  { title: '请求方法', dataIndex: 'method', key: 'method', width: 100 },
  { title: '结果', dataIndex: 'result', key: 'result', width: 80 },
  { title: '时间', dataIndex: 'time', key: 'time', width: 180, ellipsis: { showTitle: true } },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const methodClassMap: Record<string, string> = {
  GET: 'page-method-tag',
  POST: 'page-method-tag',
  PUT: 'page-method-tag page-method-tag--soft',
  PATCH: 'page-method-tag page-method-tag--soft',
  DELETE: 'page-method-tag page-method-tag--soft',
}

const loading = ref(false)
const dataSource = ref<OperationLogItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const currentDetail = ref<OperationLogItem | null>(null)
const { drawerWidth } = useDrawerWidth()
const tableScroll = useTableScrollY()
const userStore = useUserStore()
const canRead = computed(() => userStore.hasPermission('operation-log:read'))

const searchForm = reactive({
  operator: '',
  module: undefined as string | undefined,
  timeRange: [] as { format: (template?: string) => string }[],
})

async function fetchData() {
  loading.value = true
  try {
    const [start, end] = searchForm.timeRange || []
    const res = await getOperationLogApi({
      operator: searchForm.operator,
      module: searchForm.module,
      startTime: start ? start.format('YYYY-MM-DD HH:mm:ss') : undefined,
      endTime: end ? end.format('YYYY-MM-DD HH:mm:ss') : undefined,
    })
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
    await nextTick()
    tableScroll.updateTableScrollY()
  }
}

function handleReset() {
  searchForm.operator = ''
  searchForm.module = undefined
  searchForm.timeRange = []
  fetchData()
}

function handleActionMenuClick({ key }: { key: string }, record: OperationLogItem) {
  if (key === 'detail') {
    handleViewDetail(record)
  }
}

function handleViewDetail(record: OperationLogItem) {
  currentDetail.value = record
  detailVisible.value = true
}

onMounted(() => {
  if (canRead.value) fetchData()
})
</script>
