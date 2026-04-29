<template>
  <div>
    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="用户名">
          <a-input v-model:value="searchForm.username" placeholder="请输入用户名" allow-clear style="width: 180px" />
        </a-form-item>
        <a-form-item label="登录结果">
          <a-select v-model:value="searchForm.result" placeholder="请选择结果" allow-clear style="width: 160px">
            <a-select-option value="成功">成功</a-select-option>
            <a-select-option value="失败">失败</a-select-option>
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

    <a-card title="登录日志列表">
      <a-table
        size="small"
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="{ total, pageSize: 10, showTotal: (t: number) => `共 ${t} 条` }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'result'">
            <a-tag :color="record.result === '成功' ? 'green' : 'red'">{{ record.result }}</a-tag>
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
    </a-card>

    <a-drawer
      v-model:open="detailVisible"
      title="登录日志详情"
      :width="drawerWidth"
    >
      <a-descriptions bordered :column="1" size="small">
        <a-descriptions-item label="用户名">{{ currentDetail?.username }}</a-descriptions-item>
        <a-descriptions-item label="登录IP">{{ currentDetail?.ip }}</a-descriptions-item>
        <a-descriptions-item label="登录地点">{{ currentDetail?.location }}</a-descriptions-item>
        <a-descriptions-item label="设备/浏览器">{{ currentDetail?.device }}</a-descriptions-item>
        <a-descriptions-item label="登录结果">{{ currentDetail?.result }}</a-descriptions-item>
        <a-descriptions-item label="登录时间">{{ currentDetail?.time }}</a-descriptions-item>
      </a-descriptions>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'SettingLoginLog' })

import { ref, reactive, onMounted, computed } from 'vue'
import { EyeOutlined } from '@ant-design/icons-vue'
import { useDrawerWidth } from '@/composables/useDrawerWidth'
import { useUserStore } from '@/stores/user'
import { getLoginLogApi, type LoginLogItem } from '../../../api/log'

const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '登录IP', dataIndex: 'ip', key: 'ip' },
  { title: '登录地点', dataIndex: 'location', key: 'location' },
  { title: '设备/浏览器', dataIndex: 'device', key: 'device' },
  { title: '登录结果', dataIndex: 'result', key: 'result' },
  { title: '登录时间', dataIndex: 'time', key: 'time' },
  { title: '操作', key: 'action', width: 90, align: 'center' as const },
]

const loading = ref(false)
const dataSource = ref<LoginLogItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const currentDetail = ref<LoginLogItem | null>(null)
const { drawerWidth } = useDrawerWidth()
const userStore = useUserStore()
const canRead = computed(() => userStore.hasPermission('login-log:read'))

const searchForm = reactive({
  username: '',
  result: undefined as string | undefined,
  timeRange: [] as { format: (template?: string) => string }[],
})

async function fetchData() {
  loading.value = true
  try {
    const [start, end] = searchForm.timeRange || []
    const res = await getLoginLogApi({
      username: searchForm.username,
      result: searchForm.result,
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
  searchForm.username = ''
  searchForm.result = undefined
  searchForm.timeRange = []
  fetchData()
}

function handleActionMenuClick({ key }: { key: string }, record: LoginLogItem) {
  if (key === 'detail') {
    handleViewDetail(record)
  }
}

function handleViewDetail(record: LoginLogItem) {
  currentDetail.value = record
  detailVisible.value = true
}

onMounted(fetchData)
</script>
