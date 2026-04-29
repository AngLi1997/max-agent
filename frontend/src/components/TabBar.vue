<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTabStore } from '../stores/tab'

const router = useRouter()
const tabStore = useTabStore()

const contextMenu = ref({ visible: false, x: 0, y: 0, path: '' })

function onTabClick(path: string) {
  tabStore.activeTab = path
  router.push(path)
}

function onClose(path: string, e: Event) {
  e.stopPropagation()
  tabStore.removeTab(path, router)
  tabStore.updateCachedNames()
}

function onContextMenu(e: MouseEvent, path: string) {
  e.preventDefault()
  contextMenu.value = { visible: true, x: e.clientX, y: e.clientY, path }
}

function closeContextMenu() {
  contextMenu.value.visible = false
}

function handleContextAction(action: string) {
  const path = contextMenu.value.path
  switch (action) {
    case 'closeCurrent': tabStore.removeTab(path, router); break
    case 'closeLeft': tabStore.closeLeft(path); break
    case 'closeRight': tabStore.closeRight(path); break
    case 'closeOthers': tabStore.closeOthers(path); break
    case 'closeAll': tabStore.closeAll(router); break
  }
  tabStore.updateCachedNames()
  closeContextMenu()
}
</script>

<template>
  <div class="tab-bar" @click="closeContextMenu">
    <div class="tab-bar-scroll">
      <div
        v-for="tab in tabStore.tabs"
        :key="tab.path"
        class="tab-item"
        :class="{ active: tabStore.activeTab === tab.path }"
        @click="onTabClick(tab.path)"
        @contextmenu="onContextMenu($event, tab.path)"
      >
        <span class="tab-title">{{ tab.title }}</span>
        <span class="tab-close" @click="onClose(tab.path, $event)">&times;</span>
      </div>
    </div>
    <teleport to="body">
      <div
        v-if="contextMenu.visible"
        class="tab-context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      >
        <div class="menu-item" @click="handleContextAction('closeCurrent')">关闭当前</div>
        <div class="menu-item" @click="handleContextAction('closeLeft')">关闭左侧</div>
        <div class="menu-item" @click="handleContextAction('closeRight')">关闭右侧</div>
        <div class="menu-item" @click="handleContextAction('closeOthers')">关闭其他</div>
        <div class="menu-item" @click="handleContextAction('closeAll')">关闭全部</div>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
.tab-bar {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 4px 8px 0;
}
.tab-bar-scroll {
  display: flex;
  overflow-x: auto;
  gap: 4px;
}
.tab-bar-scroll::-webkit-scrollbar { height: 0; }
.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #f0f0f0;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  white-space: nowrap;
  font-size: 13px;
  color: #666;
  background: #fafafa;
  transition: all 0.2s;
}
.tab-item:hover { color: #1890ff; background: #e6f7ff; }
.tab-item.active {
  color: #1890ff;
  background: #fff;
  border-color: #d9d9d9;
  border-bottom-color: #fff;
}
.tab-close {
  font-size: 14px;
  line-height: 1;
  color: #999;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tab-close:hover { background: #ddd; color: #333; }
.tab-context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 1050;
  padding: 4px 0;
}
.menu-item {
  padding: 6px 16px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}
.menu-item:hover { background: #e6f7ff; color: #1890ff; }
</style>
