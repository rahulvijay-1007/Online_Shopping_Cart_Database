const token = localStorage.getItem("token");

if (!token) {
  alert("Not logged in");
  window.location.href = "index.html";
}

fetch(`${API_BASE_URL}/orders/history`, {
  headers: {
    Authorization: `Bearer ${token}`
  }
})
  .then(res => {
    if (!res.ok) {
      throw new Error("Failed to fetch orders");
    }
    return res.json();
  })
  .then(data => {
    const ordersDiv = document.getElementById("orders");

    if (!data.orders || data.orders.length === 0) {
      ordersDiv.innerHTML = "<p>No orders yet.</p>";
      return;
    }

    ordersDiv.innerHTML = "";

    data.orders.forEach(order => {
      let itemsHtml = "";

      order.items.forEach(item => {
        const itemTotal = item.quantity * item.price_at_purchase;

        itemsHtml += `
          <tr>
            <td>${item.product_name}</td>
            <td>${item.quantity}</td>
            <td>Rs. ${item.price_at_purchase}</td>
            <td>Rs. ${itemTotal}</td>
          </tr>
        `;
      });

      ordersDiv.innerHTML += `
        <div class="order-card">
          <div class="order-header">
            <span><strong>Order #${order.order_id}</strong></span>
            <span>${new Date(order.created_at).toLocaleString()}</span>
          </div>

          <table class="order-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              ${itemsHtml}
            </tbody>
          </table>

          <div class="order-total">
            Total: Rs. ${order.total_amount}
          </div>
        </div>
      `;
    });
  })
  .catch(err => {
    console.error(err);
    document.getElementById("orders").innerText =
      "Failed to load orders.";
  });
