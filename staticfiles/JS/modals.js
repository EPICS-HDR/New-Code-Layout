map.on('load', function () {
  map.resize();
});
map.on('load', function () {

var lat = [47.2852816, 47.287222, 47.2888822, 47.07971406, 46.8338827, 46.81416667, 46.7033333, 46.3761111, 
45.6486883, 45.7119422, 45.2558171, 46.65638889, 42.74844444,];

var lon = [-101.6221093, -101.3397222, -101.0379239, -100.9323594, -100.9745789, -100.8213889, -101.2136111, 
-100.93444, -102.6433259, -100.5593015, -100.8429214, -100.7391667, -98.058,];

var text = ['Knife River at Hazen ND', 'Missouri River Near Stanton ND', 'Missouri River at Washburn ND', 
'Missouri River at Price ND', 'Heart River near Mandan ND', 'Missouri River at Bismarck', 'Heart River at Stark Bridge near Judson', 
'Cannonball River at Breien', 'NF Grand River near Cash SD', 'Oak Creek at Wakpala', 'Moreau River near Whitehorse SD', 
'Missouri River at Schmidt ND', 'Grand River near Little Eagle SD',];

for (var i = 0; i < lat.length; i++) {
var marker = new mapboxgl.Marker({ color: 'green' })
  .setLngLat([lon[i], lat[i]])
  .addTo(map);

function closeModal() {
  var modals = document.querySelectorAll('.modal');
  for (var i = 0; i < modals.length; i++) {
    modals[i].style.display = 'none';
  }
}

if (text[i] === 'Knife River at Hazen ND') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
   // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Hazen').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Hazen');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});   
}
if (text[i] === 'Missouri River Near Stanton ND') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
  // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Stanton').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Stanton');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});
}
if (text[i] === 'Missouri River at Washburn ND') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
  // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Washburn').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Washburn');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});
}
if (text[i] === 'Missouri River at Price ND') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
  // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Price').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Price');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});
}
if (text[i] === 'Heart River near Mandan ND') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
  // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Mandan').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Mandan');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});
}
if (text[i] === 'Missouri River at Bismarck') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
  // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Bismarck').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Bismarck');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});
}
if (text[i] === 'Heart River at Stark Bridge near Judson') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
  // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Judson').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Judson');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});
}
if (text[i] === 'Cannonball River at Breien') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
  // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Breien').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Breien');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});
}
if (text[i] === 'Missouri River at Schmidt ND') {
// Add click event listener to the marker
marker.getElement().addEventListener('click', function() {
  // Close any open modals
  closeModal();
  // Show the modal
  document.getElementById('Schmidt').style.display = 'block';

// Get the modal and the close button
var modal = document.getElementById('Schmidt');
var closeButton = modal.querySelector('.close');

// Add a click event listener to the close button to close the modal
closeButton.addEventListener('click', function() {
  modal.style.display = 'none';
});
});
}
}
});