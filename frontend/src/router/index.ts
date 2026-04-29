import { createRouter, createWebHistory } from 'vue-router'
import { defineComponent, h } from 'vue'

const EmptyView = defineComponent({
  name: 'EmptyView',
  setup() {
    return () => h('div')
  },
})

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: EmptyView,
    },
  ],
})

export default router
