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
