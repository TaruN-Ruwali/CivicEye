// Dummy complaints until backend connects
const complaints = [
  { id: 1, image: "./assets/iPad Chor logo.png", status: "Pending" },
  { id: 2, image: "./assets/Potholes.png", status: "In-Progress" },
  { id: 3, image: "./assets/login-art.png", status: "Resolved" },
];

function loadComplaints() {
  const list = document.getElementById("complaint-list");
  list.innerHTML = "";

  complaints.forEach((c) => {
    const div = document.createElement("div");
    div.className = "complaint-item";
    div.innerHTML = `
      <div>
        <img src="${c.image}" />
      </div>
      <span class="status-badge ${c.status.toLowerCase().replace(" ", "-")}">
        ${c.status}
      </span>
    `;
    div.onclick = () => showPreview(c.image);
    list.appendChild(div);
  });
}

function showPreview(src) {
  document.getElementById("preview-img").src = src;
}

function refreshComplaints() {
  alert("In real project, this will fetch updated data from backend.");
  loadComplaints();
}

// First load
loadComplaints();
