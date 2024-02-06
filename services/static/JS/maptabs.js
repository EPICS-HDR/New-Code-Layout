function initMap() {
    const dakotaBorder = {
      north: 49.5121,
      south: 42.4796,
      east: -95.5603,
      west: -107.0577
    };
  
    const mapStyles = [
      {
        featureType: 'road',
        elementType: 'geometry',
        stylers: [{ visibility: 'off' }]  // Turn off roads
      },
      {
        featureType: 'water',
        elementType: 'geometry',
        stylers: [{ color: '#aedbf3' }]  // Set water color to light blue
      },
      {
        featureType: 'landscape',
        elementType: 'geometry',
        stylers: [{ color: '#d5f5e3' }]  // Set landscape color to light green
      },
      {
        featureType: 'landscape.natural.terrain',
        elementType: 'geometry',
        stylers: [{ color: '#aafaa1' }]  // Set natural terrain color to a different green shade
      }
    ];
  
    // Initialize the map
    map = new google.maps.Map(document.getElementById('map'), {
      center: { lat: (dakotaBorder.north + dakotaBorder.south) / 2, lng: (dakotaBorder.east + dakotaBorder.west) / 2 },
      zoom: 6,
      disableDefaultUI: true,
      styles: mapStyles,
      restriction: {
        latLngBounds: dakotaBorder,
        strictBounds: true
      }
    });
  
}

