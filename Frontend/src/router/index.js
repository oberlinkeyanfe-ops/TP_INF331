import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../pages/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../pages/Register.vue') },
  { path: '/signout', name: 'SignOut', component: () => import('../pages/SignOut.vue') },
  { path: '/home', name: 'Home', component: () => import('../pages/Home.vue').catch(() => import('../pages/Login.vue')) },
  { path: '/bandes', name: 'BandesList', component: () => import('../pages/BandesList.vue').catch(() => import('../pages/Login.vue')) },
  { path: '/bandes/create', name: 'BandesCreate', component: () => import('../pages/BandesCreate.vue').catch(() => import('../pages/Login.vue')) },
  { path: '/bandes/:id', name: 'Bande', component: () => import('../pages/Bandes.vue').catch(() => import('../pages/Login.vue')) }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
