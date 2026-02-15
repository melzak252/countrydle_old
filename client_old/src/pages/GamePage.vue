<template>
  <div class="game-page">
    <div class="game-container">
      <MapBox class="map-box"/>
      <QuestionBox class="question-box" />
      <GuessBox class="guess-box"/>
    </div>
    <CustomPopUp
      :showPopup="showPopup"
      @update:showPopup="showPopup = $event"
      :popUpTitle="popUpTitle"
      :popUpText="popUpText"
    />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, ref, watch } from 'vue';
import { useCountrydleStore } from '../stores/countrydle';
import QuestionBox from '../components/QuestionBox.vue';
import GuessBox from '../components/GuessBox.vue';
import MapBox from '../components/MapBox.vue';
import CustomPopUp from '../components/CustomPopUp.vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'GamePage',
  components: {
    QuestionBox,
    GuessBox,
    MapBox,
    CustomPopUp,
  },
  setup() {
    // Access the store
    const gameStore = useCountrydleStore();
    const authStore = useAuthStore();
    const router = useRouter();

    const won = computed(() => gameStore.won);
    const loading = computed(() => gameStore.loading);
    const country = computed(() => gameStore.correctCountry);
    const showPopup = ref(gameStore.isGameOver);
    const shouldShow = ref(false);
    const popUpTitle = computed(() => gameStore.won ? 'Congratulations!' : 'Game Over');
    const popUpText = computed(() => gameStore.won ? `Great job! You've guessed the correct country. Keep it up! U get: <br><br> <h1>+${ gameStore.points} Points</h1>`:
            `The country was <b>${ country.value?.name }</b>. <br>Don't worry! You can get it tomorrow!`);
    onMounted(async () => {
      if(!await authStore.checkAuth()) {
        router.push({ name: 'Home' })
        return;
      }
      await gameStore.loadGameState();
    });

    const closePopup = () => {
      showPopup.value = false;
    };

    watch(() => gameStore.isGameOver, (newVal) => {
      if (gameStore.loading && newVal) {
        shouldShow.value = true;
        return
      }
      showPopup.value = newVal;
    });

    watch(() => gameStore.loading, (newVal) => {
      if (newVal) return;
      if (shouldShow) shouldShow.value = true
    })

    return {
      showPopup,
      won,
      loading,
      country,
      popUpTitle,
      popUpText,
      closePopup,
    };
  }
});
</script>

<style scoped>
.game-page {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.game-container {
  display: grid;
  grid-template-columns: 2fr 1fr; 
  gap: 20px;
  max-width: 1440px;
  width: 100%;
}

.map-box {
  grid-column: 1 / 3;
}

@media (max-width: 800px) {
  .game-container {
    grid-template-columns: 1fr; 
    grid-template-rows: auto auto auto;
    column-gap: 0px;
  }
  .question-box {
    grid-row: 2;
  }
  .guess-box {
    grid-row: 3;
  }
}

</style>
