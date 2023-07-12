import { RouteRecordRaw } from 'vue-router';
import useAuth from '../script/useAuth';

const { isLoggedIn } = useAuth();

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('../pages/IndexPage.vue') },
      {
        path: '/profile',
        component: () => import('../pages/UserPage.vue'),
        beforeEnter: (to, from, next) => {
          if (isLoggedIn.value) {
            next();
          } else {
            next('/login');
          }
        },
        props: true,
      },
      {
        path: '/login',
        component: () => import('../pages/LogIn.vue'),
        beforeEnter: (to, from, next) => {
          const previousProps = from.params;
          to.params = previousProps;

          isLoggedIn.value ? next('/profile') : next();
        },
      },
      {
        path: '/signup',
        component: () => import('../pages/SignUp.vue'),
        beforeEnter: (to, from, next) => {
          const previousProps = from.params;
          to.params = previousProps;

          isLoggedIn.value ? next('/profile') : next();
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
