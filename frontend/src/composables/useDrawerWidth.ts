import { ref, onMounted, onUnmounted } from 'vue'

export function useDrawerWidth() {
  const drawerWidth = ref(getWidth())

  function getWidth() {
    const w = window.innerWidth
    if (w <= 768) return '100%'
    if (w <= 1200) return '50%'
    return 520
  }

  function onResize() {
    drawerWidth.value = getWidth()
  }

  onMounted(() => window.addEventListener('resize', onResize))
  onUnmounted(() => window.removeEventListener('resize', onResize))

  return { drawerWidth }
}
