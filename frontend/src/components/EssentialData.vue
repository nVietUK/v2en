<template>
  <q-item clickable tag="a" target="_blank" @click="eFunction()">
    <q-item-section v-if="icon" avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ origin + ' >> ' + translated }}</q-item-label>
      <q-item-label caption>{{
        'translator: ' + translator + ' verified: ' + verified
      }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import router from 'src/router';

export default defineComponent({
  props: {
    origin: {
      type: String,
      default: '',
    },

    translated: {
      type: String,
      default: '',
    },

    translator: {
      type: String,
      default: '',
    },

    verified: {
      type: Boolean,
      default: false,
    },

    eFunction: {
      type: Function,
      default: () => router.push('/view'),
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
