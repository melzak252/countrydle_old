<template>
    <v-container class="account-container">
        <v-card class="mt-3 account-card">
            <v-card-title>My Account</v-card-title>
            <v-card-text>
                <v-form ref="form" v-model="validUser">
                    <v-text-field label="Username" prepend-icon="mdi-account" v-model="user.username"
                        variant="underlined" required></v-text-field>
                    <v-text-field label="Email" variant="underlined" prepend-icon="mdi-email" v-model="user.email"
                        required></v-text-field>
                </v-form>
            </v-card-text>
            <v-card-actions>
                <v-btn color="primary" :disabled="!validUser" @click="updateAccount">
                    Save Changes
                </v-btn>
            </v-card-actions>
        </v-card>
        <v-card class="mt-3 account-card">
            <v-card-title>Password change</v-card-title>
            <v-card-text>
                <v-text-field l abel="Password" prepend-icon="mdi-lock"
                    :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'" :type="showPassword ? 'text' : 'password'"
                    @click:append="toggleShowPassword" variant="underlined" v-model="pass1" :rules="passwordRules"
                    label="New password" required></v-text-field>

                <v-text-field l abel="Password" prepend-icon="mdi-lock"
                    :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'" :type="showPassword ? 'text' : 'password'"
                    @click:append="toggleShowPassword" variant="underlined" v-model="pass2" :rules="passwordRules"
                    label="Repeat new password" required></v-text-field>
            </v-card-text>
            <v-card-actions class="act-btn-box">
                <v-btn class="password-btn" color="primary" @click="changePassword">
                    Change password
                </v-btn>
            </v-card-actions>
        </v-card>
        <v-card class="my-countrydle-history">
            <v-card-title>My Countrydle History</v-card-title>
            <v-card-text>
                <v-data-table>
                    <template v-slot:default>
                        <thead>
                            <tr>
                                <th class="text-left">Date</th>
                                <th class="text-left">Country</th>
                                <th class="text-left">Points</th>
                                <th class="text-left">Questions asked</th>
                                <th class="text-left">Guesses Made</th>
                                <th class="text-left">Won</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="entry in history" :key="entry.id" :class="entry.won? 'won-row': 'lost-row'">
                                <td>{{ entry.day.date }}</td>
                                <td>{{ entry.day.country?.name}}</td>
                                <td>{{ entry.points }}</td>
                                <td>{{ entry.questions_asked }}</td>
                                <td>{{ entry.guesses_made }}</td>
                                <td>{{ entry.won ? 'Yes' : 'No' }}</td>
                            </tr>
                        </tbody>
                    </template>
                </v-data-table>
                </v-card-text>  
        </v-card>
    </v-container>
    <CustomPopUp :showPopup="showPopup" @update:showPopup="showPopup = $event" :popUpTitle="popUpTitle"
        :popUpText="popUpText" />
</template>

<script lang="ts">
import { ref, computed, onMounted, defineComponent } from 'vue';
import { useAuthStore, User } from '../stores/auth'; // Your auth store
import { useRouter } from 'vue-router';
import { useVuelidate } from '@vuelidate/core';
import { required, email, minLength } from '@vuelidate/validators';
import { apiService, MyState } from '../services/api';

export default defineComponent({
    name: 'Account',
    setup() {
        const authStore = useAuthStore();
        const router = useRouter();

        const pass1 = ref('');
        const pass2 = ref('');

        const showPopup = ref(false);
        const popUpTitle = ref('')
        const popUpText = ref('')
        const user = ref<User>({
            username: '',
            email: '',
        });
        const history = ref<Array<MyState>>([]);
        const rules = {
            username: { required, minLength: minLength(3) },
            email: { required, email },
        };

        const passwordRules = [
            (v: string): string | boolean => !!v || 'Password is required',
            // (v: string): string | boolean => v.length >= 5 || 'Password must be at least 5 characters long',
            // (v: string): string | boolean => /[A-Z]/.test(v) || 'Password must contain at least one uppercase letter',
            // (v: string): string | boolean => /[a-z]/.test(v) || 'Password must contain at least one lowercase letter',
            // (v: string): string | boolean => /[0-9]/.test(v) || 'Password must contain at least one number',
            (): string | boolean => pass1.value == pass2.value || 'Passwords must be the same!'

        ];

        // const password2Rules = [
        //     (v: string): string | boolean => !!v || 'Password is required',
        //     (v: string): string | boolean => v.length >= 5 || 'Password must be at least 5 characters long',
        //     // (v: string): string | boolean => /[A-Z]/.test(v) || 'Password must contain at least one uppercase letter',
        //     // (v: string): string | boolean => /[a-z]/.test(v) || 'Password must contain at least one lowercase letter',
        //     (v: string): string | boolean => /[0-9]/.test(v) || 'Password must contain at least one number',
        // ];

        const v$ = useVuelidate(rules, user);

        const validUser = computed(() => !v$.value.$error && (user.value.username.trim() !== authStore.user?.username || user.value.email.trim() !== authStore.user.email));
        // const validPassword = computed(() => true);
        const showPassword = ref(false);

        function toggleShowPassword() {
            showPassword.value = !showPassword.value;
        }

        onMounted(async () => {
            await authStore.getUser();
            if (!authStore.isAuth) {
                router.push({ name: 'Home' })
                return;
            }
            if (authStore.user == null) return;

            user.value = {
                ...authStore.user
            };
            let resp = await apiService.getMyHistory();
            history.value = resp.data;
        });

        const updateAccount = async () => {
            const status = await v$.value.$validate();
            if (!status) return;

            const resp = await authStore.updateUser(user.value);
            popUpTitle.value = "Account updated!";
            popUpText.value = resp.data.message;
            if (authStore.error) {
                popUpTitle.value = "Account update failed!";
                popUpText.value = authStore.errorMessage;
            }
            showPopup.value = true;
        };

        const changePassword = async () => {
            // console.log(!pass1.value || !pass2.value || pass1.value !== pass2.value)
            if (!pass1.value || !pass2.value || pass1.value !== pass2.value) return;

            const resp = await authStore.changePassword(pass1.value);

            popUpTitle.value = "Password changed!";
            popUpText.value = resp.data.message;

            if (authStore.error) {
                popUpTitle.value = "Password change failed!";
                popUpText.value = authStore.errorMessage;
            }
            showPopup.value = true;
        };


        return {
            user,
            showPassword,
            validUser,
            rules,
            pass1,
            pass2,
            showPopup,
            popUpTitle,
            popUpText,
            passwordRules,
            history,
            updateAccount,
            toggleShowPassword,
            changePassword
        }

    },
});
</script>

<style scoped>
.account-card {
    padding: 20px;
}

.act-btn-box {
    justify-content: center;
}

.account-container {
    display: grid;
    grid-template-columns: 50% 50%;
    column-gap: 20px;
    row-gap: 20px;
}

.password-btn {
    width: max-content;
}

.my-countrydle-history {
    grid-column: 1 / 3;
}

.lost-row {
    background-color: #aa2222;
    color: white;
}

.won-row {
    background-color: #4caf50;
    color: white;
}

@media (max-width: 800px) {
    .account-container {
        grid-template-columns: auto;
        row-gap: 20px;
    }
}
</style>