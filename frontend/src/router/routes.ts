import { route } from 'quasar/wrappers';
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
      {
        path: '/datas',
        component: () => import('../pages/DatasPage.vue'),
        children: [
          {
            path: ':id',
            name: 'dataViewer',
            component: () => import('../pages/DataView.vue'),
          },
        ],
        props: (route) => ({ id: Number(route.params.id) }),
      },
    ],
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('../pages/ErrorNotFound.vue'),
  },
];

export default routes;
