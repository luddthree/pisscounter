var map = L.map('map').fitWorld();

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var markers = [];

map.on('click', function(e) {
  var lat = e.latlng.lat;
  var lon = e.latlng.lng;

  // Use the 'username' variable instead of a static string
  var popupContent = username + " pissed here";

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

  // Define a custom icon for the "Your Location" marker
  var locationIcon = L.icon({
      iconUrl: 'static/homemarker.png', // Replace with the path to your custom marker icon
      iconSize: [22, 32], // Set the icon size as needed
      iconAnchor: [16, 32], // Adjust the icon anchor if needed
  });

  // Add a marker at the user's location with the custom icon
  L.marker([lat, lon], { icon: locationIcon }).addTo(map)
    .bindPopup('Your Location')
    .openPopup();

  // Center the map on the user's location
  map.setView([lat, lon], 13);
});