<template>
  <q-page>
    <q-form @submit.prevent="submitForm">
      <q-input
        v-model="emailOrUsername"
        label="Email or Username"
        type="text"
        required
      />
      <q-input v-model="password" label="Password" type="password" required />
      <q-btn type="submit" label="Login" />
    </q-form>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import gql from 'graphql-tag';
import { useMutation } from 'villus';
import { client } from 'src/App.vue';

const LOGIN_MUTATION = gql`
  mutation signUp($username: String!, $email: String!, $password: String!) {
    signUp(username: $username, email: $email, password: $password) {
      username
      email
    }
  }
`;

export default defineComponent({
  name: 'LoginPage',
  setup() {
    const emailOrUsername = ref('');
    const password = ref('');

    const { data, execute } = useMutation(LOGIN_MUTATION);

    const submitForm = async () => {
      try {
        const variables = {
          emailOrUsername: emailOrUsername.value,
          password: password.value,
        };
        execute(variables);
      } catch (error) {
        console.error(error);
      }
    };

    return {
      emailOrUsername,
      password,
      submitForm,
    };
  },
});
</script>
