async function fetchCars() {
    currentPage = 'fetch-cars';  // Track that we're on the "fetch cars" page

    try {
        const response = await fetch('http://127.0.0.1:5000/api/cars');
        const data = await response.json();

        if (Array.isArray(data) && data.length > 0) {
            const carsDataDiv = document.getElementById('cars-data');

            // Use map and await the results before joining
            const carItems = await Promise.all(data.map(async car => {
                let salePrice = null;
                let oldPrice = car.price;  // Default to original price

                // Ensure price is valid before continuing
                const isValidPrice = (price) => !isNaN(price) && price !== null && price !== undefined;

                try {
                    // Fetch sale data for this car
                    const saleResponse = await fetch(`http://127.0.0.1:5000/api/car_sale/${car.veh_inv_id}`);
                    const saleData = await saleResponse.json();

                    if (saleData.campaign_price && isValidPrice(saleData.campaign_price)) {
                        salePrice = saleData.campaign_price;  // If there's a sale, use the campaign price
                        oldPrice = car.price;  // Keep the original price if there's a sale
                    } else {
                        console.log(`No active sale for ${car.veh_inv_id}`);
                    }
                } catch (error) {
                    console.log(`Error fetching sale data for ${car.veh_inv_id}: ${error}`);
                }

                // Ensure salePrice and oldPrice are valid before using `toFixed`
                const displayPrice = isValidPrice(salePrice) ? salePrice : (isValidPrice(oldPrice) ? oldPrice : 0);

                // Return the car's HTML content with the correct price
                return `
                    <div class="data-item" onclick="viewCarDetails('${car.veh_id}', '${car.veh_inv_id}')">
                        <strong>${car.veh_name}</strong><br>
                        <img src="${car.image_url}" alt="${car.veh_name}" class="car-image" style="height: 200px; object-fit: cover;">
                        ${isValidPrice(salePrice) ? `<span class="old-price" style="text-decoration: line-through; color: grey;">$${oldPrice.toFixed(2)}</span> ` : ''}
                        <span class="${isValidPrice(salePrice) ? 'sale-price' : ''}" style="${isValidPrice(salePrice) ? 'color: red;' : ''}">$${displayPrice.toFixed(2)}</span><br>
                        Mileage: ${car.mileage} miles<br>
                        Color: ${car.ext_color}<br>
                        Condition: ${car.condition}<br>
                        Year: ${car.year}<br>
                        Location: ${car.location}<br>
                    </div>
                `;
            }));

            // Join the array of car HTML elements into a single string and set the innerHTML
            carsDataDiv.innerHTML = carItems.join('');
        } else {
            document.getElementById('cars-data').innerHTML = '<p>No cars found.</p>';
        }
    } catch (error) {
        console.error('Error fetching cars:', error);
        document.getElementById('cars-data').innerHTML = `<p class="error">Error fetching cars: ${error.message}</p>`;
    }
}
