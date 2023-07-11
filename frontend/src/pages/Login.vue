<template>
  <q-page class="justify-center">
    <div id="login" class="discord-login center-of-parent">
      <div class="discord-login-header">
        <h1>Sign In</h1>
      </div>
      <div class="form-inputs self-center">
        <label for="username">Email or Phone</label>
        <input
          type="text"
          id="username"
          name="username"
          v-model="input.username"
          placeholder="Email or Phone"
        />
      </div>
      <div class="form-inputs">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          v-model="input.password"
          placeholder="Password"
        />
      </div>
      <div class="discord-login-footer">
        <button type="button" v-on:click="login()">Login</button>
        <a href="#">Forgot your password?</a>
      </div>
    </div>
  </q-page>
</template>

<script>
export default {
  name: 'Login-ui',
  data() {
    return {
      input: {
        username: '',
        password: '',
      },
    };
  },
  methods: {
    login() {
      if (this.input.username != '' && this.input.password != '') {
        // This should actually be an api call not a check against this.$parent.mockAccount
        if (
          this.input.username == this.$parent.mockAccount.username &&
          this.input.password == this.$parent.mockAccount.password
        ) {
          this.$emit('authenticated', true);
          this.$router.replace({ name: 'Secure' });
        } else {
          console.log('The username and / or password is incorrect');
        }
      } else {
        console.log('A username and password must be present');
      }
    },
  },
};
</script>

<style>
.center-of-parent {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.discord-login {
  background-color: #36393f;
  border-radius: 5px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  width: 400px;
}

.discord-login-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.discord-login-header img {
  height: 50px;
  margin-right: 10px;
  width: 50px;
}

.discord-login-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.form-inputs {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  width: 100%;
}

.form-inputs label {
  font-size: 14px;
  margin-bottom: 5px;
}

.form-inputs input {
  background-color: #40444b;
  border: none;
  border-radius: 3px;
  color: #fff;
  font-size: 16px;
  padding: 10px;
}

.discord-login-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.discord-login-footer button {
  background-color: #7289da;
  border: none;
  border-radius: 3px;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  padding: 10px 20px;
  transition: background-color 0.2s ease-in-out;
}

.discord-login-footer button:hover {
  background-color: #677bc4;
}

.discord-login-footer a {
  color: #b9bbbe;
  font-size: 14px;
  text-decoration: none;
}
</style>
