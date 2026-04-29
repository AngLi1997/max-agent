import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
  },
  {
    path: '/',
    component: () => import('../layouts/BasicLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/dashboard/index.vue'), meta: { title: '仪表盘' } },
      { path: 'model', name: 'Model', component: () => import('../views/model/index.vue'), meta: { title: '模型管理' } },
      { path: 'skill', name: 'Skill', component: () => import('../views/skill/index.vue'), meta: { title: 'Skills 管理' } },
      { path: 'tool', name: 'Tool', component: () => import('../views/tool/index.vue'), meta: { title: '工具管理' } },
      {
        path: 'setting',
        name: 'Setting',
        redirect: '/setting/user',
        meta: { title: '系统设置' },
        children: [
          { path: 'user', name: 'SettingUser', component: () => import('../views/setting/user/index.vue'), meta: { title: '用户管理' } },
          { path: 'role', name: 'SettingRole', component: () => import('../views/setting/role/index.vue'), meta: { title: '角色管理' } },
          { path: 'permission', name: 'SettingPermission', component: () => import('../views/setting/permission/index.vue'), meta: { title: '权限管理' } },
          { path: 'menu', name: 'SettingMenu', component: () => import('../views/setting/menu/index.vue'), meta: { title: '菜单配置' } },
          { path: 'config', name: 'SettingConfig', component: () => import('../views/setting/config/index.vue'), meta: { title: '系统配置' } },
          { path: 'operation-log', name: 'SettingOperationLog', component: () => import('../views/setting/operation-log/index.vue'), meta: { title: '操作日志' } },
          { path: 'login-log', name: 'SettingLoginLog', component: () => import('../views/setting/login-log/index.vue'), meta: { title: '登录日志' } },
        ],
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  if (!userStore.token && to.path !== '/login') {
    return '/login'
  }
  if (userStore.token && to.path === '/login') {
    return '/dashboard'
  }
})

export default router
