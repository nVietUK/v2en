<template>
  <div class="user-profile">
    <div class="user-info">
      <h2>{{ user.name }}</h2>
      <p>Birthday: {{ user.birthday }}</p>
      <p>Gender: {{ user.gender }}</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    User: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    return {
      user: {
        name: props.User.name,
        birthday: props.User.birthday,
        gender: props.User.gender,
      },
    };
  },
});
</script>
