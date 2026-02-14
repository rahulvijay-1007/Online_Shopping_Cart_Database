async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    });

    const data = await res.json();
    console.log("Login response:", data);

    if (!res.ok) {
      alert("Login failed: " + (data.detail || res.status));
      return;
    }

    localStorage.setItem("token", data.access_token);
    window.location.href = "products.html";

  } catch (err) {
    console.error("Login error:", err);
    alert("Login request failed");
  }
}
