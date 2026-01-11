function loadAdminTable() {
  const body = document.getElementById("admin-table-body");
  body.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";

  const admin_id = localStorage.getItem("user_id");
  if (!admin_id) {
    alert("Please login as admin first");
    window.location.href = "./login.html";
    return;
  }

  fetch("/admin/complaints")
    .then(response => response.json())
    .then(data => {
      body.innerHTML = "";
      if (!data.ok || !data.items || data.items.length === 0) {
        body.innerHTML = "<tr><td colspan='5'>No reports found</td></tr>";
        return;
      }

      data.items.forEach((c) => {
        const row = document.createElement("tr");
        // Use image_path from DB, or fallback
        const imgUrl = c.image_path ? "/" + c.image_path : "./assets/login-art.png";
        // Calculate score percentage if confidence exists
        const score = c.ai_confidence ? Math.round(c.ai_confidence * 100) : 0;
        
        row.innerHTML = `
          <td><img src="${imgUrl}" width="50" style="object-fit:cover; aspect-ratio:1" /></td>
          <td>CIVIC-${c.id} <br><small>(${c.complaint_type || 'General'})</small></td>
          <td>${c.address || c.location || 'N/A'}</td>
          <td>
            <select class="status-select" id="status-${c.id}" onchange="updateStatus('${c.id}')">
              <option value="pending" ${c.status === "pending" ? "selected" : ""}>Pending</option>
              <option value="verified" ${c.status === "verified" ? "selected" : ""}>Verified</option>
              <option value="resolved" ${c.status === "resolved" ? "selected" : ""}>Resolved</option>
              <option value="rejected" ${c.status === "rejected" ? "selected" : ""}>Rejected</option>
            </select>
            <br>
            <small>AI: ${score}%</small>
          </td>
          <td>
            <button class="update-btn" onclick="updateStatus('${c.id}')">Save</button>
            <button class="update-btn" style="margin-left:8px" onclick="reviewDecision('${c.id}')">Review AI</button>
          </td>
        `;
        body.appendChild(row);
      });
    })
    .catch(error => {
      console.error("Error fetching reports:", error);
      body.innerHTML = "<tr><td colspan='5'>Error loading reports</td></tr>";
    });
}

function updateStatus(id) {
  const newStatus = document.getElementById(`status-${id}`).value;
  const admin_id = localStorage.getItem("user_id");

  fetch("/admin/update_status", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      complaint_id: id,
      status: newStatus,
      admin_id: admin_id
    })
  })
  .then(res => res.json())
  .then(data => {
    if(data.ok) {
      alert("Status updated!");
    } else {
      alert("Failed to update: " + (data.error || "Unknown error"));
    }
  })
  .catch(err => console.error(err));
}

function logout() {
  localStorage.clear();
  alert("Logged out");
  window.location.href = "./login.html";
}

function reviewDecision(id) {
  window.location.href = `./decision.html?id=${id}`;
}

loadAdminTable();
