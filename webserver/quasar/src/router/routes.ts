import { RouteRecordRaw } from 'vue-router';
import { NestFactory } from '@nestjs/core';
import { AppModule } from '../app.module';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/IndexPage.vue') }],
  },
  {
    path: '/graphql',
    component: () => NestFactory.create(AppModule)
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
