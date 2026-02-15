// src/main.ts
import { createApp } from "vue";
import App from "./App.vue";
import { createVuetify } from "vuetify";
import { router } from "./router"; // Import the router
import "vuetify/styles"; // Import Vuetify styles
import "@mdi/font/css/materialdesignicons.css"; // Material Design Icons
import { LMap, LTileLayer, LMarker } from '@vue-leaflet/vue-leaflet';
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import GoogleLogInPlugin from "vue3-google-login";
import CustomPopUp from "./components/CustomPopUp.vue";

const vuetify = createVuetify({
  theme: {
    defaultTheme: "dark", // Set the default theme to dark
    themes: {
      dark: {
        dark: true,
        colors: {
          background: "#121212", // Dark background color
          surface: "#1e1e1e", // Dark surface color
          primary: "#BB86FC", // Customize your primary color
          secondary: "#03DAC6", // Customize your secondary color
          error: "#CF6679", // Error color
          success: "#03DAC5", // Success color
        },
      },
    },
  },
  components,
  directives,
});

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate); // Register the persistence plugin

const app = createApp(App);

app
  .use(router) // Use the router
  .use(pinia)
  .use(vuetify) // Use Vuetify
  .use(GoogleLogInPlugin, {
    clientId:
      "624396927539-luhujtnrft1igdoug3bim8ac9nmvf3sk.apps.googleusercontent.com",
  })
  .mount("#app");

app.component("CustomPopUp", CustomPopUp);
app.component('l-map', LMap);
app.component('l-tile-layer', LTileLayer);
app.component('l-marker', LMarker);
