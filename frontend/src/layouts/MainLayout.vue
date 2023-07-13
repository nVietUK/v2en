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
import { defineComponent, ref } from 'vue';
import EssentialLink from '../components/EssentialLink.vue';
import router from 'src/router';

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
    logoutMutation: {
      type: Function,
      required: true,
    },
  },

  async setup(props) {
    const leftDrawerOpen = ref(false);
    const user = await props.userMutation(localStorage.getItem('token'));

    const userLinks =
      user instanceof Object
        ? [
            {
              title: 'Profile',
              eFunction: () => {
                router.push({ path: '/profile' });
              },
            },
            {
              title: 'LogOut',
              eFunction: async () => {
                localStorage.removeItem('token');
                await props.logoutMutation(user['username'], user['token']);
                window.location.reload();
              },
            },
          ]
        : [
            {
              title: 'Login',
              eFunction: () => {
                router.push({ path: '/login' });
              },
            },
            {
              title: 'Signup',
              eFunction: () => {
                router.push({ path: '/signup' });
              },
            },
          ];

    const linksList = [
      {
        title: 'Github',
        caption: 'github.com/takahashinguyen',
        icon: 'code',
      },
      ...userLinks,
    ];

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
