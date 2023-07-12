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
          :user="user"
        />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import EssentialLink from '../components/EssentialLink.vue';
import gql from 'graphql-tag';
import { useMutation } from 'villus';

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

const TOKEN_MUTATION = gql`
  mutation CheckToken($token: String!) {
    checkToken(token: $token) {
      username
      familyName
      givenName
      gender
      birthDay
      token
    }
  }
`;

export default defineComponent({
  name: 'MainLayout',

  components: {
    EssentialLink,
  },

  async setup() {
    const leftDrawerOpen = ref(false);
    const { error, execute } = useMutation(TOKEN_MUTATION, {});
    const variables = {
      token: localStorage.getItem('token'),
    };

    const fetchData = async () => {
      try {
        const response = await execute(variables);
        return response.data.checkToken;
      } catch (error) {
        console.error(error);
      }
    };

    const user = await fetchData();

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
