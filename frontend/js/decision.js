function getQueryId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

function logout() {
  localStorage.clear();
  window.location.href = "./login.html";
}

function setBadge(elementId, type) {
  const el = document.getElementById(elementId);
  const map = {
    garbage: "badge-garbage",
    pothole: "badge-pothole",
    water_leakage: "badge-water",
    unknown: "badge-unknown",
    pending: "badge-pending",
    verified: "badge-verified",
    rejected: "badge-rejected",
  };
  // reset classes
  el.className = "badge " + (map[type] || "badge-unknown");
  el.textContent = (type || "unknown").replace("_", " ").replace("-", " ").toUpperCase();
}

function renderDecision(item) {
  console.log("Rendering decision for item:", item);
  
  document.getElementById("complaint-id").textContent = `Complaint #CIVIC-${item.id}`;
  const ts = item.decision_timestamp || item.last_detection_at || item.created_at || "";
  document.getElementById("timestamp").textContent = ts ? new Date(ts).toLocaleString() : "";
  
  // Display the actual uploaded image
  const img = item.image_path ? `/${item.image_path}` : "./assets/AI DECISION.png";
  document.getElementById("image-preview").src = img;
  document.getElementById("image-preview").onerror = function() {
    this.src = "./assets/AI DECISION.png";
  };
  
  document.getElementById("address").textContent = item.address || item.location || "—";
  document.getElementById("description").textContent = item.description || "—";
  
  // AI Detection Type - prioritize ai_detected_type from database
  const dtype = item.ai_detected_type || item.last_detected_type || "unknown";
  setBadge("detected-type", dtype);
  
  // Confidence - use ai_confidence from database, fallback to last_confidence
  const conf = (item.ai_confidence !== null && item.ai_confidence !== undefined) 
    ? item.ai_confidence 
    : (item.last_confidence ?? 0);
  document.getElementById("confidence").textContent = `${Math.round((conf || 0) * 100)}%`;
  
  // AI Status - show current review status
  setBadge("ai-status", item.ai_status || "pending");
  
  // Show detected object label (what the model actually detected)
  const detectedLabel = item.last_model_name || item.ai_model_name || "N/A";
  document.getElementById("detected-label").textContent = detectedLabel;
  
  // Show all detector results if available
  if (item.detections || item.last_detected_type) {
    const resultsDiv = document.getElementById("detector-results");
    const detailsDiv = document.getElementById("detector-details");
    
    if (item.detections && Array.isArray(item.detections)) {
      resultsDiv.style.display = "block";
      let html = "";
      item.detections.forEach((det, idx) => {
        const type = det.detected_type || det.detector_name || "Unknown";
        const conf = (det.confidence || 0) * 100;
        const model = det.detector_name || "N/A";
        html += `<div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 5px;">
          <strong>${model}:</strong> ${type} (${conf.toFixed(1)}% confidence)
        </div>`;
      });
      detailsDiv.innerHTML = html || "<p>No detailed detection data available.</p>";
    }
  }
}

function loadDecision() {
  const id = getQueryId();
  if (!id) {
    alert("Missing complaint id");
    return;
  }
  
  // Check if user is logged in and is admin
  const admin_id = localStorage.getItem("user_id");
  const user_role = localStorage.getItem("user_role");
  
  if (!admin_id) {
    alert("Please login first");
    window.location.href = "./login.html";
    return;
  }
  
  if (user_role !== "admin") {
    alert("Access denied: Admin privileges required");
    window.location.href = "./login.html";
    return;
  }
  
  fetch(`/admin/complaint/${id}/ai-result`)
    .then((res) => res.json())
    .then((data) => {
      if (!data.ok || !data.item) {
        alert("Failed to load decision");
        return;
      }
      renderDecision(data.item);
    })
    .catch((e) => {
      console.error(e);
      alert("Error loading decision");
    });
}

function submitDecision(ai_status) {
  const id = getQueryId();
  const admin_id = localStorage.getItem("user_id");
  const user_role = localStorage.getItem("user_role");
  
  if (!admin_id) {
    alert("Please login as admin");
    window.location.href = "./login.html";
    return;
  }
  
  // Verify user is admin
  if (user_role !== "admin") {
    alert("Access denied: Admin privileges required");
    window.location.href = "./login.html";
    return;
  }
  
  const override_type = document.getElementById("override-type").value || null;
  
  // Ensure admin_id is sent as a number (localStorage stores as string)
  const payload = {
    ai_status: ai_status,
    override_type: override_type,
    admin_id: parseInt(admin_id, 10) || admin_id  // Convert to int if possible
  };
  
  console.log("Submitting decision:", payload);
  
  fetch(`/admin/complaint/${id}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((res) => {
      if (!res.ok) {
        // Try to get error message from response
        return res.json().then(data => {
          throw new Error(data.error || `HTTP ${res.status}: ${res.statusText}`);
        });
      }
      return res.json();
    })
    .then((data) => {
      if (data.ok) {
        alert("Decision saved successfully");
        loadDecision();
      } else {
        alert("Failed to save: " + (data.error || "Unknown error"));
      }
    })
    .catch((e) => {
      console.error("Error saving decision:", e);
      alert("Error saving decision: " + e.message);
    });
}

// Check admin access on page load
const user_role_check = localStorage.getItem("user_role");
if (user_role_check !== "admin") {
  alert("Access denied: Admin privileges required");
  window.location.href = "./login.html";
} else {
  loadDecision();
}
