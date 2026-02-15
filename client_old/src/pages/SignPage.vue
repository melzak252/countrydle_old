<template>
  <v-container class="sign-container">
    <v-card class="login-container">
      <v-card-title>Login</v-card-title>
      <v-form @submit.prevent="submitLogin" class="my-5">
        <v-text-field class="mb-4" v-model="usernameLog" label="Username" type="username" required></v-text-field>
        <v-text-field class="mb-4" v-model="passwordLog" label="Password" type="password" required></v-text-field>
        <v-btn type="submit" color="primary">Login</v-btn>
        <v-alert v-if="errorMessage" type="error">{{ errorMessage }}</v-alert>
      </v-form>
    </v-card>
    <v-card class="register-container">
      <v-card-title>Register</v-card-title>
      <v-form @submit.prevent="submitRegistration" ref="form" class="my-5">
        <v-text-field class="mb-4" v-model="usernameReg" label="Username" required
          :rules="usernameRules"></v-text-field>

        <v-text-field class="mb-4" v-model="email" label="Email" type="email" :rules="emailRules"
          required></v-text-field>
        <v-text-field class="mb-4" v-model="passwordReg" label="Password" type="password" required
          :rules="passwordRules"></v-text-field>
        <v-btn type="submit" color="primary">Register</v-btn>
      </v-form>
    </v-card>

    <fieldset class="google-container" align="center">
      <legend>Google Sign</legend>
      <GoogleLogin class="google-login" :callback="googleLoginCallback" prompt auto-login />
    </fieldset>

  </v-container>
  <CustomPopUp 
      :showPopup="showPopup" 
      @update:showPopup="showPopup = $event" 
      :popUpTitle="popUpTitle" 
      :popUpText="popUpText"
    />
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import { apiService } from '../services/api';
import { useAuthStore } from '../stores/auth';
import CustomPopUp from '../components/CustomPopUp.vue';

export default defineComponent({
  name: 'SignPage',
  components: {
    CustomPopUp: CustomPopUp
  },
  setup() {
    const form = ref(null);
    const email = ref<string>('');
    const usernameReg = ref<string>('');
    const passwordReg = ref<string>('');
    const popUpTitle = ref('');
    const popUpText = ref('');
    const router = useRouter();
    const showPopup = ref<boolean>(false);
    const userLoggedIn = ref<boolean>(false);
    const usernameLog = ref('');
    const passwordLog = ref('');
    const errorMessage = ref('');

    const authStore = useAuthStore();

    const popUp = (title: string, content: string) => {
      showPopup.value = true;
      popUpTitle.value = title;
      popUpText.value = content;
    }

    const submitLogin = async () => {
      await authStore.login({ username: usernameLog.value, password: passwordLog.value });
      if(authStore.isAuth) {
        router.push({ name: 'Home' })
        return;
      }

      popUp(
        'Login failed.',
        authStore.errorMessage
      );

    };

    const googleLoginCallback = async (response: any) => {
      await authStore.googleSignIn(response.credential);
      if(authStore.isAuth) {
        router.push({ name: 'Home'})
        return;
      }
    
      popUp(
        'Login failed.',
        authStore.errorMessage
      );
    }

    const submitRegistration = async () => {
      const isUsernameValid = usernameRules.every(rule => rule(usernameReg.value) === true);
      const isEmailValid = emailRules.every(rule => rule(email.value) === true);
      const isPasswordValid = passwordRules.every(rule => rule(passwordReg.value) === true);
      if (!(isUsernameValid && isEmailValid && isPasswordValid)) {
        showPopup.value = true;
        popUpTitle.value = 'Cannot register user!';
        popUpText.value = 'Please fill in all required fields correctly.';
        userLoggedIn.value = false;
        return
      }

      try {

        let response = await apiService.register({
          email: email.value,
          username: usernameReg.value,
          password: passwordReg.value
        });
        if (response && response.data && response.data.ok) {
          popUp(
            `User: ${usernameReg.value} successfully registered!`,
            `Go to verify your email to login!`
          );
          return;
        }

        const errorDetail = response?.data?.detail || 'Network error or server unreachable';
        popUp(
          'Registration failed.',
          errorDetail
        );
      } catch (error: any) {
        popUp(
          'Registration failed.',
          error.message
        );
      }
    };

    const usernameRules = [
      (v: string): string | boolean => !!v || 'Username is required',
      (v: string): string | boolean => v.length >= 3 || 'Username must be at least 3 characters',
      (v: string): string | boolean => !(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(v)) || 'Username cannot be an email address'

    ];

    const emailRules = [
      (v: string): string | boolean => !!v || 'Email is required',
      (v: string): string | boolean => /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(v) || 'Please enter a valid email address'
    ];

    const passwordRules = [
      (v: string): string | boolean => !!v || 'Password is required',
      (v: string): string | boolean => v.length >= 5 || 'Password must be at least 5 characters long',
      // (v: string): string | boolean => /[A-Z]/.test(v) || 'Password must contain at least one uppercase letter',
      // (v: string): string | boolean => /[a-z]/.test(v) || 'Password must contain at least one lowercase letter',
      (v: string): string | boolean => /[0-9]/.test(v) || 'Password must contain at least one number',
    ];

    return {
      form,
      usernameReg,
      email,
      passwordReg,
      usernameLog,
      passwordLog,
      showPopup,
      popUpText,
      popUpTitle,
      emailRules,
      usernameRules,
      passwordRules,
      errorMessage,
      submitRegistration,
      submitLogin,
      googleLoginCallback,
    };
  },
});
</script>

<style scoped>
.sign-container {
  display: grid;
  grid-template-columns: 50% 50%;
  grid-template-rows: auto 100px;
  column-gap: 20px;
  row-gap: 30px;
}

.register-container,
.login-container {
  padding: 10px !important;
}

.google-container {
  display: flex;
  grid-column: 1 / 3;
  justify-content: center;
  border: none;
  border-top: 1px solid #7c7c7cbc;
  color: #7c7c7cbc;
}

.login-buttons {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 0 !important;
}

.google-login {
  color: black;
  padding-top: 20px;
}

@media (max-width: 600px) {
  .sign-container {
    display: flex;
    flex-direction: column;
  }

  ;
}
</style>