<template>
  <div class="user-profile">
    <div class="user-info">
      <h2>{{ data.translator }}</h2>
      <p>Origin: {{ data.origin }}</p>
      <p>Translated: {{ data.translated }}</p>
    </div>
  </div>
</template>

<script lang="ts">
import gql from 'graphql-tag';
import router from 'src/router';
import { useQuery } from 'villus';
import { defineComponent } from 'vue';

const GET_DATA = gql`
  query Data($dataId: Float!) {
    data(id: $dataId) {
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
  props: {
    id: {
      type: Number,
      required: true,
    },
    user: {
      type: [Object, String],
      required: true,
    },
  },
  async setup(props) {
    if (!props.user) router.push('/login');

    const { execute } = useQuery({
      query: GET_DATA,
      variables: {
        dataId: props.id,
      },
    });

    const { error, data } = await execute();

    return { error: error, data: data.data };
  },
});
</script>
