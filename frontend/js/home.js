// Check authentication on page load
function checkAuth() {
  const user_id = localStorage.getItem("user_id");
  if (!user_id) {
    alert("Please login to access the dashboard.");
    window.location.href = "./login.html";
    return false;
  }
  return true;
}

// Update welcome message with user name
function updateWelcomeMessage() {
  const userName = localStorage.getItem("user_name") || "User";
  const welcomeElement = document.querySelector(".dash-title");
  if (welcomeElement) {
    welcomeElement.textContent = `Welcome, ${userName} 👋`;
  }
}

// Check auth when page loads
window.addEventListener("DOMContentLoaded", function() {
  if (checkAuth()) {
    updateWelcomeMessage();
  }
});

function logout() {
  localStorage.clear();
  window.location.href = "./login.html";
}
