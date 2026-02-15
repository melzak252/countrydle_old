<template>
  <v-card class="question-box">
    <v-card-title @click="toggleCollapse" style="cursor: pointer; display: flex;">
      Ask Your Questions <v-icon style="margin-left: auto;">{{ isCollapsed ? 'mdi-chevron-up' : 'mdi-chevron-down'
        }}</v-icon>
    </v-card-title>
    <p style="padding-left: 1rem;">You have {{ remainingQuestions }} questions remaining.</p>
    <v-expand-transition>
      <div v-show="isCollapsed">
        <div class="sent-box ma-0">
          <v-text-field class="question-input" v-model="questionInput" maxlength="100" label="Ask a True/False Question"
            placeholder="Is it located in Europe?" :rules="questionRules" @keyup.enter="sendQuestion"
            :disabled="!canSend">
          </v-text-field>
          <v-btn class="sent-btn" style="height: 56px; align-self: baseline;" @click="sendQuestion" color="primary"
            :disabled="!canSend || !questionInput">
            <template v-if="loading">
              <v-progress-circular indeterminate color="white" size="24" class="mr-2"></v-progress-circular>
            </template>
            <template v-else>
              Ask
              <v-icon dark right style="padding-left: 10px;">
                mdi-send
              </v-icon>
            </template>
          </v-btn>
        </div>
        <v-row>
          <v-col v-for="(entry, index) in reversedQuestionsHistory" :key="index" cols="12">
            <v-card outlined :class="getRowClass(entry)" class="pa-2" style="overflow: initial; z-index: initial">
              <v-icon size="80" style="margin-left: auto;" class="question-icon">
                {{ (!entry.valid || entry.answer === null) ? 'mdi-help' : (entry.answer ? 'mdi-check-bold' :
                  'mdi-close-thick') }}
              </v-icon>
              <v-card-title title="Improved question by system" style="justify-self: center;">
                {{ entry.question }}
              </v-card-title>
              <v-card-subtitle title="Original question">{{ entry.original_question }}</v-card-subtitle>
              <v-card-text>{{ entry.explanation }}</v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-expand-transition>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { Question, useCountrydleStore } from '../stores/countrydle';
import { useMediaQuery } from '../consumable/useMediaQuery';

export default defineComponent({
  name: 'QuestionBox',
  setup() {
    const gameStore = useCountrydleStore(); // Access the Pinia store
    // Access state from the store
    const isMobile = useMediaQuery("(max-width: 1000px)")

    const questionInput = ref('');
    const isCollapsed = ref(true);
    const isGameOver = computed(() => gameStore.isGameOver);
    const questionsHistory = computed(() => gameStore.questionsHistory);
    const loading = computed(() => gameStore.loading);
    const canSend = computed(() => gameStore.remainingQuestions > 0 && !gameStore.loading && !gameStore.isGameOver);
    const remainingQuestions = computed(() => gameStore.remainingQuestions)
    // Reverse the questionsHistory array
    const reversedQuestionsHistory = computed(() => {
      return [...gameStore.questionsHistory].reverse();
    });

    const toggleCollapse = () => {
      isCollapsed.value = !isCollapsed.value;
    };

    // Determine the row class based on the answer
    const getRowClass = (entry: Question) => {
      if (!entry.valid || entry.answer === null) return 'orange-outline';
      return entry.answer ? 'green-outline' : 'red-outline';
    };

    // Handle sending the question
    const sendQuestion = () => {
      questionInput.value = questionInput.value.trim();
      if (!questionInput.value) return;
      const question = questionInput.value;
      gameStore.askQuestion(question); // Use the store action to send a question
      questionInput.value = ""; // Clear the input field
    };

    const questionRules = [
      // (v: string): string | boolean => !!v || 'Question is required',
      // (v: string): string | boolean => v.length >= 3 || 'Question must be at least 3 characters!',
      (v: string): string | boolean => v.length <= 100 || 'Question cannot be longer than 100 characters!'
    ];

    return {
      questionInput,
      canSend,
      isGameOver,
      isMobile,
      questionsHistory,
      reversedQuestionsHistory,
      loading,
      remainingQuestions,
      questionRules,
      isCollapsed,
      toggleCollapse,
      getRowClass,
      sendQuestion
    };
  }
});
</script>

<style scoped>
.question-box {
  height: 100%;
  padding: 20px;
  /* background-color: #f5f5f5; Light background */
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

.orange-outline {
  border: 2px solid #ff9800;
  color: #ff9800;
  background-color: #ff980010;
}

.sent-box {
  height: 100px;
  display: grid;
  grid-template-columns: auto 100px;
  align-items: flex-start;
  padding: 0.5rem 1rem;
}


/* .dektop-question-layout {
  display: grid;
  width: 100%;
  max-width: 100%;
  grid-template-columns: auto 75px;
  align-items: center;
}

.mobile-question-layout {
  display: flex;
  flex-direction: column;
  grid-template-rows: auto 75px;
  justify-content: flex-start;
  align-items: center;
} */

.question-icon {
  position: absolute;
  top: calc(50% - 40px);
  right: 40px;
  z-index: -1;
  opacity: 0.4;
}
</style>
