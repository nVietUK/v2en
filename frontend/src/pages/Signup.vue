<template>
  <div>
    <q-form @submit.prevent="submitForm">
      <q-input
        v-model="name"
        label="Name"
        :rules="[(val) => !!val || 'Name is required']"
      />
      <q-input
        v-model="email"
        label="Email"
        type="email"
        :rules="[
          (val) => !!val || 'Email is required',
          (val) => emailRegex.test(val) || 'Invalid email',
        ]"
      />
      <q-input
        v-model="password"
        label="Password"
        type="password"
        :rules="[(val) => !!val || 'Password is required']"
      />
      <q-input
        v-model="passwordConfirm"
        label="Confirm Password"
        type="password"
        :rules="[
          (val) => !!val || 'Confirm password is required',
          (val) => val === password || 'Passwords do not match',
        ]"
      />
      <q-btn type="submit" label="Sign Up" />
    </q-form>
  </div>
</template>

<script>
import client from '../villus';
import { gql } from 'graphql-tag';

const SignUpMutation = gql`
  mutation Signup($name: String!, $email: String!, $password: String!) {
    signup(name: $name, email: $email, password: $password) {
      id
    }
  }
`;

export default {
  name: 'Sign-up',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      passwordConfirm: '',
    };
  },
  methods: {
    async submitForm() {
      try {
        // Call the signup mutation with Villus and pass in user data as variables
        const { data } = await client.executeMutation(SignUpMutation, {
          name: this.name,
          email: this.email,
          password: this.password,
        });
        // Handle the response from the server, e.g. redirect to the dashboard
        console.log(data);
      } catch (error) {
        // Handle any error messages from the server
        console.error(error);
      }
    },
  },
  computed: {
    emailRegex() {
      // Regular expression for email validation
      return /.+@.+\..+/;
    },
  },
};
</script>
