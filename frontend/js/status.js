
// Check if user is logged in, redirect to login if not
function checkAuth() {
  const user_id = localStorage.getItem("user_id");
  if (!user_id) {
    alert("Please login to view your complaints.");
    window.location.href = "./login.html";
    return null;
  }
  return user_id;
}

// Get user_id from localStorage (set during login)
// If not available, redirect to login
function getUserId() {
  const user_id = checkAuth();
  if (!user_id) {
    return null;
  }
  return user_id;
}

function loadComplaints() {
  const list = document.getElementById("complaint-list");
  list.innerHTML = "<div style='padding: 20px; text-align: center;'>Loading complaints...</div>";

  const user_id = getUserId();
  if (!user_id) {
    return; // Already redirected to login
  }
  
  // Fetch complaints from backend API
  fetch(`/complaint/status/${user_id}`)
    .then(response => response.json())
    .then(data => {
      if (!data.ok) {
        list.innerHTML = `<div style='padding: 20px; color: red;'>Error: ${data.error || 'Failed to load complaints'}</div>`;
        return;
      }

      const complaints = data.complaints || [];
      
      if (complaints.length === 0) {
        list.innerHTML = "<div style='padding: 20px; text-align: center;'>No complaints found. Submit a new complaint to get started!</div>";
        return;
      }

      list.innerHTML = "";
      
      complaints.forEach((c) => {
        const div = document.createElement("div");
        div.className = "complaint-item";
        
        // Format status for display
        const status = c.status || "pending";
        const statusDisplay = status.charAt(0).toUpperCase() + status.slice(1);
        
        // Get image URL (prepend server path if relative)
        const imageUrl = c.image_path ? (c.image_path.startsWith("http") ? c.image_path : `/${c.image_path}`) : "./assets/login-art.png";
        
        // Format date
        const createdDate = c.created_at ? new Date(c.created_at).toLocaleDateString() : "N/A";
        
        div.innerHTML = `
          <div class="complaint-item-content">
            <div class="complaint-image">
              <img src="${imageUrl}" alt="Complaint image" onerror="this.src='./assets/login-art.png'" />
            </div>
            <div class="complaint-details">
              <div class="complaint-type"><strong>Type:</strong> ${c.complaint_type || "N/A"}</div>
              <div class="complaint-address"><strong>Address:</strong> ${c.address || "N/A"}</div>
              <div class="complaint-date"><strong>Date:</strong> ${createdDate}</div>
              ${c.ai_result ? `<div class="complaint-ai"><strong>AI Result:</strong> ${c.ai_result}</div>` : ""}
            </div>
            <span class="status-badge ${status.toLowerCase().replace("_", "-")}">
              ${statusDisplay}
            </span>
          </div>
        `;
        
        // Show full details on click
        div.onclick = () => showComplaintDetails(c, imageUrl);
        list.appendChild(div);
      });
    })
    .catch(error => {
      console.error("Error fetching complaints:", error);
      list.innerHTML = "<div style='padding: 20px; color: red;'>Error loading complaints. Please try again later.</div>";
    });
}

function showComplaintDetails(complaint, imageUrl) {
  // Update preview image
  document.getElementById("preview-img").src = imageUrl;
  
  // You can also show a modal or expand details here
  console.log("Complaint details:", complaint);
}

function showPreview(src) {
  document.getElementById("preview-img").src = src;
}

function refreshComplaints() {
  loadComplaints();
}

function logout() {
  localStorage.clear();
  window.location.href = "./login.html";
}

// Check authentication on page load
window.addEventListener("DOMContentLoaded", function() {
  const user_id = checkAuth();
  if (user_id) {
    loadComplaints();
  }
});
