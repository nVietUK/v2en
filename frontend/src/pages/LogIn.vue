<template>
  <q-page class="justify-center">
    <div class="login-page center-of-parent">
      <div class="login-form">
        <h1 class="login-title">Welcome back!</h1>
        <h2 class="login-subtitle">We're so excited to see you again!</h2>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label for="emailOrUsername" class="form-label"
              >Email or Phone</label
            >
            <input
              id="emailOrUsername"
              v-model="emailOrUsername"
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
          <button type="submit" class="btn btn-primary btn-block">Login</button>
        </form>
        <div class="forgot-password">
          <a href="#">Forgot your password?</a>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import gql from 'graphql-tag';
import { useMutation } from 'villus';

const LOGIN_MUTATION = gql`
  mutation Login($emailOrUsername: String!, $password: String!) {
    login(emailOrUsername: $emailOrUsername, password: $password) {
      token
    }
  }
`;

export default defineComponent({
  name: 'LoginPage',
  setup() {
    const emailOrUsername = ref('');
    const password = ref('');

    const { data, execute } = useMutation(LOGIN_MUTATION, {});

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
