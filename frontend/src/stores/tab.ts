import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import type { RouteLocationNormalized } from 'vue-router'

export interface TabItem {
  path: string
  title: string
  name: string
}

export const useTabStore = defineStore('tab', () => {
  const tabs = ref<TabItem[]>([])
  const activeTab = ref('')

  function addTab(route: RouteLocationNormalized) {
    const title = (route.meta?.title as string) || route.path
    const name = (route.name as string) || ''
    if (!name) return
    const exists = tabs.value.find(t => t.path === route.path)
    if (!exists) {
      tabs.value.push({ path: route.path, title, name })
    }
    activeTab.value = route.path
  }

  function removeTab(path: string, router: ReturnType<typeof useRouter>) {
    const idx = tabs.value.findIndex(t => t.path === path)
    if (idx === -1) return
    tabs.value.splice(idx, 1)
    if (activeTab.value === path) {
      const next = tabs.value[idx] || tabs.value[idx - 1]
      if (next) {
        activeTab.value = next.path
        router.push(next.path)
      }
    }
  }

  function closeLeft(path: string) {
    const idx = tabs.value.findIndex(t => t.path === path)
    if (idx > 0) tabs.value.splice(0, idx)
  }

  function closeRight(path: string) {
    const idx = tabs.value.findIndex(t => t.path === path)
    if (idx < tabs.value.length - 1) tabs.value.splice(idx + 1)
  }

  function closeOthers(path: string) {
    tabs.value = tabs.value.filter(t => t.path === path)
  }

  function closeAll(router: ReturnType<typeof useRouter>) {
    tabs.value = []
    activeTab.value = ''
    router.push('/dashboard')
  }

  const cachedNames = ref<string[]>([])
  function updateCachedNames() {
    cachedNames.value = tabs.value.map(t => t.name).filter(Boolean)
  }

  function syncRoute(route: RouteLocationNormalized) {
    if (route.path === '/login') return
    addTab(route)
    updateCachedNames()
  }

  return {
    tabs, activeTab, cachedNames,
    addTab, removeTab, closeLeft, closeRight, closeOthers, closeAll, updateCachedNames, syncRoute,
  }
})
