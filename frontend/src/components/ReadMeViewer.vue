<template>
  <div :style="{ height: contentHeight + 'px' }" v-html="content"></div>
</template>

<script lang="ts">
import axios from 'axios';

async function fetchContent(url: string): Promise<string> {
  const response = await axios.get(url);
  return response.data;
}

import { defineComponent, onMounted, ref } from 'vue';

export default defineComponent({
  props: {
    url: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const content = ref('');
    const contentHeight = ref(0);

    onMounted(async () => {
      content.value = await fetchContent(props.url);
      contentHeight.value = document.body.scrollHeight;
    });

    return {
      content,
      contentHeight,
    };
  },
});
</script>
