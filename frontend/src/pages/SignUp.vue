<template>
  <q-page>
    <q-form @submit.prevent="submitForm">
      <q-input v-model="email" label="Email" type="email" required />
      <q-input v-model="username" label="Username" type="text" required />
      <q-input v-model="password" label="Password" type="password" required />
      <q-checkbox
        v-model="terms"
        label="I agree to the terms and conditions"
        required
      />
      <q-btn type="submit" label="Sign up" />
    </q-form>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useMutation } from 'villus';
import gql from 'graphql-tag';

const SIGN_UP_MUTATION = gql`
  mutation signUp($username: String!, $email: String!, $password: String!) {
    signUp(username: $username, email: $email, password: $password) {
      username
      email
    }
  }
`;

export default defineComponent({
  setup() {
    const email = ref('');
    const username = ref('');
    const password = ref('');
    const terms = ref(false);

    const { data, execute } = useMutation(SIGN_UP_MUTATION);

    const submitForm = async () => {
      try {
        const variables = {
          email: email.value,
          username: username.value,
          password: password.value,
        };
        execute(variables);
      } catch (error) {
        console.error(error);
      }
    };

    return {
      email,
      username,
      password,
      terms,
      submitForm,
    };
  },
});
</script>
