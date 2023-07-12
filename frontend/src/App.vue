<template>
  <Suspense>
    <router-view :userMutation="userMutation" />
  </Suspense>
</template>

<script lang="ts">
import { cache, fetch, useClient } from 'villus';
import { defineComponent } from 'vue';
import gql from 'graphql-tag';
import { useMutation } from 'villus';

const graphqlUrl = 'http://[::1]:3000/graphql';

const TOKEN_MUTATION = gql`
  mutation CheckToken($token: String!) {
    checkToken(token: $token) {
      username
      familyName
      givenName
      gender
      birthDay
      token
    }
  }
`;
const variables = {
  token: localStorage.getItem('token'),
};
export default defineComponent({
  name: 'App',
  methods: {
    async userMutation() {
      const { execute } = useMutation(TOKEN_MUTATION, {});
      try {
        const response = await execute(variables);
        return response.data.checkToken;
      } catch (error) {
        return '';
      }
    },
  },
  setup() {
    useClient({
      url: graphqlUrl,
      use: [cache(), fetch()],
    });
  },
});
</script>
