import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import './styles.css';
import { session } from './lib/api';

const routes = [
  { path: '/login', component: () => import('./pages/Login.vue'), meta: { public: true } },
  { path: '/', component: () => import('./pages/Home.vue') },
  { path: '/work/planner', component: () => import('./pages/Planner.vue') },
  { path: '/work/engineer', component: () => import('./pages/Engineer.vue') },
  { path: '/work/operator', component: () => import('./pages/Operator.vue') },
  { path: '/work/quality', component: () => import('./pages/Quality.vue') },
  { path: '/work/manager', component: () => import('./pages/Manager.vue') },
  { path: '/3d', component: () => import('./pages/Factory3D.vue') },
  { path: '/teach', component: () => import('./pages/Teach.vue') },
  { path: '/bus', component: () => import('./pages/BusView.vue') },
  { path: '/:p(.*)*', redirect: '/' },
];

const router = createRouter({ history: createWebHistory(), routes });
router.beforeEach((to) => {
  if (!to.meta.public && !session.token) return { path: '/login', query: { next: to.fullPath } };
  return true;
});

createApp(App).use(router).mount('#app');
