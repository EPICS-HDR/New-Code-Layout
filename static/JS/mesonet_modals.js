map.on('load', function () {
    map.resize();
  });
  map.on('load', function () {
  
  var lat = [46.084858, 46.38, 46.44303, 46.328, 45.92, 45.92, 45.8, 45.67, 45.42];
  
  var lon = [-100.676495, -102.322, -101.373829, -100.277, -102.11, -101.34, -100.78, -100.11, -101.08];
  
  var text = ['Fort Yates', 'Mott', 'Carson', 'Linton', 'Lemmon', 'McIntosh', 'Mclaughlin', 'Mound City', 'Timber Lake'];
  
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
  
  if (text[i] === 'Fort Yates') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
     // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Fort Yates').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Fort Yates');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });   
  }
  if (text[i] === 'Mott') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Mott').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Mott');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Carson') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Carson').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Carson');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Linton') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Linton').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Linton');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Lemmon') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Lemmon').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Lemmon');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'McIntosh') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('McIntosh').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('McIntosh');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Mclaughlin') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Mclaughlin').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Mclaughlin');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Mound City') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Mound City').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Mound City');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  if (text[i] === 'Timber Lake') {
  // Add click event listener to the marker
  marker.getElement().addEventListener('click', function() {
    // Close any open modals
    closeModal();
    // Show the modal
    document.getElementById('Timber Lake').style.display = 'block';
  
  // Get the modal and the close button
  var modal = document.getElementById('Timber Lake');
  var closeButton = modal.querySelector('.close');
  
  // Add a click event listener to the close button to close the modal
  closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  });
  }
  }
  });