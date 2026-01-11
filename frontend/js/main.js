function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  // TODO – integrate Flask API later
  console.log("Login Attempt:", email, password);

  fetch("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, password })
  })
  .then(response => response.json())
  .then(data => {
    if (data.ok && data.user) {
      // Store user information in localStorage
      localStorage.setItem("user_id", data.user.id);
      localStorage.setItem("user_name", data.user.name || "");
      localStorage.setItem("user_role", data.user.role || "user");
      
      alert("Login Successful!");
      if (data.user.role === "admin") {
        window.location.href = "./admin.html";
      } else {
        window.location.href = "./home.html";
      }
    } else {
      alert("Login Failed: " + (data.error || "Invalid credentials"));
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("An error occurred during login.");
  });
}
