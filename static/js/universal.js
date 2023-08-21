var map = L.map('map').fitWorld();

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var markers = [];

map.on('click', function(e) {
  var lat = e.latlng.lat;
  var lon = e.latlng.lng;

  var popupContent = "Someone pissed here";

  var marker = L.marker([lat, lon]).addTo(map)
    .bindPopup(popupContent)
    .openPopup();

  marker.on('click', function() {
    map.removeLayer(marker);

    // Send a request to Flask to remove the marker from the database
    fetch('/remove_marker', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ lat, lon }),
    });

    // Remove the marker from the markers array
    markers = markers.filter(function(existingMarker) {
      return existingMarker !== marker;
    });
  });

  markers.push(marker);

  // Send the marker data to the server for saving
  fetch('/save_marker', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ lat, lon, popup: popupContent }),
  });
});

navigator.geolocation.getCurrentPosition(function(position) {
    var lat = position.coords.latitude;
    var lon = position.coords.longitude;

    // Add a marker at the user's location
    L.marker([lat, lon]).addTo(map)
      .bindPopup('Your Location')
      .openPopup();
    
    // Center the map on the user's location
    map.setView([lat, lon], 13);
  });