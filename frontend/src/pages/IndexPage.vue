<template>
  <div class="row">
    <div class="col"></div>
    <div class="col-6 position-relative">
      <ReadMeViewer :url="link" />
    </div>
    <div class="col"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import ReadMeViewer from '../components/ReadMeViewer.vue';
export default defineComponent({
  name: 'IndexPage',
  components: {
    ReadMeViewer,
  },
  setup() {
    const link =
      'https://raw.githubusercontent.com/TakahashiNguyen/TakahashiNguyen/main/README.md';
    return { link };
  },
});
</script>
