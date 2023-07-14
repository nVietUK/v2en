<template>
  <div>
    <div v-if="error">{{ error.message }}</div>
    <div v-else>
      <div v-for="item in data" :key="item.id">{{ item.name }}</div>
    </div>
  </div>
</template>

<script lang="ts">
import gql from 'graphql-tag';
import router from 'src/router';
import { useMutation, useQuery } from 'villus';
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
    },
    user: {
      type: [Object, String],
      required: true,
    },
  },
  async setup(props) {
    if (!props['user']) router.push('/login');

    const { execute } = useQuery({
      query: GET_DATA,
      variables: {
        dataId: props.id,
      },
    });

    return {
      ...(await execute()),
    };
  },
});
</script>
