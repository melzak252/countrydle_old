<template>
    <v-container class="profile-container">
        <!-- Profile Section -->
        <v-card class="mt-3 profile-card">
            <v-card-title>{{ user.user.username }}'s Profile</v-card-title>
            <v-card-text>
                <v-row>
                    <v-col cols="12" md="6">
                        <v-text-field label="Username" prepend-icon="mdi-account" v-model="user.user.username"
                            variant="underlined" disabled></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6">
                        <v-text-field label="Account Created" prepend-icon="mdi-calendar" v-model="formattedCreatedAt"
                            variant="underlined" disabled></v-text-field>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>

        <!-- Game Stats -->
        <v-card class="mt-3 stats-card">
            <v-card-title>Game Stats</v-card-title>
            <v-card-text>
                <v-row dense>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Total Points</v-card-title>
                            <v-card-text class="stat-value">{{ user.points }}</v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Wins</v-card-title>
                            <v-card-text class="stat-value">{{ user.wins }}</v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Current streak</v-card-title>
                            <v-card-text class="stat-value">{{ user.streak }}</v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Questions Asked</v-card-title>
                            <v-card-text class="stat-value">{{ user.questions_asked }}</v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Correct Questions</v-card-title>
                            <v-card-text class="stat-value">{{ user.questions_correct }}</v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Incorrect Questions</v-card-title>
                            <v-card-text class="stat-value">{{ user.questions_incorrect }}</v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Guesses Made</v-card-title>
                            <v-card-text class="stat-value">{{ user.guesses_made }}</v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Correct Guesses</v-card-title>
                            <v-card-text class="stat-value">{{ user.guesses_correct }}</v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card class="stat-box">
                            <v-card-title class="stat-title">Incorrect Guesses</v-card-title>
                            <v-card-text class="stat-value">{{ user.guesses_incorrect }}</v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>

        <!-- Game History Section -->
        <v-card class="mt-3 history-card">
            <v-card-title>Game History</v-card-title>
            <v-card-text>
                <v-data-table :items="user.history" item-value="id" class="elevation-1">
                    <template v-slot:default>
                        <thead>
                            <tr>
                                <th class="text-left">Date</th>
                                <th class="text-left">Country</th>
                                <th class="text-left">Points</th>
                                <th class="text-left">Questions Asked</th>
                                <th class="text-left">Guesses Made</th>
                                <th class="text-left">Won</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="entry in user.history" :key="entry.id" :class="entry.won ? 'won-row' : 'lost-row'">
                                <td>{{ entry.day.date }}</td>
                                <td>{{ entry.day.country === null? 'N/A': entry.day.country.name }}</td>
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
</template>

<script lang="ts">
import { ref, onMounted, defineComponent, computed } from "vue";
import { useRoute } from "vue-router";
import { apiService, ProfileState } from "../services/api"; // Update with actual API service
import dayjs from "dayjs";

export default defineComponent({
    name: "ProfilePage",
    setup() {
        const route = useRoute();
        const username = ref<string>(
            Array.isArray(route.params.username)
                ? route.params.username[0]
                : route.params.username
        );

        const user = ref<ProfileState>({
            user: {
                username: "",
                created_at: "",
            },
            points: 0,
            streak: 0,
            wins: 0,
            questions_asked: 0,
            questions_correct: 0,
            questions_incorrect: 0,
            guesses_made: 0,
            guesses_correct: 0,
            guesses_incorrect: 0,
            history: [],
        });
        
        const formattedCreatedAt = computed(() => {
            return user.value.user.created_at
                ? dayjs(user.value.user.created_at).format("MMMM D, YYYY")
                : "";
        });

        onMounted(async () => {
            try {
                const resp = await apiService.getUserProfile(username.value);
                user.value = resp.data;
            } catch (error) {
                console.error("Error fetching user data:", error);
            }
        });

        return {
            user,
            formattedCreatedAt
        };
    },
});
</script>

<style scoped>
.profile-container {
    max-width: 1200px;
    margin: auto;
}

.profile-card, .stats-card, .history-card {
    padding: 20px;
}

.stat-box {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 150px;
    text-align: center;
    border-radius: 8px;
    background-color: #1f1f1f;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.4);
}

.stat-title {
    font-weight: bold;
    margin-bottom: 10px;
    font-size: 18px;
    opacity: 0.5;
}

.stat-value {
    font-size: 36px;
    font-weight: bold;
}

.elevation-1 {
    box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.12);
}
.lost-row {
    background-color: #aa2222;
    color: white;
}

.won-row {
    background-color: #4caf50aa;
    color: white;
}
@media (max-width: 800px) {
    .profile-container {
        padding: 10px;
    }
}
</style>
