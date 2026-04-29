<template>
  <div>
    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="操作人">
          <a-input v-model:value="searchForm.operator" placeholder="请输入操作人" allow-clear style="width: 180px" />
        </a-form-item>
        <a-form-item label="模块">
          <a-select v-model:value="searchForm.module" placeholder="请选择模块" allow-clear style="width: 180px">
            <a-select-option value="用户管理">用户管理</a-select-option>
            <a-select-option value="模型管理">模型管理</a-select-option>
            <a-select-option value="角色管理">角色管理</a-select-option>
            <a-select-option value="工具管理">工具管理</a-select-option>
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
    </a-card>

    <a-card title="操作日志列表">
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="{ total, pageSize: 10, showTotal: (t: number) => `共 ${t} 条` }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'method'">
            <a-tag :color="methodColorMap[record.method]">{{ record.method }}</a-tag>
          </template>
          <template v-if="column.key === 'result'">
            <a-tag :color="record.result === '成功' ? 'green' : 'red'">{{ record.result }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleViewDetail(record)">查看详情</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      title="日志详情"
      :open="detailModalVisible"
      :footer="null"
      @cancel="detailModalVisible = false"
      width="640"
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
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getOperationLogApi, type OperationLogItem } from '../../../api/log'

const columns = [
  { title: '操作人', dataIndex: 'operator', key: 'operator' },
  { title: '模块', dataIndex: 'module', key: 'module' },
  { title: '操作类型', dataIndex: 'action', key: 'actionType' },
  { title: '请求方法', dataIndex: 'method', key: 'method' },
  { title: '结果', dataIndex: 'result', key: 'result' },
  { title: '时间', dataIndex: 'time', key: 'time' },
  { title: '操作', key: 'action', width: 100 },
]

const methodColorMap: Record<string, string> = {
  GET: 'blue',
  POST: 'green',
  PUT: 'orange',
  DELETE: 'red',
}

const loading = ref(false)
const dataSource = ref<OperationLogItem[]>([])
const total = ref(0)
const detailModalVisible = ref(false)
const currentDetail = ref<OperationLogItem | null>(null)

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
  }
}

function handleReset() {
  searchForm.operator = ''
  searchForm.module = undefined
  searchForm.timeRange = []
  fetchData()
}

function handleViewDetail(record: OperationLogItem) {
  currentDetail.value = record
  detailModalVisible.value = true
}

onMounted(fetchData)
</script>
