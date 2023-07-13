<template>
  <div class="user-profile">
    <div class="user-info">
      <h2>{{ userDisplay.name }}</h2>
      <p>Birthday: {{ userDisplay.birthday }}</p>
      <p>Gender: {{ userDisplay.gender }}</p>
    </div>
  </div>
</template>

<script lang="ts">
import router from 'src/router';
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    user: {
      type: [Object, String],
      required: true,
    },
  },
  setup(props) {
    if (!props['user']) router.push('/login');

    return {
      userDisplay: {
        name: props.user['username'],
        birthday: props.user['birthDay'],
        gender: props.user['gender'],
      },
    };
  },
});
</script>
