<template>
  <Suspense>
    <router-view
      :userMutation="userMutation"
      :logoutMutation="logoutMutation"
    />
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

const LOGOUT_MUTATION = gql`
  mutation LogOut($username: String!, $token: String!) {
    LogOut(username: $username, token: $token)
  }
`;

export default defineComponent({
  name: 'App',
  methods: {
    async userMutation(token: string) {
      const { execute } = useMutation(TOKEN_MUTATION, {});
      try {
        const response = await execute({ token: token });
        return response.data.checkToken;
      } catch (error) {
        return '';
      }
    },
    async logoutMutation(username: string, token: string) {
      const { execute } = useMutation(LOGOUT_MUTATION, {});
      await execute({ username: username, token: token });
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
