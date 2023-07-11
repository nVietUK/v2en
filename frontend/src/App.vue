<template>
  <router-view />
</template>

<script lang="ts">
import { useClient } from 'villus';
import { defineComponent } from 'vue';

const graphqlUrl = 'http://[::1]:3000/graphql';

export default defineComponent({
  name: 'App',
  setup() {
    useClient({
      url: graphqlUrl, // your endpoint.
    });
  },
});
</script>
