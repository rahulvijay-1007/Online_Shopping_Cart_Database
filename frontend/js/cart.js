const token = localStorage.getItem("token");

if (!token) {
  alert("Not logged in");
  window.location.href = "index.html";
}

function loadCart() {
  fetch(`${API_BASE_URL}/cart`, {
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(res => res.json())
    .then(data => {
      const cartDiv = document.getElementById("cart");

      if (!data.items || data.items.length === 0) {
        cartDiv.innerHTML = "<p>Cart is empty</p>";
        return;
      }

      cartDiv.innerHTML = "";

      data.items.forEach(item => {
        cartDiv.innerHTML += `
          <div class="cart-item">
            <span>${item.name}</span>

            <div class="qty-controls">
              <button onclick="updateQty(${item.product_id}, -1)">−</button>
              <span>${item.quantity}</span>
              <button onclick="updateQty(${item.product_id}, 1)">+</button>
            </div>

            <span>Rs. ${item.subtotal.toFixed(2)}</span>
          </div>
        `;
      });

      cartDiv.innerHTML += `
        <div class="cart-total">
          Total: Rs. ${data.total.toFixed(2)}
        </div>
      `;
    });
}

function updateQty(productId, delta) {
  fetch(`${API_BASE_URL}/cart`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: delta
    })
  }).then(() => loadCart());
}

function checkout() {
  fetch(`${API_BASE_URL}/orders/checkout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(res => {
      if (!res.ok) throw new Error();
      return res.json();
    })
    .then(() => {
      alert("Order placed successfully!");
      window.location.href = "products.html";
    });
}

loadCart();
