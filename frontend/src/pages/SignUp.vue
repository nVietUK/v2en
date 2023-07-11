<template>
  <div class="signup-page">
    <div class="signup-form">
      <h1 class="signup-title">Create an account</h1>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="email" class="form-label">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-control"
            required
          />
        </div>
        <div class="form-group">
          <label for="username" class="form-label">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="form-control"
            required
          />
        </div>
        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            required
          />
        </div>
        <div class="form-group">
          <div class="form-check">
            <input
              id="terms"
              v-model="terms"
              type="checkbox"
              class="form-check-input"
              required
            />
            <label for="terms" class="form-check-label">
              I agree to the terms and conditions
            </label>
          </div>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Sign up</button>
      </form>
    </div>
  </div>
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
