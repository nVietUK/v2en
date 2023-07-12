<template>
  <Suspense>
    <router-view />
  </Suspense>
</template>

<script lang="ts">
import { cache, fetch, useClient } from 'villus';
import { defineComponent } from 'vue';

const graphqlUrl = 'http://[::1]:3000/graphql';

export default defineComponent({
  name: 'App',
  setup() {
    useClient({
      url: graphqlUrl, // your endpoint.
      use: [cache(), fetch()],
    });
  },
});
</script>
