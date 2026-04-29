<script setup lang="ts">
defineOptions({ name: 'Dashboard' })

import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import {
  UserOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  ToolOutlined,
} from '@ant-design/icons-vue'
import { getStatsApi, getTrendApi } from '../../api/dashboard'
import type { DashboardStats, TrendItem } from '../../api/dashboard'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const stats = ref<DashboardStats>({ userCount: 0, modelCount: 0, skillCount: 0, toolCount: 0 })
const trend = ref<TrendItem[]>([])

const chartOption = ref({})

onMounted(async () => {
  stats.value = await getStatsApi()
  trend.value = await getTrendApi()
  chartOption.value = {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: trend.value.map((t) => t.date) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: trend.value.map((t) => t.value), smooth: true, areaStyle: {} }],
  }
})
</script>

<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 24px;">
      <a-col :span="6">
        <a-card>
          <a-statistic title="用户数" :value="stats.userCount">
            <template #prefix><UserOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="模型数" :value="stats.modelCount">
            <template #prefix><RobotOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="Skills 数" :value="stats.skillCount">
            <template #prefix><ThunderboltOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="工具数" :value="stats.toolCount">
            <template #prefix><ToolOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>
    <a-card title="近 7 天趋势">
      <v-chart :option="chartOption" style="height: 300px;" autoresize />
    </a-card>
  </div>
</template>
