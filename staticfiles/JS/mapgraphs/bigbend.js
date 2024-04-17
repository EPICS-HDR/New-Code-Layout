/* Load the JSON data from the file */
fetch(BIGBEND_URL)

.then(response => response.json())
.then(data => {
  /* Extract the data from the JSON object */
  const [times, elevation, flowSpill, flowPowerhouse, flowOut, elevTailwater, energy, tempWater, tempAir] = data;

  /* Create the graph for Elevation */
  const graphElevation = {
    x: times,
    y: elevation,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutElevation = {
    title: 'Big Bend Elevation',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Elevation'}
  };
  Plotly.newPlot('Big Bend Elevation', [graphElevation], layoutElevation);

  /* Create the table for Elevation */
  const mean1 = getMean(elevation).toFixed(3);
  const sd1 = getStandardDeviation(elevation).toFixed(3);
  const median1 = getMedian(elevation).toFixed(3);
  const min1 = Math.min(...elevation).toFixed(3);
  const max1 = Math.max(...elevation).toFixed(3);
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
  Plotly.newPlot('Big Bend Elevation Table', [table1], tableLayout);

  /* Create the graph for Flow Spill */
  const graphFlowSpill = {
    x: times,
    y: flowSpill,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutFlowSpill = {
    title: 'Big Bend Flow Spill',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Flow Spill'}
  };
  Plotly.newPlot('Big Bend Flow Spill', [graphFlowSpill], layoutFlowSpill);

  /* Create the table for Flow Spill */
  const mean2 = getMean(flowSpill).toFixed(3);
  const sd2 = getStandardDeviation(flowSpill).toFixed(3);
  const median2 = getMedian(flowSpill).toFixed(3);
  const min2 = Math.min(...flowSpill).toFixed(3);
  const max2 = Math.max(...flowSpill).toFixed(3);
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
  Plotly.newPlot('Big Bend Flow Spill Table', [table2], tableLayout);

  /* Create the graph for Flow Powerhouse */
  const graphFlowPowerhouse = {
    x: times,
    y: flowPowerhouse,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutFlowPowerhouse = {
    title: 'Big Bend Flow Powerhouse',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Flow Powerhouse'}
  };
  Plotly.newPlot('Big Bend Flow Powerhouse', [graphFlowPowerhouse], layoutFlowPowerhouse);

  /* Create the table for Flow Powerhouse */
  const mean3 = getMean(flowPowerhouse).toFixed(3);
  const sd3 = getStandardDeviation(flowPowerhouse).toFixed(3);
  const median3 = getMedian(flowPowerhouse).toFixed(3);
  const min3 = Math.min(...flowPowerhouse).toFixed(3);
  const max3 = Math.max(...flowPowerhouse).toFixed(3);
  const range3 = (max3 - min3).toFixed(3);
  const statistics3 = [mean3, sd3, median3, min3, max3, range3];
  const table3 = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics3,
      align: 'center',
    }
  };
  Plotly.newPlot('Big Bend Flow Powerhouse Table', [table3], tableLayout);

  /* Create the graph for Flow Out */
  const graphFlowOut = {
    x: times,
    y: flowOut,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutFlowOut = {
    title: 'Big Bend Flow Out',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Flow Out'}
  };
  Plotly.newPlot('Big Bend Flow Out', [graphFlowOut], layoutFlowOut);

  /* Create the table for Flow Out */
  const mean4 = getMean(flowOut).toFixed(3);
  const sd4 = getStandardDeviation(flowOut).toFixed(3);
  const median4 = getMedian(flowOut).toFixed(3);
  const min4 = Math.min(...flowOut).toFixed(3);
  const max4 = Math.max(...flowOut).toFixed(3);
  const range4 = (max4 - min4).toFixed(3);
  const statistics4 = [mean4, sd4, median4, min4, max4, range4];
  const table4 = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics4,
      align: 'center',
    }
  };
  Plotly.newPlot('Big Bend Flow Out Table', [table4], tableLayout);

  /* Create the graph for Elev Tailwater */
  const graphElevTailwater = {
    x: times,
    y: elevTailwater,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutElevTailwater = {
    title: 'Big Bend Tailwater Elevation',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Elevation'}
  };
  Plotly.newPlot('Big Bend Tailwater Elevation', [graphElevTailwater], layoutElevTailwater);

  /* Create the table for Elev Tailwater */
  const mean5 = getMean(elevTailwater).toFixed(3);
  const sd5 = getStandardDeviation(elevTailwater).toFixed(3);
  const median5 = getMedian(elevTailwater).toFixed(3);
  const min5 = Math.min(...elevTailwater).toFixed(3);
  const max5 = Math.max(...elevTailwater).toFixed(3);
  const range5 = (max5 - min5).toFixed(3);
  const statistics5 = [mean5, sd5, median5, min5, max5, range5];
  const table5 = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics5,
      align: 'center',
    }
  };
  Plotly.newPlot('Big Bend Tailwater Elevation Table', [table5], tableLayout);

  /* Create the graph for Energy */
  const graphEnergy = {
    x: times,
    y: energy,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutEnergy = {
    title: 'Big Bend Energy',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Energy'}
  };
  Plotly.newPlot('Big Bend Energy', [graphEnergy], layoutEnergy);

  /* Create the table for Energy */
  const mean6 = getMean(energy).toFixed(3);
  const sd6 = getStandardDeviation(energy).toFixed(3);
  const median6 = getMedian(energy).toFixed(3);
  const min6 = Math.min(...energy).toFixed(3);
  const max6 = Math.max(...energy).toFixed(3);
  const range6 = (max6 - min6).toFixed(3);
  const statistics6 = [mean6, sd6, median6, min6, max6, range6];
  const table6 = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics6,
      align: 'center',
    }
  };
  Plotly.newPlot('Big Bend Energy Table', [table6], tableLayout);

  /* Create the graph for Temp Water */
  const graphtempWater = {
    x: times,
    y: tempWater,
    mode: 'lines',
    type: 'scatter'
  };
  const layouttempWater = {
    title: 'Big Bend Water Temperature',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Temperature'}
  };
  Plotly.newPlot('Big Bend Water Temperature', [graphtempWater], layouttempWater);

  /* Create the table for Temp Water */
  const mean7 = getMean(tempWater).toFixed(3);
  const sd7 = getStandardDeviation(tempWater).toFixed(3);
  const median7 = getMedian(tempWater).toFixed(3);
  const min7 = Math.min(...tempWater).toFixed(3);
  const max7 = Math.max(...tempWater).toFixed(3);
  const range7 = (max7 - min7).toFixed(3);
  const statistics7 = [mean7, sd7, median7, min7, max7, range7];
  const table7 = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics7,
      align: 'center',
    }
  };
  Plotly.newPlot('Big Bend Water Temperature Table', [table7], tableLayout);
      
  /* Create the graph for Temp Air */
  const graphtempAir = {
    x: times,
    y: tempAir,
    mode: 'lines',
    type: 'scatter'
  };
  const layouttempAir = {
    title: 'Big Bend Air Temperature',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Temperature'}
  };
  Plotly.newPlot('Big Bend Air Temperature', [graphtempAir], layouttempAir);

  /* Create the table for Temp Air */
  const mean8 = getMean(tempAir).toFixed(3);
  const sd8 = getStandardDeviation(tempAir).toFixed(3);
  const median8 = getMedian(tempAir).toFixed(3);
  const min8 = Math.min(...tempAir).toFixed(3);
  const max8 = Math.max(...tempAir).toFixed(3);
  const range8 = (max8 - min8).toFixed(3);
  const statistics8 = [mean8, sd8, median8, min8, max8, range8];
  const table8 = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics8,
      align: 'center',
    }
  };
  Plotly.newPlot('Big Bend Air Temperature Table', [table8], tableLayout);
})