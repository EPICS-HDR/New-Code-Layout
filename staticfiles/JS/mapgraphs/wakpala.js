/* Load the JSON data from the file */
fetch(WAKPALA_URL)

.then(response => response.json())
.then(data => {
  /* Extract the data from the JSON object */
  const [times1, gheights, times2, discharge] = data;

  /* Create the first graph */
  const graph1 = {
    x: times1,
    y: gheights,
    mode: 'lines',
    type: 'scatter'
  };

  /* Set the layout options for the first plot */
  const layout1 = {
    title: 'Wakpala Gauge Height',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Gauge Height'}
  };

  /* Create the first plot */
  Plotly.newPlot('Wakpala Gauge Height', [graph1], layout1);

  /* Create the first table */
  const mean1 = getMean(gheights).toFixed(3);
  const sd1 = getStandardDeviation(gheights).toFixed(3);
  const median1 = getMedian(gheights).toFixed(3);
  const min1 = Math.min(...gheights).toFixed(3);
  const max1 = Math.max(...gheights).toFixed(3);
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
  Plotly.newPlot('Wakpala Gauge Height Table', [table1], tableLayout);

  /* Create the second graph */
  const graph2 = {
    x: times2,
    y: discharge,
    mode: 'lines',
    type: 'scatter'
  };

  /* Set the layout options for the second plot */
  const layout2 = {
    title: 'Wakpala Discharge',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Discharge'}
  };

  /* Create the second plot */
  Plotly.newPlot('Wakpala Discharge', [graph2], layout2);

  /* Create the second table */
  const mean2 = getMean(discharge).toFixed(3);
  const sd2 = getStandardDeviation(discharge).toFixed(3);
  const median2 = getMedian(discharge).toFixed(3);
  const min2 = Math.min(...discharge).toFixed(3);
  const max2 = Math.max(...discharge).toFixed(3);
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
  Plotly.newPlot('Wakpala Discharge Table', [table2], tableLayout);
})