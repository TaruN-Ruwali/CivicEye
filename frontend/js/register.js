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

  console.log("Register Attempt:", name, email, password);

  fetch("/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ name, email, password })
  })
  .then(response => response.json())
  .then(data => {
    if (data.ok) {
      alert("Registration Successful! Please login.");
      window.location.href = "./login.html";
    } else {
      alert("Registration Failed: " + (data.error || "Unknown error"));
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("An error occurred during registration.");
  });
}
