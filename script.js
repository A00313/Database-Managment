// Function to handle fetching users
async function fetchUsers() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/users');
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
            const usersDataDiv = document.getElementById('users-data');
            usersDataDiv.innerHTML = data.map(user => `
                <div class="data-item">
                    <strong>${user.name}</strong> (${user.email})
                </div>
            `).join('');
        } else {
            document.getElementById('users-data').innerHTML = '<p>No users found.</p>';
        }
    } catch (error) {
        console.error('Error fetching users:', error);
        document.getElementById('users-data').innerHTML = `<p class="error">Error fetching users: ${error.message}</p>`;
    }
}

// Function to handle fetching products
async function fetchProducts() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/products');
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
            const productsDataDiv = document.getElementById('products-data');
            productsDataDiv.innerHTML = data.map(product => `
                <div class="data-item">
                    <strong>${product.name}</strong> - $${product.price}
                </div>
            `).join('');
        } else {
            document.getElementById('products-data').innerHTML = '<p>No products found.</p>';
        }
    } catch (error) {
        console.error('Error fetching products:', error);
        document.getElementById('products-data').innerHTML = `<p class="error">Error fetching products: ${error.message}</p>`;
    }
}

// Function to handle fetching orders
async function fetchOrders() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/orders');
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
            const ordersDataDiv = document.getElementById('orders-data');
            ordersDataDiv.innerHTML = data.map(order => `
                <div class="data-item">
                    <strong>${order.name}</strong> bought ${order.quantity} x ${order.product_name}
                </div>
            `).join('');
        } else {
            document.getElementById('orders-data').innerHTML = '<p>No orders found.</p>';
        }
    } catch (error) {
        console.error('Error fetching orders:', error);
        document.getElementById('orders-data').innerHTML = `<p class="error">Error fetching orders: ${error.message}</p>`;
    }
}

// Function to handle fetching cars
async function fetchCars() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/cars');
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
            const carsDataDiv = document.getElementById('cars-data');
            carsDataDiv.innerHTML = data.map(car => `
                <div class="data-item">
                    <strong>${car.model}</strong> - $${car.price}<br>
                    Mileage: ${car.mileage} miles<br>
                    Color: ${car.color}<br>
                    <img src="${car.picture}" alt="${car.model}">
                </div>
            `).join('');
        } else {
            document.getElementById('cars-data').innerHTML = '<p>No cars found.</p>';
        }
    } catch (error) {
        console.error('Error fetching cars:', error);
        document.getElementById('cars-data').innerHTML = `<p class="error">Error fetching cars: ${error.message}</p>`;
    }
}

// Function to show and hide sections
function showSection(section) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(s => s.classList.remove('active'));
    document.getElementById(section).classList.add('active');
}

// Initialize with Users section visible
window.onload = () => {
    showSection('users');
};
