const tableHeaderValues = ['Mean', 'SD', 'Median', 'Minimum', 'Maximum', 'Range'];

const tableLayout = {
    margin: {
        l: 0,
        r: 0,
        b: 0,
        /* Adds space between graph (above) and table (below). */
        t: 15
    },
    /* Overrides default Plotly.js table height. */
    height: 90
};

function getMean (array) {
    sum = 0;
    num = 0;
    for (let i = 0; i < array.length; i++) {
      sum += array[i];
      num += 1;
    }
    return sum / num;
}

function getStandardDeviation (array) {
    const n = array.length;
    const mean = array.reduce((a, b) => a + b) / n;
    return Math.sqrt(array.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n);
}

function getMedian (array) {
    const mid = Math.floor(array.length / 2);
    nums = array.sort((a, b) => a - b);
    return array.length % 2 !== 0 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2;
}