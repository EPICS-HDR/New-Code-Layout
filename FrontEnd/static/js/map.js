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
