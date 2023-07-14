<template>
  <q-item clickable tag="a" target="_blank" @click="eFunction($props.id)">
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
    id: {
      type: Number,
      required: true,
    },

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
      default: (id: number) => router.push('/datas/' + id),
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
