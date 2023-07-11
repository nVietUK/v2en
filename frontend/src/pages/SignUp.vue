<template>
  <q-page class="justify-center">
    <div class="account-page center-of-parent">
      <div class="account-form">
        <h1 class="account-title">Create an account</h1>
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
          <div class="form-group row">
            <div class="col">
              <label for="first-name" class="form-label">First Name</label>
              <input
                id="first-name"
                v-model="firstName"
                type="text"
                class="form-control"
                required
              />
            </div>
            <div class="col">
              <label for="last-name" class="form-label">Last Name</label>
              <input
                id="last-name"
                v-model="lastName"
                type="text"
                class="form-control"
                required
              />
            </div>
          </div>
          <div class="form-group row">
            <div class="col">
              <label for="birthday" class="form-label">Birthday</label>
              <input
                id="birthday"
                v-model="birthday"
                type="date"
                class="form-control"
                required
              />
            </div>
            <div class="col">
              <label for="gender" class="form-label">Gender</label>
              <select
                id="gender"
                v-model="gender"
                class="form-control"
                required
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
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
          <button type="submit" class="btn btn-primary btn-block">
            Sign up
          </button>
        </form>
      </div>
    </div>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useMutation } from 'villus';
import gql from 'graphql-tag';

const SIGN_UP_MUTATION = gql`
  mutation AddUser($newUser: UserInput!) {
    addUser(newUser: $newUser) {
      username
      familyName
      givenName
      gender
      birthDay
    }
  }
`;

export default defineComponent({
  setup() {
    const email = ref('');
    const username = ref('');
    const password = ref('');
    const terms = ref(false);
    const firstName = ref('');
    const lastName = ref('');
    const gender = ref('');
    const birthday = ref('');

    const { data, execute } = useMutation(SIGN_UP_MUTATION);

    const submitForm = async () => {
      try {
        const variables = {
          newUser: {
            username: username.value,
            familyName: lastName.value,
            givenName: firstName.value,
            gender: gender.value,
            birthDay: birthday.value,
            password: password.value,
          },
        };
        await execute(variables);

        console.log(data.value.addUser);
      } catch (error) {
        console.error(error);
      }
    };

    return {
      email,
      username,
      password,
      terms,
      firstName,
      lastName,
      gender,
      birthday,
      submitForm,
    };
  },
});
</script>
