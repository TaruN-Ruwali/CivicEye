function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  // Temporary mock logic (backend will replace later)
  if (email === "admin@civiceye.com" && password === "admin123") {
    alert("Welcome Admin");
    window.location.href = "./admin.html";
    return;
  }

  // normal user
  alert("Login Successful ✔");
  window.location.href = "./home.html";
}
