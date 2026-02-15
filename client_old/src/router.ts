// src/router.ts
import { createRouter, createWebHistory } from "vue-router";
import HomePage from "./pages/HomePage.vue";
import PortfolioPage from "./pages/PortfolioPage.vue";
import AboutMePage from "./pages/AboutMePage.vue";
import GamePage from "./pages/GamePage.vue";
import SignPage from "./pages/SignPage.vue";
import AccountPage from "./pages/AccountPage.vue";
import TermsPage from "./pages/TermsPage.vue";
import PrivacyPage from "./pages/PrivacyPage.vue";
import CookiePage from "./pages/CookiePage.vue";
import CountrydleHistoryPage from "./pages/CountrydleHistoryPage.vue";
import ProfilePage from "./pages/ProfilePage.vue";

import { useAuthStore } from "./stores/auth";

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomePage,
  },
  {
    path: "/home",
    name: "HomePage",
    component: HomePage,
  },
  {
    path: "/portfolio",
    name: "Portfolio",
    component: PortfolioPage,
  },
  {
    path: "/aboutme",
    name: "AboutMe",
    component: AboutMePage,
  },
  {
    path: "/game",
    name: "Game",
    component: GamePage,
  },
  { path: "/sign", name: "Sign", component: SignPage },
  { path: "/account", name: "Account", component: AccountPage },
  { path: "/terms", name: "Terms", component: TermsPage },
  { path: "/privacy", name: "Privacy", component: PrivacyPage },
  { path: "/cookie", name: "Cookie", component: CookiePage },
  { path: "/countrydle/history", name: "CountrydleHistory", component: CountrydleHistoryPage },
  {
    path: '/profile/:username', // Dynamic segment for username
    name: 'Profile',
    component: ProfilePage,
    props: true, // Pass the route params as props to the component
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const store = useAuthStore();
  // we wanted to use the store here
  if (to.path === "/game" && !store.isAuth) next("/sign");
  else if (to.path === "/sign" && store.isAuth) next("/");
  else next();
});

router.beforeEach(() => {
  // ✅ This will work because the router starts its navigation after
  // the router is installed and pinia will be installed too
  // const store = useAuthStore()
  // if (to.meta.requiresAuth && !store.isAuth) return '/login'
});
