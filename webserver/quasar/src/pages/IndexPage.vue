<template>
  <div class="row">
    <div class="col"></div>
    <div class="col-6 position-relative">
      <iframe
        id="my-iframe"
        src="https://htmlpreview.github.io/?https://raw.githubusercontent.com/TakahashiNguyen/TakahashiNguyen/main/README.md"
        style="width: 100%; border: none"
        onload="resizeIframe"
      ></iframe>
    </div>
    <div class="col"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

async function fetchContent() {
  const url = 'https://example.com/content-to-copy';

  const response = await fetch(url);
  const html = await response.text();

  const container = document.createElement('div');
  container.innerHTML = html;

  const content = container.querySelector('#content-to-copy');

  if (content) {
    const height = content. | 0;
    content.style.height = height + 'px';

    return content.outerHTML;
  }
}

export default defineComponent({
  name: 'IndexPage',
  setup() {
    return {fetchContent()}
  }
})
</script>
