<template>
  <router-view />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useClient } from 'villus';

export default defineComponent({
  name: 'App',
});

useClient({
  url: 'http://[::1]:3000', // your endpoint.
});
</script>
