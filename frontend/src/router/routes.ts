import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('../pages/IndexPage.vue') },
      {
        path: '/profile',
        component: () => import('../pages/UserPage.vue'),
      },
      {
        path: '/login',
        component: () => import('../pages/LogIn.vue'),
      },
      {
        path: '/signup',
        component: () => import('../pages/SignUp.vue'),
      },
    ],
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('../pages/ErrorNotFound.vue'),
  },
];

export default routes;
