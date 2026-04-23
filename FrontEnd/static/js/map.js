/*
Author: Fenix Do
Date: 03/28/2026
Purpose: Initialise the Mapbox map. Markers and click handlers are created
         dynamically from database locations in openModals.js.
*/
mapboxgl.accessToken = 'pk.eyJ1IjoiYWxleGlzMTMiLCJhIjoiY2xkeGk4bXpvMDJmeTNwbXV2bmpleGxxeCJ9.4PMbriYdSiVtIskoEwAsfw';

const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/outdoors-v12',
  center: [-100.5, 46.5],
  zoom: 6,
  maxBounds: [
    [-112.0399, 42.000],
    [-90.3084, 49.0014],
  ],
});

// Zoom threshold at which pin name labels become visible.
// Below this zoom the labels would be illegible and massively overlap
// (there are ~350 markers); above it pins are typically far enough apart
// that overlap is manageable (users can zoom further to separate them).
const PIN_LABEL_MIN_ZOOM = 9;

function _applyPinLabelVisibility() {
  const el = document.getElementById('map');
  if (!el) return;
  el.classList.toggle('zoom-high', map.getZoom() >= PIN_LABEL_MIN_ZOOM);
}

map.on('zoom', _applyPinLabelVisibility);
map.on('load', _applyPinLabelVisibility);
