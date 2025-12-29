function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  // TODO – integrate Flask API later
  console.log("Login Attempt:", email, password);

  alert("Login submitted ✔ (Backend integration pending)");
}
