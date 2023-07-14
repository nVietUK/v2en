<template>
  <q-list>
    <EssentialData
      v-for="link in essentialLinks"
      :key="link.title"
      v-bind="link"
    />
  </q-list>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import EssentialData from '../components/EssentialData.vue';
import router from 'src/router';
import gql from 'graphql-tag';
import { useMutation } from 'villus';

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
    user: {
      type: [Object, String],
      required: true,
    },
  },

  async setup(props) {
    if (!props.user) router.push('/login');

    const { execute } = useMutation(DATAS_QUERY);
    const linksList = (await execute()).data.datas;

    return {
      essentialLinks: linksList,
    };
  },
});
</script>
