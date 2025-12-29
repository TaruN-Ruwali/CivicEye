function previewImage(event) {
  const output = document.getElementById("preview");
  output.src = URL.createObjectURL(event.target.files[0]);
}

function handleSubmit(event) {
  event.preventDefault();

  const image = document.getElementById("image").files[0];
  const desc = document.getElementById("desc").value;
  const location = document.getElementById("location").value;

  if (!image) return alert("Please select an image");

  // Eventually send to backend using Flask API
  console.log("Complaint Submitted ->", { image, desc, location });

  alert("Complaint submitted ✔ (Backend integration pending)");

  // Redirect to status page
  window.location.href = "./status.html";
}
