<template>
  <q-item clickable tag="a" target="_blank" @click="eFunction()">
    <q-item-section v-if="icon" avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ title }}</q-item-label>
      <q-item-label caption>{{ caption }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import router from 'src/router';

export default defineComponent({
  name: 'EssentialLink',
  props: {
    title: {
      type: String,
      required: true,
    },

    caption: {
      type: String,
      default: '',
      optional: true,
    },

    eFunction: {
      type: Function,
      default: () => router.push('/'),
      optional: true,
    },

    icon: {
      type: String,
      default: '',
      optional: true,
    },
  },
});
</script>
