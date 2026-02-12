<template>
  <v-card class="pa-4 guess-box">
    <v-card-title @click="toggleCollapse" style="cursor: pointer; display: flex;">
      Make a Guess <v-icon style="margin-left: auto;">{{ isCollapsed ? 'mdi-chevron-up' : 'mdi-chevron-down'
        }}</v-icon>
    </v-card-title>
    <p style="padding-left: 1rem; padding-bottom: 2px;">You have {{ remainingGuesses }} guesses remaining.</p>
    <v-expand-transition>
      <div v-show="isCollapsed">
        <div class="guess-container">
          <v-autocomplete v-model="selectedCountry" :items="countries" item-title="name" item-value="id"
            label="Select a Country" placeholder="Start typing to search..." :loading="loadingCountries"
            :disabled="remainingGuesses <= 0 || loading || isGameOver" return-object class="ma-0 mb-4 guess-input"
            hide-no-data hide-details></v-autocomplete>

          <v-btn @click="sendGuess" color="primary" class="guess-button"
            :disabled="remainingGuesses <= 0 || loading || isGameOver || !selectedCountry">
            <template v-if="loading">
              <v-progress-circular indeterminate color="white" size="24" class="mr-2"></v-progress-circular>
            </template>
            <template v-else>
              Guess
              <v-icon dark right style="padding-left: 10px;">
                mdi-magnify
              </v-icon>
            </template>
          </v-btn>
        </div>
        <v-row>
          <v-col v-for="(entry, index) in guessHistory" :key="index" cols="12">
            <v-card outlined :class="getRowClass(entry.answer)" class="pa-4 guess-card">
              <v-card-title style="align-items: center; width: min-content; max-width: calc(100% - 75px);">{{
                entry.guess }} </v-card-title>
              <v-icon size="50">{{ entry.answer ? 'mdi-check-bold' : (entry.answer === null ? 'mdi-help' :
                'mdi-close-thick') }}</v-icon>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-expand-transition>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, ref } from 'vue';
import { useCountrydleStore } from '../stores/countrydle'; // Import Pinia store
import { apiService } from '../services/api';

export default defineComponent({
  name: 'GuessBox',
  setup() {
    // Access the store
    const gameStore = useCountrydleStore();

    // Access state and actions
    const guessHistory = computed(() => gameStore.guessHistory)
    const isGameOver = computed(() => gameStore.isGameOver)
    const remainingGuesses = computed(() => gameStore.remainingGuesses)
    const loading = computed(() => gameStore.loading)
    const isCollapsed = ref(true)
    const selectedCountry = ref<{ id: number, name: string } | null>(null);
    const countries = ref<{ id: number, name: string }[]>([]);
    const loadingCountries = ref(false);


    const toggleCollapse = () => {
      isCollapsed.value = !isCollapsed.value;
    };

    const getRowClass = (correct: boolean | null) => {
      if (correct) return 'green-outline';
      if (correct === null) return 'orange-outline';
      return 'red-outline';
    };

    const sendGuess = () => {
      if (!selectedCountry.value) return;
      
      gameStore.makeGuess(selectedCountry.value.name, selectedCountry.value.id);
      selectedCountry.value = null;
    };

    const fetchCountries = async () => {
      loadingCountries.value = true;
      try {
        const response = await apiService.getCountries();
        countries.value = response.data;
      } catch (error) {
        console.error("Failed to fetch countries", error);
      } finally {
        loadingCountries.value = false;
      }
    }

    onMounted(() => {
      fetchCountries();
    })

    return {
      selectedCountry,
      countries,
      loadingCountries,
      remainingGuesses,
      isGameOver,
      guessHistory,
      loading,
      isCollapsed,
      getRowClass,
      sendGuess,
      toggleCollapse
    };
  }
});
</script>

<style scoped>
.guess-box {
  height: 100%;
  padding: 20px;

}

.green-outline {
  border: 2px solid #4caf50;
  color: #4caf50;
  background-color: #4caf5010;
}

.red-outline {
  border: 2px solid #f44336;
  color: #f44336;
  background-color: #f4433610;
}

.guess-button {
  width: 100%;
  margin-bottom: 10px;
}

.guess-container {
  padding: 0.5rem 1rem;
}

.orange-outline {
  border: 2px solid #ff9800;
  color: #ff9800;
  background-color: #ff980010;
}

.guess-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
