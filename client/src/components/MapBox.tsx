import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useGameStore } from '../stores/gameStore';
import L, { type PathOptions } from 'leaflet';
import type { Feature } from 'geojson';
import { RotateCcw, Check } from 'lucide-react';

interface MapBoxProps {
  correctCountryName?: string;
}

interface MapControlsProps {
  correctCountryName?: string;
  geoJsonData: any;
  map: L.Map | null;
}

function MapControls({ correctCountryName, geoJsonData, map }: MapControlsProps) {
  const { gameState, clearSelection } = useGameStore();

  const handleZoomToCorrect = () => {
    if (map && correctCountryName && geoJsonData) {
      const correctFeature = geoJsonData.features.find((f: any) => 
        f.properties.SOVEREIGNT.toUpperCase() === correctCountryName.toUpperCase()
      );

      if (correctFeature) {
        const layer = L.geoJSON(correctFeature);
        const bounds = layer.getBounds();
        if (bounds.isValid()) {
            map.flyToBounds(bounds, { duration: 2 });
        }
      }
    }
  };

  return (
    <div 
        className="absolute top-0 left-0 mt-20 ml-3 flex flex-col gap-2 z-[1000]"
    >
       <button
          onClick={(e) => {
             e.preventDefault();
             clearSelection();
          }}
          className="bg-zinc-800 text-white p-2 rounded shadow-md hover:bg-zinc-700 transition-colors border border-zinc-600 w-8 h-8 flex items-center justify-center cursor-pointer"
          title="Reset selected countries"
       >
          <RotateCcw size={16} />
       </button>
       
       {gameState?.is_game_over && (
         <button
            onClick={(e) => {
                e.preventDefault();
                handleZoomToCorrect();
            }}
            className="bg-green-600 text-white p-2 rounded shadow-md hover:bg-green-700 transition-colors border border-green-500 w-8 h-8 flex items-center justify-center cursor-pointer"
            title="Zoom to correct country"
         >
            <Check size={16} />
         </button>
       )}
    </div>
  );
}

function MapController({ correctCountryName, geoJsonData }: { correctCountryName?: string, geoJsonData: any }) {
  const map = useMap();
  const { gameState } = useGameStore();

  useEffect(() => {
    if (gameState?.is_game_over && correctCountryName && geoJsonData) {
      // Find the feature for the correct country
      const correctFeature = geoJsonData.features.find((f: any) => 
        f.properties.SOVEREIGNT.toUpperCase() === correctCountryName.toUpperCase()
      );

      if (correctFeature) {
        const layer = L.geoJSON(correctFeature);
        const bounds = layer.getBounds();
        if (bounds.isValid()) {
            map.flyToBounds(bounds, { duration: 2 });
        }
      }
    }
  }, [gameState?.is_game_over, correctCountryName, geoJsonData, map]);

  return null;
}

export default function MapBox({ correctCountryName }: MapBoxProps) {
  const [geoJsonData, setGeoJsonData] = useState<any>(null);
  const [map, setMap] = useState<L.Map | null>(null);
  const { selectedCountries, toggleCountrySelection, gameState } = useGameStore();
  const geoJsonLayerRef = useRef<L.GeoJSON | null>(null);
  
  useEffect(() => {
    fetch('/countries_50m.geojson')
      .then(res => res.json())
      .then(data => setGeoJsonData(data))
      .catch(err => console.error('Failed to load map data', err));
  }, []);

  const getStyleFromState = (feature: any, currentSelectedCountries: string[], currentCorrectName?: string): PathOptions => {
    if (!feature || !feature.properties) return {};

    const countryName = feature.properties.SOVEREIGNT.toUpperCase();
    
    let isCorrect = false;
    console.log('Computing style for', countryName, 'Selected:', currentSelectedCountries, 'Correct:', currentCorrectName);
    if (currentCorrectName) {
        isCorrect = countryName === currentCorrectName.toUpperCase();
    }
    const isSelected = currentSelectedCountries.includes(countryName);

    return {
      fillColor: isCorrect ? '#22cc22' : (isSelected ? '#cc2222' : '#242424'),
      weight: 1, // Keep thin border
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7,
    };
  };

  const getStyle = (feature: any) => {
      // This is called by React render cycle or when we manually invoke it with current state
      const { selectedCountries, correctCountry } = useGameStore.getState();
      return getStyleFromState(feature, selectedCountries, correctCountry?.name);
  }

  // Optimization: Update styles imperatively instead of re-rendering whole map
  useEffect(() => {
    if (geoJsonLayerRef.current) {
        geoJsonLayerRef.current.eachLayer((layer: any) => {
             const feature = layer.feature;
             if (feature) {
                 const { gameState, correctCountry } = useGameStore.getState();
                 const newStyle = getStyleFromState(
                     feature, 
                     selectedCountries, 
                     gameState?.is_game_over ? correctCountryName || correctCountry?.name : undefined
                 );
                 layer.setStyle(newStyle);
                 
                 // If game over and correct country, bring to front
                 const countryName = feature.properties.SOVEREIGNT.toUpperCase();
                 if (correctCountryName && (countryName === correctCountryName.toUpperCase())) {
                     layer.bringToFront();
                 }
             }
        });
    }
  }, [selectedCountries, gameState?.is_game_over, correctCountryName]);

  const onEachFeature = (feature: Feature, layer: L.Layer) => {
    const countryName = feature.properties?.SOVEREIGNT;
    
    // Bind click handler
    layer.on({
      click: () => {
        // Allow selection regardless of game state
        toggleCountrySelection(countryName.toUpperCase());
      },
      mouseover: (e) => {
        const l = e.target;
        l.setStyle({
          weight: 2,
          fillOpacity: 0.8,
        });
        l.bringToFront();
      },
      mouseout: (e) => {
        const l = e.target;
        // Reset to computed style using direct store access
        const { selectedCountries: currentSelected, correctCountry } = useGameStore.getState();
        
        const style = getStyleFromState(
            feature, 
            currentSelected, 
            correctCountry?.name
        );
        l.setStyle(style);
      }
    });

    if (feature.properties) {
        layer.bindTooltip(`${feature.properties.ADMIN}`);
    }
  };

  if (!geoJsonData) {
    return <div className="h-[400px] w-full bg-zinc-900 rounded-xl animate-pulse flex items-center justify-center text-zinc-500">Loading Map...</div>;
  }

  return (
    <div className="h-[500px] w-full bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-lg mb-8 relative z-0">
      <style>{`
        .leaflet-interactive:focus {
            outline: none;
        }
      `}</style>
      <MapContainer 
        center={[20, 0]} 
        zoom={2} 
        style={{ height: '100%', width: '100%', background: '#242424' }}
        minZoom={2}
        maxZoom={10}
        attributionControl={false}
        ref={setMap}
      >
        <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        
        <GeoJSON 
            data={geoJsonData} 
            style={getStyle} 
            onEachFeature={onEachFeature}
            ref={geoJsonLayerRef}
        />
        
        <MapController correctCountryName={correctCountryName} geoJsonData={geoJsonData} />
      </MapContainer>
      <MapControls correctCountryName={correctCountryName} geoJsonData={geoJsonData} map={map} />
    </div>
  );
}
