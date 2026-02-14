// products.js

const token = localStorage.getItem("token");

if (!token) {
  alert("Not logged in");
  window.location.href = "index.html";
}

// Fetch products
fetch(`${API_BASE_URL}/products`, {
  headers: {
    Authorization: `Bearer ${token}`
  }
})
.then(res => {
  if (!res.ok) {
    throw new Error("Failed to fetch products: " + res.status);
  }
  return res.json();
})
.then(products => {
  console.log("Products:", products);

  const div = document.getElementById("products");
  div.innerHTML = "";

  products.forEach(p => {
    div.innerHTML += `
      <div class="product">
        <strong>${p.name}</strong><br>
        Price: Rs. ${p.price}<br>
        Stock: ${p.stock}<br><br>
        <button onclick="addToCart(${p.product_id})">
          Add to Cart
        </button>
      </div>
    `;
  });
})
.catch(err => {
  console.error(err);
  document.getElementById("products").innerText =
    "Error loading products";
});

// Add item to cart
function addToCart(productId) {
  fetch(`${API_BASE_URL}/cart`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: 1
    })
  })
  .then(res => {
    if (!res.ok) {
      throw new Error("Add to cart failed");
    }
    return res.json();
  })
  .then(() => {
    alert("Added to cart");
  })
  .catch(err => {
    console.error(err);
    alert("Failed to add item");
  });
}
