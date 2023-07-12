<template>
  <q-layout view="hhh lpr lff">
    <q-header reveal bordered class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header> v2en </q-item-label>

        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view :user="user" />
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, provide, ref } from 'vue';
import EssentialLink from '../components/EssentialLink.vue';

const linksList = [
  {
    title: 'Github',
    caption: 'github.com/takahashinguyen',
    icon: 'code',
    link: '/',
  },
  {
    title: 'Login',
    link: '/login',
  },
  {
    title: 'Signup',
    link: '/signup',
  },
];

export default defineComponent({
  name: 'MainLayout',

  components: {
    EssentialLink,
  },

  props: {
    userMutation: {
      type: Function,
      required: true,
    },
  },

  async setup(props) {
    const leftDrawerOpen = ref(false);
    const user = await props.userMutation();

    return {
      essentialLinks: linksList,
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      },
      user,
    };
  },
});
</script>
