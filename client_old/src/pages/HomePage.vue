<template>
  <v-container class="home-container">
    <v-card class="rules" style="align-self: flex-start; margin-top: 10px;">
      <v-card-title class="headline font-weight-bold">
        Welcome to JMelzacki!
      </v-card-title>
      <v-card-text class="py-5">
        <h2 class="text-h5 font-weight-medium mb-4">
          How to play Countrydle:
        </h2>
        <v-row class="d-flex flex-column">
          <!-- Objective Card -->
          <v-col cols="12" class="d-flex">
            <v-card class="pa-3 flex-grow-1 d-flex flex-column" variant="tonal">
              <v-card-title class="text-h6 font-weight-bold">
                Objective
              </v-card-title>
              <v-card-text class="flex-grow-1">
                Guess the country by asking up to 10 true/false questions and making up to 3 guesses.
              </v-card-text>
            </v-card>
          </v-col>
          <!-- Step 1 Card -->
          <v-col cols="12" class="d-flex">
            <v-card class="pa-3 flex-grow-1 d-flex flex-column" variant="tonal">
              <v-card-title class="text-h6 font-weight-bold">
                Step 1: Log In
              </v-card-title>
              <v-card-text class="flex-grow-1">
                To start, you need to register an account.<br>
                Once registered, log in to access the game.
              </v-card-text>
            </v-card>
          </v-col>
          <!-- Step 2 Card -->
          <v-col cols="12" class="d-flex">
            <v-card class="pa-3 flex-grow-1 d-flex flex-column" variant="tonal">
              <v-card-title class="text-h6 font-weight-bold">
                Step 2: Ask Questions
              </v-card-title>
              <v-card-text class="flex-grow-1">
                You can ask up to 10 true/false questions to narrow down the possibilities.
              </v-card-text>
            </v-card>
          </v-col>
          <!-- Step 3 Card -->
          <v-col cols="12" class="d-flex">
            <v-card class="pa-3 flex-grow-1 d-flex flex-column" variant="tonal">
              <v-card-title class="text-h6 font-weight-bold">
                Step 3: Make Guesses
              </v-card-title>
              <v-card-text class="flex-grow-1">
                You have 3 attempts to guess the correct country. Use your questions wisely!
              </v-card-text>
            </v-card>
          </v-col>
          <!-- Step 4 Card -->
          <v-col cols="12" class="d-flex">
            <v-card class="pa-3 flex-grow-1 d-flex flex-column" variant="tonal">
              <v-card-title class="text-h6 font-weight-bold">
                Step 4: Win!
              </v-card-title>
              <v-card-text class="flex-grow-1">
                Celebrate your victory!
                <br>
                <br>
                For each win, you earn points and climb the leaderboard.<br><br>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" class="d-flex">
            <v-card class="pa-3 flex-grow-1 d-flex flex-column" variant="tonal">
              <v-card-title class="text-h6 font-weight-bold">
                Points
              </v-card-title>
              <v-card-text class="flex-grow-1">
                Questions are worth <b>100 points each.</b><br>
                Guesses are worth more:<br>
                - 1st guess is worth <b>1000 points</b><br>
                - 2nd guess is worth <b>500 points</b><br>
                - 3rd guess is worth <b>200 points</b><br>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <!-- Second Column: Buttons and Leaderboard -->
    <!-- Buttons Section -->
    <v-card class="home-buttons">
      <v-btn large variant="tonal" to="/game" class="home-btn mb-3">
        Play
      </v-btn>
      <v-btn large variant="tonal" to="/aboutme" class="home-btn mb-3">
        About Me
      </v-btn>
      <v-btn large variant="tonal" to="/portfolio" class="home-btn">
        Portfolio
      </v-btn>
    </v-card>
    <v-card class="home-leader-board">
      <v-card-title class="headline font-weight-bold">
        Leaderboard
      </v-card-title>
      <v-data-table :items="countrydle.leaderboard" :items-per-page-options="[5, 10, 20, 50, 100]" :headers="headers">
        <template v-slot:item.index="{ index }">
          {{ index + 1 }}
        </template>
        <template v-slot:item.username="{ item }">
          <!-- Make username clickable -->
          <router-link :to="{ name: 'Profile', params: { username: item.username } }" class="username-link">
            {{ item.username }}
          </router-link>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { useCountrydleStore } from '../stores/countrydle';
import { onMounted } from 'vue';

export default {
  name: 'HomePage',
  setup() {
    const countrydle = useCountrydleStore();
    const headers = [
      { title: 'Index', value: 'index', sortable: false, width: "50px" },
      { title: 'Player', value: 'username', width: "100px" },
      { title: 'Points', value: 'points', sortable: true, width: "50px", align: "center" as 'start' | 'center' | 'end' },
      { title: 'Wins', value: 'wins', sortable: true, width: "50px", align: "center" as 'start' | 'center' | 'end' },
      { title: 'Streak', value: 'streak', sortable: true, width: "50px", align: "center" as 'start' | 'center' | 'end' },
    ];
    onMounted(() => {
      countrydle.getLeaderboard();
    });

    return {
      countrydle,
      headers,
    };
  },
};
</script>

<style>
.home-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 250px auto;
  column-gap: 15px;
  row-gap: 15px;
  align-items: center;
}

.rules {
  grid-column: 1;
  grid-row: 1 / 2 span;
}

.home-buttons {
  grid-column: 2;
  grid-row: 1;
  display: flex;
  flex-direction: column;
  padding: 10px 20px !important;
}

.headline {
  text-align: center;
}

.home-leader-board {
  grid-column: 2;
  grid-row: 2;
  height: 100%;
}

.username-link {
  text-decoration: none; 
  color: inherit;
}

.username-link:hover {
  color: #ddaa00;
  text-decoration: underline;
}

.home-btn {
  width: 100%;
  height: max-content !important;
  padding: 10px 20px !important;
  font-size: 36px !important;
}

@media (max-width: 900px) {
  .home-container {
    grid-template-columns: auto;
    grid-template-rows: repeat(3, auto);
  }

  .home-buttons {
    grid-row: 1;
    grid-column: auto;
  }

  .rules {
    grid-row: 2;
  }

  .home-leader-board {
    grid-column: auto;
    grid-row: auto;
    height: 100%;
  }
}

@media (max-width: 800px) {
  .home-btn {
    font-size: 24px !important;
  }
}
</style>
