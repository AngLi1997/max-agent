import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

export function useTableScrollY(minHeight = 240) {
  const tableSectionRef = ref<HTMLElement | null>(null)
  const scrollY = ref(minHeight)
  let resizeObserver: ResizeObserver | null = null
  let observedElement: HTMLElement | null = null
  let frameId = 0

  const bindObserver = (element: HTMLElement | null) => {
    if (!resizeObserver) {
      return
    }

    if (observedElement) {
      resizeObserver.unobserve(observedElement)
    }

    observedElement = element

    if (observedElement) {
      resizeObserver.observe(observedElement)
    }
  }

  const updateScrollY = () => {
    cancelAnimationFrame(frameId)
    frameId = requestAnimationFrame(() => {
      nextTick(() => {
        const section = tableSectionRef.value
        if (!section) {
          return
        }

        const tableWrapper = section.querySelector<HTMLElement>('.ant-table-wrapper')
        const tableHeader = tableWrapper?.querySelector<HTMLElement>('.ant-table-thead')
        const pagination = tableWrapper?.querySelector<HTMLElement>('.ant-pagination')
        const sectionStyle = window.getComputedStyle(section)
        const sectionPaddingTop = Number.parseFloat(sectionStyle.paddingTop || '0')
        const sectionPaddingBottom = Number.parseFloat(sectionStyle.paddingBottom || '0')
        const paginationStyle = pagination ? window.getComputedStyle(pagination) : null
        const paginationMarginTop = paginationStyle
          ? Number.parseFloat(paginationStyle.marginTop || '0')
          : 0
        const paginationMarginBottom = paginationStyle
          ? Number.parseFloat(paginationStyle.marginBottom || '0')
          : 0

        const availableHeight =
          section.clientHeight -
          sectionPaddingTop -
          sectionPaddingBottom -
          (tableHeader?.offsetHeight ?? 0) -
          (pagination?.offsetHeight ?? 0) -
          paginationMarginTop -
          paginationMarginBottom

        scrollY.value = Math.max(minHeight, availableHeight)
      })
    })
  }

  onMounted(() => {
    resizeObserver = new ResizeObserver(updateScrollY)
    bindObserver(tableSectionRef.value)
    updateScrollY()
    window.addEventListener('resize', updateScrollY)
  })

  watch(tableSectionRef, (element) => {
    bindObserver(element)
    updateScrollY()
  })

  onBeforeUnmount(() => {
    cancelAnimationFrame(frameId)
    window.removeEventListener('resize', updateScrollY)

    if (resizeObserver && observedElement) {
      resizeObserver.unobserve(observedElement)
    }

    resizeObserver?.disconnect()
    observedElement = null
  })

  return {
    tableSectionRef,
    tableScrollY: computed(() => scrollY.value),
    updateTableScrollY: updateScrollY,
  }
}
