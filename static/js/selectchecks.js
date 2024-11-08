// get references to select element and containers
const selectElement = document.querySelector('#data2see');
const gaugeHeightContainer = document.querySelector('#gaugeContainer');
const elevationContainer = document.querySelector('#elevationContainer');
const dischargeContainer = document.querySelector('#dischargeContainer');
const waterTemperatureContainer = document.querySelector('#waterTemperatureContainer');

// add event listener to select element
selectElement.addEventListener('change', () => {
  // get selected option value
  const selectedValue = selectElement.value;
  
  // hide both containers
  gaugeHeightContainer.style.display = 'none';
  elevationContainer.style.display = 'none';
  dischargeContainer.style.display = 'none';
  waterTemperatureContainer.style.display = 'none';

  
  // show container for selected option
  if (selectedValue === 'Gauge Height') {
    gaugeHeightContainer.style.display = 'block';
  } else if (selectedValue === 'Elevation') {
    elevationContainer.style.display = 'block';
  } else if (selectedValue === 'Discharge') {
    dischargeContainer.style.display = 'block';
  } else if (selectedValue === 'Water Temperature') {
    waterTemperatureContainer.style.display = 'block';
  }
});