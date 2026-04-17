/*
Author: Fenix Do
Date: 03/28/2026
Purpose: Build map markers from database locations (window.mapLocations) and wire pin
         clicks to fetchAndUpdateGraph (updateGraphs.js) for client-side graph rendering.
*/

function closeAllModals() {
  document.querySelectorAll('.modal').forEach(m => { m.style.display = 'none'; });
}

// Marker colour by source table
function markerColor(table) {
  if (table === 'USACE')    return '#140ceb';
  if (table === 'DANR')     return '#f91d1d';
  if (table === 'COCORAHS') return '#057c37';
  return '#888888';
}

// Wait for map to be ready, then build markers
map.on('load', function () {
  map.resize();

  const locations = window.mapLocations || [];
  const container = document.getElementById('modal-container');

  locations.forEach(function (loc) {
    const modalId = loc.name.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '');

    // --- Create modal ---
    const modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal';

    const content = document.createElement('div');
    content.className = 'modal-content';

    const closeBtn = document.createElement('span');
    closeBtn.className = 'close';
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = 'float:right;font-size:1.4rem;cursor:pointer;line-height:1';
    closeBtn.addEventListener('click', function () { modal.style.display = 'none'; });

    const heading = document.createElement('h3');
    heading.textContent = loc.name + ' (' + loc.table + ')';

    const graphContainer = document.createElement('div');
    graphContainer.className = 'modal-graph-container';
    graphContainer.id = modalId + '_graph';

    content.appendChild(closeBtn);
    content.appendChild(heading);

    // Dataset selector (if multiple datasets available)
    if (loc.datasets && loc.datasets.length > 1) {
      const label = document.createElement('label');
      label.textContent = 'Dataset: ';
      label.style.cssText = 'font-size:0.85rem;color:#667085;margin-right:6px;';

      const sel = document.createElement('select');
      sel.className = 'modal-dataset-select';
      sel.id = modalId + '_dataset';
      loc.datasets.forEach(function (ds) {
        const opt = document.createElement('option');
        opt.value = ds;
        opt.textContent = ds;
        sel.appendChild(opt);
      });
      sel.addEventListener('change', function () {
        fetchAndUpdateGraph(loc.name, sel.value, modalId);
      });
      content.appendChild(label);
      content.appendChild(sel);
    }

    content.appendChild(graphContainer);
    modal.appendChild(content);
    container.appendChild(modal);

    // --- Create Mapbox marker ---
    const marker = new mapboxgl.Marker({ color: markerColor(loc.table) })
      .setLngLat([loc.lon, loc.lat])
      .addTo(map);

    marker.getElement().style.cursor = 'pointer';

    marker.getElement().addEventListener('click', function () {
      closeAllModals();
      modal.style.display = 'block';

      const defaultDataset = (loc.datasets && loc.datasets.length > 0)
        ? loc.datasets[0]
        : '';

      if (defaultDataset) {
        fetchAndUpdateGraph(loc.name, defaultDataset, modalId);
      }

      // Scroll map into view then modal
      const mapEl = document.getElementById('map');
      if (mapEl) {
        scrollTo({ top: mapEl.offsetTop + mapEl.offsetHeight, left: 0, behavior: 'smooth' });
      }
    });
  });
});
