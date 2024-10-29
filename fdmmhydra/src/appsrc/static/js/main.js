function updateZoomTooltip(level) {
  const zoomButton = document.getElementById('zoomButton');
  try {
    zoomButton.textContent = ` ${level}%`;
  } catch (error) {
    
  }
}

function toggleZoom(event) {
  let currentZoomLevel = parseFloat(localStorage.getItem('zoomLevel')) || 100;
  currentZoomLevel += 10;
  if (currentZoomLevel > 200) {
    currentZoomLevel = 100;
  }
  localStorage.setItem('zoomLevel', currentZoomLevel);
  document.body.style.zoom = currentZoomLevel + '%';
  updateZoomTooltip(currentZoomLevel);
}

$(document).ready(function(){
    let currentZoomLevel = parseFloat(localStorage.getItem('zoomLevel')) || 100;
    document.body.style.zoom = currentZoomLevel + '%';
    updateZoomTooltip(currentZoomLevel);
});

function deleteMessage(button) {
  // Traverse up the DOM to find the parent alert div and remove it
  var alertDiv = button.closest('.alert');
  if (alertDiv) {
    alertDiv.remove();
  }
};