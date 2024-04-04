/* Load the JSON data from the file */
fetch(CARSON_URL)

.then(response => response.json())
.then(data => {
  /* Extract the data from the JSON object */
  const [times, avgAirTemp, AvgRelHum, AvgBSTemp, AvgTSTemp, maxWind, AvgWindDir, totalSR, totalRainFall, AvgBaroPres, AvgDewP, AvgWindChill] = data;

  /* Create the graph for Average Air Temperature */
  const graphAirTemp = {
    x: times,
    y: avgAirTemp,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutAirTemp = {
    title: 'Carson Average Air Temperature',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Degrees Fahrenheit'}
  };
  Plotly.newPlot('Carson Average Air Temperature', [graphAirTemp], layoutAirTemp);

  /* Create the table for Average Air Temperature */
  const mean1 = getMean(avgAirTemp).toFixed(3);
  const sd1 = getStandardDeviation(avgAirTemp).toFixed(3);
  const median1 = getMedian(avgAirTemp).toFixed(3);
  const min1 = Math.min(...avgAirTemp).toFixed(3);
  const max1 = Math.max(...avgAirTemp).toFixed(3);
  const range1 = (max1 - min1).toFixed(3);
  const statistics1 = [mean1, sd1, median1, min1, max1, range1];
  const tableAirTemp = {
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
  Plotly.newPlot('Carson Average Air Temperature Table', [tableAirTemp], tableLayout);

  /* Create the graph for Relative Humidity */
  const graphRelativeHumidity = {
    x: times,
    y: AvgRelHum,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutRelativeHumidity = {
    title: 'Carson Average Relative Humidity',
    xaxis: {title: 'Time'},
    yaxis: {title: '% Humidity'}
  };
  Plotly.newPlot('Carson Average Relative Humidity', [graphRelativeHumidity], layoutRelativeHumidity);

  /* Create the table for Relative Humidity */
  const mean2 = getMean(AvgRelHum).toFixed(3);
  const sd2 = getStandardDeviation(AvgRelHum).toFixed(3);
  const median2 = getMedian(AvgRelHum).toFixed(3);
  const min2 = Math.min(...AvgRelHum).toFixed(3);
  const max2 = Math.max(...AvgRelHum).toFixed(3);
  const range2 = (max2 - min2).toFixed(3);
  const statistics2 = [mean2, sd2, median2, min2, max2, range2];
  const tableRelativeHumidity = {
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
  Plotly.newPlot('Carson Average Relative Humidity Table', [tableRelativeHumidity], tableLayout);

  /* Create the graph for Average Bare Soil Temperature */
  const graphAverageBareSoil = {
    x: times,
    y: AvgBSTemp,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutAverageBareSoil = {
    title: 'Carson Average Bare Soil Temperature',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Degrees Fahrenheit'}
  };
  Plotly.newPlot('Carson Average Bare Soil Temperature', [graphAverageBareSoil], layoutAverageBareSoil);

  /* Create the table for Average Bare Soil Temperature */
  const mean3 = getMean(AvgBSTemp).toFixed(3);
  const sd3 = getStandardDeviation(AvgBSTemp).toFixed(3);
  const median3 = getMedian(AvgBSTemp).toFixed(3);
  const min3 = Math.min(...AvgBSTemp).toFixed(3);
  const max3 = Math.max(...AvgBSTemp).toFixed(3);
  const range3 = (max3 - min3).toFixed(3);
  const statistics3 = [mean3, sd3, median3, min3, max3, range3];
  const tableAverageBareSoil = {
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
  Plotly.newPlot('Carson Average Bare Soil Temperature Table', [tableAverageBareSoil], tableLayout);

  /* Create the graph for Average Turf Soil Temperature */
  const graphAverageTurfSoil = {
    x: times,
    y: AvgTSTemp,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutAverageTurfSoil = {
    title: 'Carson Average Turf Soil Temperature',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Degrees Fahrenheit'}
  };
  Plotly.newPlot('Carson Average Turf Soil Temperature', [graphAverageTurfSoil], layoutAverageTurfSoil);

  /* Create the table for Average Turf Soil Temperature */
  const mean4 = getMean(AvgTSTemp).toFixed(3);
  const sd4 = getStandardDeviation(AvgTSTemp).toFixed(3);
  const median4 = getMedian(AvgTSTemp).toFixed(3);
  const min4 = Math.min(...AvgTSTemp).toFixed(3);
  const max4 = Math.max(...AvgTSTemp).toFixed(3);
  const range4 = (max4 - min4).toFixed(3);
  const statistics4 = [mean4, sd4, median4, min4, max4, range4];
  const tableAverageTurfSoil = {
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
  Plotly.newPlot('Carson Average Turf Soil Temperature Table', [tableAverageTurfSoil], tableLayout);

  /* Create the graph for Max Wind Speed */
  const graphMaxWind = {
    x: times,
    y: maxWind,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutMaxWind = {
    title: 'Carson Max Wind Speed',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Miles Per Hour'}
  };
  Plotly.newPlot('Carson Max Wind Speed', [graphMaxWind], layoutMaxWind);

  /* Create the table for Max Wind Speed */
  const mean5 = getMean(maxWind).toFixed(3);
  const sd5 = getStandardDeviation(maxWind).toFixed(3);
  const median5 = getMedian(maxWind).toFixed(3);
  const min5 = Math.min(...maxWind).toFixed(3);
  const max5 = Math.max(...maxWind).toFixed(3);
  const range5 = (max5 - min5).toFixed(3);
  const statistics5 = [mean5, sd5, median5, min5, max5, range5];
  const tableMaxWind = {
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
  Plotly.newPlot('Carson Max Wind Speed Table', [tableMaxWind], tableLayout);

  /* Create the graph for Average Wind Direction */
  const graphAvgWindDir = {
    x: times,
    y: AvgWindDir,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutAvgWindDir = {
    title: 'Carson Average Wind Direction',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Degrees'}
  };
  Plotly.newPlot('Carson Average Wind Direction', [graphAvgWindDir], layoutAvgWindDir);

  /* Create the table for Average Wind Direction */
  const mean6 = getMean(AvgWindDir).toFixed(3);
  const sd6 = getStandardDeviation(AvgWindDir).toFixed(3);
  const median6 = getMedian(AvgWindDir).toFixed(3);
  const min6 = Math.min(...AvgWindDir).toFixed(3);
  const max6 = Math.max(...AvgWindDir).toFixed(3);
  const range6 = (max6 - min6).toFixed(3);
  const statistics6 = [mean6, sd6, median6, min6, max6, range6];
  const tableAvgWindDir = {
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
  Plotly.newPlot('Carson Average Wind Direction Table', [tableAvgWindDir], tableLayout);
    
  /* Create the graph for Total Solar Radiation */
  const graphTotalSR = {
    x: times,
    y: totalSR,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutTotalSR = {
    title: 'Carson Total Solar Radiation',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Langleys'}
  };
  Plotly.newPlot('Carson Total Solar Radiation', [graphTotalSR], layoutTotalSR);

  /* Create the table for Total Solar Radiation */
  const mean7 = getMean(avgAirTemp).toFixed(3);
  const sd7 = getStandardDeviation(avgAirTemp).toFixed(3);
  const median7 = getMedian(avgAirTemp).toFixed(3);
  const min7 = Math.min(...avgAirTemp).toFixed(3);
  const max7 = Math.max(...avgAirTemp).toFixed(3);
  const range7 = (max7 - min7).toFixed(3);
  const statistics7 = [mean7, sd7, median7, min7, max7, range7];
  const tableTotalSR = {
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
  Plotly.newPlot('Carson Total Solar Radiation Table', [tableTotalSR], tableLayout);

  /* Create the graph for Total Rainfall */
  const graphRainfall = {
    x: times,
    y: totalRainFall,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutRainfall = {
    title: 'Carson Total Rainfall',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Inches'}
  };
  Plotly.newPlot('Carson Total Rainfall', [graphRainfall], layoutRainfall);
  
  /* Create the table for Total Rainfall */
  const mean8 = getMean(totalRainFall).toFixed(3);
  const sd8 = getStandardDeviation(totalRainFall).toFixed(3);
  const median8 = getMedian(totalRainFall).toFixed(3);
  const min8 = Math.min(...totalRainFall).toFixed(3);
  const max8 = Math.max(...totalRainFall).toFixed(3);
  const range8 = (max8 - min8).toFixed(3);
  const statistics8 = [mean8, sd8, median8, min8, max8, range8];
  const tableRainfall = {
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
  Plotly.newPlot('Carson Total Rainfall Table', [tableRainfall], tableLayout);

  /* Create the graph for Average Barometric Pressure */
  const graphBaroPres = {
    x: times,
    y: AvgBaroPres,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutBaroPres = {
    title: 'Carson Average Barometric Pressure',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Millibars'}
  };
  Plotly.newPlot('Carson Average Barometric Pressure', [graphBaroPres], layoutBaroPres);

  /* Create the table for Average Barometric Pressure */
  const mean9 = getMean(AvgBaroPres).toFixed(3);
  const sd9 = getStandardDeviation(AvgBaroPres).toFixed(3);
  const median9 = getMedian(AvgBaroPres).toFixed(3);
  const min9 = Math.min(...AvgBaroPres).toFixed(3);
  const max9 = Math.max(...AvgBaroPres).toFixed(3);
  const range9 = (max9 - min9).toFixed(3);
  const statistics9 = [mean9, sd9, median9, min9, max9, range9];
  const tableBaroPres = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics9,
      align: 'center',
    }
  };
  Plotly.newPlot('Carson Average Barometric Pressure Table', [tableBaroPres], tableLayout);

  /* Create the graph for Average Dew Point */
  const graphAvgDew = {
    x: times,
    y: AvgDewP,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutAvgDew = {
    title: 'Carson Average Dew Point',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Degrees Fahrenheit'}
  };
  Plotly.newPlot('Carson Average Dew Point', [graphAvgDew], layoutAvgDew);

  /* Create the table for Average Dew Point */
  const mean10 = getMean(AvgDewP).toFixed(3);
  const sd10 = getStandardDeviation(AvgDewP).toFixed(3);
  const median10 = getMedian(AvgDewP).toFixed(3);
  const min10 = Math.min(...AvgDewP).toFixed(3);
  const max10 = Math.max(...AvgDewP).toFixed(3);
  const range10 = (max10 - min10).toFixed(3);
  const statistics10 = [mean10, sd10, median10, min10, max10, range10];
  const tableAvgDew = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics10,
      align: 'center',
    }
  };
  Plotly.newPlot('Carson Average Dew Point Table', [tableAvgDew], tableLayout);

  /* Create the graph for Average Wind Chill */
  const graphAvgWindChill = {
    x: times,
    y: AvgWindChill,
    mode: 'lines',
    type: 'scatter'
  };
  const layoutAvgWindChill = {
    title: 'Carson Average Wind Chill',
    xaxis: {title: 'Time'},
    yaxis: {title: 'Degrees Fahrenheit'}
  };
  Plotly.newPlot('Carson Average Wind Chill', [graphAvgWindChill], layoutAvgWindChill);

  /* Create the table for Average Wind Chill */
  const mean11 = getMean(AvgWindChill).toFixed(3);
  const sd11 = getStandardDeviation(AvgWindChill).toFixed(3);
  const median11 = getMedian(AvgWindChill).toFixed(3);
  const min11 = Math.min(...AvgWindChill).toFixed(3);
  const max11 = Math.max(...AvgWindChill).toFixed(3);
  const range11 = (max11 - min11).toFixed(3);
  const statistics11 = [mean11, sd11, median11, min11, max11, range11];
  const tableAvgWindChill = {
    type: 'table',
    header: {
      values: tableHeaderValues,
      align: 'center',
    },
    cells: {
      values: statistics11,
      align: 'center',
    }
  };
  Plotly.newPlot('Carson Average Wind Chill Table', [tableAvgWindChill], tableLayout);
})