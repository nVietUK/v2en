<template>
  <q-list v-if="$route.path === '/datas'">
    <EssentialData
      v-for="link in essentialLinks"
      :key="link.title"
      v-bind="link"
    />
  </q-list>

  <router-view :user="$props.user" :id="id" />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import EssentialData from '../components/EssentialData.vue';
import router from 'src/router';
import gql from 'graphql-tag';
import { useQuery } from 'villus';

const DATAS_QUERY = gql`
  query Query {
    datas {
      id
      origin
      translated
      translator
      hashValue
      verified
    }
  }
`;

export default defineComponent({
  components: {
    EssentialData,
  },

  props: {
    id: { type: Number },

    user: {
      type: [Object, String],
      required: true,
    },

    data: {
      type: [Object],
    },
  },

  async setup(props) {
    if (!props.user) router.push('/login');

    const { execute } = useQuery({ query: DATAS_QUERY });
    const linksList = (await execute()).data.datas;

    return {
      essentialLinks: linksList,
    };
  },
});
</script>
