/*
Author: Fenix Do
Date: 03/28/2026
Purpose: Fetch time-series data from /api/timeseries/ and render a Plotly graph
         inside the modal graph container for the given location and dataset.
*/

/**
 * Fetch time-series data and render a Plotly graph inside the modal.
 * @param {string} location - Location name (e.g. "BISMARCK 1.3 WNW")
 * @param {string} dataset  - Dataset display name (e.g. "Max Temperature")
 * @param {string} modalId  - ID of the modal element
 */
async function fetchAndUpdateGraph(location, dataset, modalId) {
  const containerId = modalId + '_graph';
  const container = document.getElementById(containerId);
  if (!container) {
    console.warn('[updateGraphs] Graph container not found:', containerId);
    return;
  }

  container.innerHTML = '<p class="modal-loading">Loading graph\u2026</p>';

  // Keep dataset selector in sync
  const sel = document.getElementById(modalId + '_dataset');
  if (sel && sel.value !== dataset) sel.value = dataset;

  try {
    const url = `/api/timeseries/?location=${encodeURIComponent(location)}&dataset=${encodeURIComponent(dataset)}`;
    const resp = await fetch(url);
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      container.innerHTML = `<p class="modal-loading" style="color:#991b1b;">Error: ${err.error || resp.status}</p>`;
      return;
    }
    const json = await resp.json();

    if (!json.times || json.times.length === 0) {
      container.innerHTML = '<p class="modal-loading">No data available for this selection.</p>';
      return;
    }

    container.innerHTML = '';
    const plotDiv = document.createElement('div');
    plotDiv.style.width = '100%';
    plotDiv.style.minHeight = '320px';
    container.appendChild(plotDiv);

    const trace = {
      x: json.times,
      y: json.values,
      type: 'scatter',
      mode: 'lines+markers',
      name: `${json.location} \u2014 ${json.dataset}`,
      line: { color: '#5b61f6', width: 2 },
      marker: { size: 4 },
    };

    const layout = {
      title: { text: `${json.dataset} \u2014 ${json.location}`, font: { size: 14 } },
      xaxis: { title: 'Date', type: 'date' },
      yaxis: { title: json.dataset },
      margin: { l: 50, r: 20, t: 40, b: 50 },
      autosize: true,
    };

    Plotly.react(plotDiv, [trace], layout, { responsive: true });
  } catch (err) {
    console.error('[updateGraphs] Graph update failed:', err);
    container.innerHTML = `<p class="modal-loading" style="color:#991b1b;">Failed to load graph.</p>`;
  }
}
