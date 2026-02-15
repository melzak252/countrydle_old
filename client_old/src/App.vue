<!-- src/App.vue -->
<template>
  <v-app>
    <Header></Header>
    <v-main>
      <v-container class="App-container">
        <router-view /> <!-- This will display the current route component -->
      </v-container>
    </v-main>
    <Footer></Footer>
  </v-app>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useMediaQuery } from './consumable/useMediaQuery';
import Footer from './components/Footer.vue';
import Header from './components/Header.vue';

export default defineComponent({
  name: 'App',
  components: {
    Footer,
    Header
  },
  setup() {
    const isMobile = useMediaQuery("(max-width: 800px)")


    return {
      isMobile
    };
  },
});
</script>

<style scoped>
.menu-spacer {
  display: flex;
}

.registration-alert {
  padding: 0 !important;
  font-size: small !important;
  max-width: 500px !important;
  margin-left: 25%;
}
</style>

<style>
.v-slide-group__content {
  justify-content: center;
}

.v-btn {
  width: 120px;
}

.v-main {
  height: 100%;
}

.username-btn {
  color: white !important;
}

.username-btn:hover {
  opacity: 0.8;
}

@media (max-width: 600px) {
  .v-btn {
    width: 100px;
  }
}

@media (min-width: 900px) {
  .App-container {
    max-width: 1200px !important;
  }

}
</style>