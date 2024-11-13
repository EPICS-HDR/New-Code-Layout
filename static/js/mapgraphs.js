  //'Hazen' , 'Judson' , BigBend', 'Bismark', and 'Breien'

  function plotLocationData(url, locationName) {

    fetch(url)
    
    .then(response => response.json())
    
    .then(data => {
    
        const [times1, elevations1, times2, gheights2, times3, discharge] = data;
    
    
        const titles = [
    
            `${locationName} Elevation`,
    
            `${locationName} Gauge Height`,
    
            `${locationName} Discharge`
    
        ];
    
        const yTitles = ['Elevation', 'Gauge Height', 'Discharge'];
    
        const dataSets = [elevations1, gheights2, discharge];
    
        const ids = [
    
            `${locationName} Elevation`,
    
            `${locationName} Gauge Height`,
    
            `${locationName} Discharge`
    
        ];
    
        const tableIds = [
    
            `${locationName} Elevation Table`,
    
            `${locationName} Gauge Height Table`,
    
            `${locationName} Discharge Table`
    
        ];
    
    
        dataSets.forEach((dataSet, index) => {
    
            const graph = {
    
                x: times1,
    
                y: dataSet,
    
                mode: 'lines',
    
                type: 'scatter'
    
            };
    
    
            const layout = {
    
                title: titles[index],
    
                xaxis: {title: 'Time'},
    
                yaxis: {title: yTitles[index]}
    
            };
    
    
            Plotly.newPlot(ids[index], [graph], layout);
    
    
            const mean = getMean(dataSet).toFixed(3);
    
            const sd = getStandardDeviation(dataSet).toFixed(3);
    
            const median = getMedian(dataSet).toFixed(3);
    
            const min = Math.min(...dataSet).toFixed(3);
    
            const max = Math.max(...dataSet).toFixed(3);
    
            const range = (max - min).toFixed(3);
    
            const statistics = [mean, sd, median, min, max, range];
    
    
            const table = {
    
                type: 'table',
    
                header: {
    
                    values: tableHeaderValues,
    
                    align: 'center',
    
                },
    
                cells: {
    
                    values: statistics,
    
                    align: 'center',
    
                }
    
            };
    
    
            Plotly.newPlot(tableIds[index], [table], tableLayout);
    
        });
    
    });
    
    }
    
    
    // Call the function for each location
    
    plotLocationData(JUDSON_URL, 'Judson');
    
    plotLocationData(HAZENGRAPHS_URL, 'Hazen');
    
    plotLocationData(BIGBEND_URL, 'BigBend');
    
    plotLocationData(BISMARCK_URL, 'Bismarck');
    
    plotLocationData(BREIEN_URL, 'Breien');