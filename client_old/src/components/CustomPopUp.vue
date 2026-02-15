<template>
  <v-dialog v-model="localShowPopup" max-width="500">
    <v-card>
      <v-card-title class="text-h5">{{ popUpTitle }}</v-card-title>
      <v-card-text v-html="popUpText"></v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="closePopup">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

// Define props
const props = defineProps({
  showPopup: Boolean,
  popUpTitle: String,
  popUpText: String
});

// Emit event
const emit = defineEmits(['update:showPopup']);

// Local reactive variable
const localShowPopup = ref(props.showPopup);

// Watch for changes in the prop and update local state
watch(() => props.showPopup, (newVal) => {
  localShowPopup.value = newVal;
});

// Emit the updated value when the popup is closed
const closePopup = () => {
  emit('update:showPopup', false);
  localShowPopup.value = false;
};

watch(localShowPopup, (newVal) => {
  emit('update:showPopup', newVal);
  localShowPopup.value = newVal;
});
</script>
