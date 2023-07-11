<template>
  <router-view />
</template>

<script lang="ts">
import { useClient } from 'villus';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'App',
  setup() {
    useClient({
      url: '/graphql', // your endpoint.
    });
  },
});
</script>
