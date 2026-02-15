// useMediaQuery.ts
import { ref, onMounted, onUnmounted, Ref } from 'vue';

export function useMediaQuery(query: string): Ref<boolean> {
  const matches = ref<boolean>(window.matchMedia(query).matches);

  const updateMatches = (event: MediaQueryListEvent) => {
    matches.value = event.matches;
  };

  onMounted(() => {
    const mediaQueryList = window.matchMedia(query);
    // Correctly add event listener
    mediaQueryList.addEventListener('change', updateMatches);
    matches.value = mediaQueryList.matches;
  });

  onUnmounted(() => {
    const mediaQueryList = window.matchMedia(query);
    // Correctly remove the event listener when the component unmounts
    mediaQueryList.removeEventListener('change', updateMatches);
  });

  return matches;
}
