map.on('load', function () {
    map.resize();
  });
  map.on('load', function () {
  
  var lat = [44.4512927, 44.0516567, 43.0661976, 42.8619, 47.4949814, 48.0027953];
  
  var lon = [-100.4043407, -99.4545179, -98.5366157, -97.4853, -101.4162492, -106.4183359];
  
  var text = ['Oahe Dam', 'Big Bend Dam', 'Fort Randall Dam', 'Gavins Point Dam', 'Garrison Dam', 'Fork Peck Dam'];

  var markers = [];
  
  for (var i = 0; i < lat.length; i++) {
  var marker = new mapboxgl.Marker({ color: 'blue' })
    .setLngLat([lon[i], lat[i]])
    .addTo(map);

  function closeModal() {
    var modals = document.querySelectorAll('.modal');
    for (var i = 0; i < modals.length; i++) {
      modals[i].style.display = 'none';
    }
  }
  
  if (text[i] === 'Oahe Dam') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
     // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Oahe').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Oahe');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });   
  }
  if (text[i] === 'Big Bend Dam') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Big Bend').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Big Bend');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Fort Randall Dam') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Fort Randall').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Fort Randall');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Gavins Point Dam') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Gavins Point').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Gavins Point');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Garrison Dam') {
    // Add click event listener to the marker
    marker.getElement().addEventListener('click', function() {
      // Close any open modals
      closeModal();
      // Show the modal
      document.getElementById('Garrison').style.display = 'block';
    
    // Get the modal and the close button
    var modal = document.getElementById('Garrison');
    var closeButton = modal.querySelector('.close');
    
    // Add a click event listener to the close button to close the modal
    closeButton.addEventListener('click', function() {
      modal.style.display = 'none';
    });
    });
    }
    if (text[i] === 'Fork Peck Dam') {
      // Add click event listener to the marker
      marker.getElement().addEventListener('click', function() {
        // Close any open modals
        closeModal();
        // Show the modal
        document.getElementById('Fort Peck').style.display = 'block';
      
      // Get the modal and the close button
      var modal = document.getElementById('Fort Peck');
      var closeButton = modal.querySelector('.close');
      
      // Add a click event listener to the close button to close the modal
      closeButton.addEventListener('click', function() {
        modal.style.display = 'none';
      });
      });
    }

  }
  });