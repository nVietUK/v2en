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
        beforeEnter: async (to, from, next) => {
          localStorage.getItem('token') ? next() : next('/login');
        },
        props: true,
      },
      {
        path: '/login',
        component: () => import('../pages/LogIn.vue'),
        beforeEnter: async (to, from, next) => {
          localStorage.getItem('token') ? next('/profile') : next();
        },
      },
      {
        path: '/signup',
        component: () => import('../pages/SignUp.vue'),
        beforeEnter: async (to, from, next) => {
          localStorage.getItem('token') ? next('/profile') : next();
        },
      },
    ],
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('../pages/ErrorNotFound.vue'),
  },
];

export default routes;
