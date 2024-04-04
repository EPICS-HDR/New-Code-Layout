/* Load the JSON data from the file */
fetch(SCHMIDT_URL)

.then(response => response.json())
.then(data => {
  /* Extract the data from the JSON object */
  const [times1, elevations1, times2, gheights2] = data;

  /* Create the first graph */
  const graph1 = {
    x: times1,
    y: elevations1,
    mode: 'lines',
    type: 'scatter'
  };

  /* Set the layout options for the first plot */
  const layout1 = {
    title: 'Schmidt Elevation',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Elevation'}
  };

  /* Create the first plot */
  Plotly.newPlot('Schmidt Elevation', [graph1], layout1);

  /* Create the first table */
  const mean1 = getMean(elevations1).toFixed(3);
  const sd1 = getStandardDeviation(elevations1).toFixed(3);
  const median1 = getMedian(elevations1).toFixed(3);
  const min1 = Math.min(...elevations1).toFixed(3);
  const max1 = Math.max(...elevations1).toFixed(3);
  const range1 = (max1 - min1).toFixed(3);
  const statistics1 = [mean1, sd1, median1, min1, max1, range1];
  const table1 = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics1,
      align: 'center',
    }
  };
  Plotly.newPlot('Schmidt Elevation Table', [table1], tableLayout);

  /* Create the second graph */
  const graph2 = {
    x: times2,
    y: gheights2,
    mode: 'lines',
    type: 'scatter'
  };

  /* Set the layout options for the second plot */
  const layout2 = {
    title: 'Schmidt Gauge Height',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Gauge Height'}
  };

  /* Create the second plot */
  Plotly.newPlot('Schmidt Gauge Height', [graph2], layout2);

  /* Create the second table */
  const mean2 = getMean(gheights2).toFixed(3);
  const sd2 = getStandardDeviation(gheights2).toFixed(3);
  const median2 = getMedian(gheights2).toFixed(3);
  const min2 = Math.min(...gheights2).toFixed(3);
  const max2 = Math.max(...gheights2).toFixed(3);
  const range2 = (max2 - min2).toFixed(3);
  const statistics2 = [mean2, sd2, median2, min2, max2, range2];
  const table2 = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics2,
      align: 'center',
    }
  };
  Plotly.newPlot('Schmidt Gauge Height Table', [table2], tableLayout);
})