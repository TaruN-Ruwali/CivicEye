// Dummy complaints data (replace with backend fetch later)
let complaints = [
  { id: 1, img: "./assets/login-art.png", desc: "Pothole on road", location: "Sector 1", status: "Pending" },
  { id: 2, img: "./assets/login-art.png", desc: "Garbage unattended", location: "Sector 2", status: "In-Progress" },
  { id: 3, img: "./assets/login-art.png", desc: "Water leakage", location: "Sector 3", status: "Resolved" }
];

function loadAdminTable() {
  const body = document.getElementById("admin-table-body");
  body.innerHTML = "";

  complaints.forEach((c) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><img src="${c.img}" /></td>
      <td>${c.desc}</td>
      <td>${c.location}</td>
      <td>
        <select class="status-select" id="status-${c.id}">
          <option ${c.status === "Pending" ? "selected" : ""}>Pending</option>
          <option ${c.status === "In-Progress" ? "selected" : ""}>In-Progress</option>
          <option ${c.status === "Resolved" ? "selected" : ""}>Resolved</option>
        </select>
      </td>
      <td>
        <button class="update-btn" onclick="updateStatus(${c.id})">Update</button>
      </td>
    `;
    body.appendChild(row);
  });
}

function updateStatus(id) {
  const newStatus = document.getElementById(`status-${id}`).value;
  const item = complaints.find(c => c.id === id);
  item.status = newStatus;

  alert(`Complaint #${id} updated to: ${newStatus}`);
  console.log("Updated:", complaints);
}

function logout() {
  alert("Logged out");
  window.location.href = "./index.html";
}

loadAdminTable();
