<template>
  <v-card class="map-box">
    <v-card-title @click="toggleMap" style="cursor: pointer;">
      World Map <v-icon>{{ isMapVisible ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
    </v-card-title>
    <v-expand-transition>
      <div v-show="isMapVisible" class="map-container">
        <l-map ref="mapRef" :zoom="zoom" :min-zoom="minZoom" :max-zoom="maxZoom" :center="center"
          style="height: 500px; width: 100%;">

          <l-geo-json ref="geoJsonRef" :geojson="countriesData" :options-style="styleCountries"
            :options="geoJsonOptions" @geojson-feature-click="onCountryClicked"
            @geojson-feature-mouseover="onCountryMouseOver" @geojson-feature-mouseout="onCountryMouseOut" />
          <v-btn class="reset-btn" @click="resetMap" title="Reset selected countries">
            <span class="mdi mdi-restore" />
          </v-btn>
          <template v-if="gameStore.isGameOver">
            <v-btn class="correct-btn" @click="showCorrect" title="Reset selected countries">
              <span class="mdi mdi-check" />
            </v-btn>
          </template>
        </l-map>

      </div>
    </v-expand-transition>
  </v-card>
</template>

<script lang="ts">
import { LGeoJson, LMap, LTileLayer } from '@vue-leaflet/vue-leaflet';
import type { Feature, Geometry } from 'geojson';
import * as L from 'leaflet';
import { defineComponent, onMounted, ref, watch } from 'vue';
import { useCountrydleStore } from '../stores/countrydle';

import 'leaflet/dist/leaflet.css';

interface FeatureProperties {
  SOVEREIGNT: string;
  // Add other properties if needed
  [key: string]: any;
}

export default defineComponent({
  name: 'MapBox',
  components: {
    LMap,
    LTileLayer,
    LGeoJson,
  },
  setup() {
    const gameStore = useCountrydleStore();

    const geoJsonRef = ref<InstanceType<typeof LGeoJson> | null>(null);
    const mapRef = ref<InstanceType<typeof LMap> | null>(null);
    const zoom = ref(2);
    const minZoom = ref(2);
    const maxZoom = ref(10);
    const center = ref<[number, number]>([20, 0]);
    const isMapVisible = ref(true);
    const toggleMap = () => {
      isMapVisible.value = !isMapVisible.value;
    }
    const countriesData = ref<any>(null);

    const loadCountriesData = async () => {
      try {
        const response = await fetch('/countries_50m.geojson');
        countriesData.value = await response.json();
      } catch (error) {
        console.error('Error loading countries data:', error);
      }
    };

    const isCountryCorrect = (cName: string): boolean => {
      return gameStore.correctCountry !== null && gameStore.correctCountry.name.toUpperCase() === cName.toUpperCase();
    }
    const getCountryColor = (isSelected: boolean, isCorrect: boolean): string => {
      return isCorrect ? '#22cc22' : (isSelected ? '#cc2222' : '#22222')
    }

    const styleCountries = (feature?: Feature<Geometry, FeatureProperties>): L.PathOptions => {
      if (!feature || !feature.properties) {
        return {
          fillColor: '#000000', // Default fill color
          weight: 1,
          opacity: 1,
          color: 'white',
          fillOpacity: 0.7,
        };
      }
      const countryName = feature.properties.SOVEREIGNT;
      const isCorrect = isCountryCorrect(countryName);
      const isSelected = gameStore.selectedCountries.includes(countryName.toUpperCase());
      return {
        fillColor: getCountryColor(isSelected, isCorrect),
        weight: 1,
        opacity: 1,
        color: 'white',
        fillOpacity: 0.7,
      };
    };

    const onCountryClicked = (event: L.LeafletMouseEvent) => {
      const countryName = event.target.feature.properties.SOVEREIGNT.toUpperCase();
      const isSelected = gameStore.handleCountryClick(countryName);
      const isCorrect = isCountryCorrect(countryName);
      if (isCorrect) return;

      if (geoJsonRef.value === null || geoJsonRef.value.leafletObject === undefined) return;
      const lObj = geoJsonRef.value.leafletObject as L.GeoJSON & { _layers: L.Path & { feature?: Feature<Geometry, FeatureProperties> } };
      for (const layer of Object.values(lObj._layers)) {
        const l = layer as L.Path & { feature?: Feature<Geometry, FeatureProperties> };
        if (!l.feature || l.feature.properties.SOVEREIGNT.toUpperCase() !== countryName) continue;
        l.setStyle({
          fillColor: getCountryColor(isSelected, false),
        });
      }

    };

    const onCountryMouseOut = (event: L.LeafletMouseEvent) => {
      const layer = event.target;
      layer.setStyle(styleCountries(layer.feature));
      layer.closeTooltip();
    };

    const onCountryMouseOver = (event: L.LeafletMouseEvent) => {
      const layer = event.target;
      const sovereigntName = layer.feature.properties.SOVEREIGNT; // Adjust property name if needed
      const countryName = layer.feature.properties.ADMIN; // Adjust property name if needed
      let tooltip = `<b>${countryName}</b>`;
      if (sovereigntName !== countryName) tooltip = `<b>${sovereigntName}</b><br/>${countryName}`
      layer.setStyle({
        weight: 2,
        fillOpacity: 0.8,
      });
      layer.bindTooltip(tooltip).openTooltip();
    };

    const geoJsonOptions = {
      style: styleCountries,
      onEachFeature: (_: Feature<Geometry, FeatureProperties>, layer: L.Layer) => {
        layer.on({
          click: onCountryClicked,
          mouseover: onCountryMouseOver,
          mouseout: onCountryMouseOut,
        });
      },
    };

    const resetMap = () => {
      gameStore.selectedCountries = [];
      if (geoJsonRef.value === null || geoJsonRef.value.leafletObject === undefined) return;
      const lObj = geoJsonRef.value.leafletObject as L.GeoJSON & { _layers: L.Path & { feature?: Feature<Geometry, FeatureProperties> } };
      for (const layer of Object.values(lObj._layers)) {
        const l = layer as L.Path & { feature?: Feature<Geometry, FeatureProperties> };
        if (!l.feature) continue;
        l.setStyle({
          fillColor: getCountryColor(false, isCountryCorrect(l.feature.properties.SOVEREIGNT)),
        });
      }

    }

    const showCorrect = () => {
      if (geoJsonRef.value === null || geoJsonRef.value.leafletObject === undefined) return;
      const lObj = geoJsonRef.value.leafletObject as L.GeoJSON & { _layers: L.Path & { feature?: Feature<Geometry, FeatureProperties> } };
      let correctLayer: L.Polygon & { feature?: Feature<Geometry, FeatureProperties> } | null = null;
      for (const layer of Object.values(lObj._layers)) {
        const l = layer as L.Polygon & { feature?: Feature<Geometry, FeatureProperties> };
        if (!l.feature || !isCountryCorrect(l.feature.properties.SOVEREIGNT)) continue;
        l.setStyle({
          fillColor: getCountryColor(false, true),
          weight: 2,
        });
        if (isCountryCorrect(l.feature.properties.ADMIN)) correctLayer = l;
      }
      if(mapRef.value === null || mapRef.value.leafletObject === undefined || correctLayer === null) return;
      mapRef.value.leafletObject.flyToBounds(correctLayer.getBounds(), {
        duration: 2,
      })

    }

    onMounted(() => {
      loadCountriesData();
    });

    watch(() => gameStore.isGameOver, (newVal) => {
      if (!newVal) return;
      showCorrect()
    })

    return {
      geoJsonRef,
      mapRef,
      zoom,
      minZoom,
      maxZoom,
      center,
      geoJsonOptions,
      countriesData,
      isMapVisible,
      gameStore,
      toggleMap,
      styleCountries,
      onCountryClicked,
      onCountryMouseOver,
      onCountryMouseOut,
      resetMap,
      showCorrect,
    };
  },
});
</script>

<style>
@import 'leaflet/dist/leaflet.css';

.map-box {
  height: 100%;
  padding: 20px;
}

.l-map {
  width: 100%;
  height: 100%;
}



*,
*:focus,
*:hover {
  outline: none;
}
</style>

<style>
.correct-btn {
  position: relative;
  padding: 0 !important;
  width: 32px !important;
  height: 32px !important;
  min-width: 10px !important;
  top: 110px;
  left: -21px;
  background-color: white !important;
  color: black !important;
  font-size: 22px !important;
  border: 2px solid rgba(0, 0, 0, 0.3) !important;
  border-radius: 3px !important;
  z-index: 1000;
}

.reset-btn {
  position: relative;
  padding: 0 !important;
  width: 32px !important;
  height: 32px !important;
  min-width: 10px !important;
  top: 80px;
  left: 11px;
  background-color: white !important;
  color: black !important;
  font-size: 22px !important;
  border: 2px solid rgba(0, 0, 0, 0.3) !important;
  border-radius: 3px !important;
  z-index: 1000;
}
</style>