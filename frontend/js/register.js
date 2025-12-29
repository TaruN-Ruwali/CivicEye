function handleRegister(event) {
  event.preventDefault();

  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirm = document.getElementById("confirm").value;

  if (password !== confirm) {
    alert("Passwords do not match!");
    return;
  }

  // TODO – integrate Flask API later
  console.log("Register Attempt:", name, email, password);

  alert("Registration submitted ✔ (Backend integration pending)");

  // Redirect to Login Page
  window.location.href = "./index.html";
}
