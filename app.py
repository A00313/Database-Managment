from flask import Flask, jsonify
import sqlite3
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Apply CORS to the entire app

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('example.db')  # SQLite DB file
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Create some example tables and insert data if they don't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY,
            model TEXT NOT NULL,
            price REAL NOT NULL,
            mileage INTEGER NOT NULL,
            color TEXT NOT NULL,
            picture TEXT NOT NULL  -- Add a column for the picture URL
        )
    ''')

    # Insert sample data for cars if the table is empty
    cursor.execute('SELECT COUNT(*) FROM cars')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO cars (model, price, mileage, color, picture) VALUES (?, ?, ?, ?, ?)', [
            ('Tesla Model S', 79999.99, 15000, 'Black', 'https://media.ed.edmunds-media.com/tesla/model-s/2024/oem/2024_tesla_model-s_sedan_plaid_fq_oem_1_815.jpg'),
            ('BMW X5', 60999.99, 30000, 'White', 'https://cache.bmwusa.com/cosy.arox?pov=walkaround&brand=WBBM&vehicle=25XO&client=byoc&paint=P0300&fabric=FKPSW&sa=S01CE,S01SF,S0255,S02TB,S0302,S0319,S0322,S03AT,S03MB,S0402,S0420,S0423,S0459,S0481,S0494,S04FL,S04KR,S04T8,S04UR,S0552,S05AC,S05AS,S05DM,S0676,S06AC,S06AK,S06C4,S06CP,S06NX,S06U2,S0775&angle=30'),
            ('Ford Mustang', 35999.99, 25000, 'Blue', 'https://i.ytimg.com/vi/lEn1jZKgXB4/sddefault.jpg'),
            ('Audi A4', 45999.99, 20000, 'Red', 'https://cdn.max.auto/t_hres/110026/WAUEAAF40RN006977/665662925eacd0c1522d7c44.jpg'),
            ('Chevrolet Corvette', 84999.99, 5000, 'Yellow', 'https://media.carsandbids.com/cdn-cgi/image/width=2080,quality=70/da4b9237bacccdf19c0760cab7aec4a8359010b0/photos/3zVDVjgP-bWZFfp5WaV2-A47-9Vmg57.jpg?t=165308031771'),
            ('Mercedes-Benz C-Class', 55999.99, 10000, 'Silver', 'https://vehicle-photos-published.vauto.com/04/3f/40/ce-30ec-4c28-b65d-00284ef63a5d/image-2.jpg'),
            ('Honda Civic', 23999.99, 15000, 'Green', 'https://www.motortrend.com/uploads/sites/5/2015/04/Honda-Civic-Concept-front-end-03.jpg'),
            ('Toyota Camry', 27999.99, 18000, 'Black', 'https://vehicle-images.dealerinspire.com/f70e-110007893/4T1DBADK6SU501169/31884f6ef3bcf63a9e1a16826f93c432.jpg'),
            ('Nissan Altima', 28999.99, 22000, 'White', 'https://vehicle-images.dealerinspire.com/2451-110005012/1N4BL4DV3SN303721/58cb63ca27eee6aaa3d42d214eec6837.jpg'),
            ('Jaguar F-Type', 70999.99, 12000, 'Orange', 'https://www.marinoperformancemotors.com/imagetag/12929/4/l/Used-2016-Jaguar-F-TYPE-S.jpg'),
            ('Lexus RX', 60999.99, 27000, 'Blue', 'https://www.kbb.com/wp-content/uploads/2022/11/2023-lexus-rx350-f-sport-front-left-3qtr.jpg'),
            ('Porsche 911', 99999.99, 3000, 'Silver', 'https://i.ytimg.com/vi/qnhuEveXoM8/maxresdefault.jpg'),
            ('Subaru Outback', 35999.99, 32000, 'Grey', 'https://i.ytimg.com/vi/-grrSULw9hk/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLARiMzy9YuDE4wkvVcoQ9OsKsLenw'),
            ('Mazda CX-5', 37999.99, 22000, 'Yellow', 'https://i.ytimg.com/vi/RnzaMjpPi6o/maxresdefault.jpg'),
            ('Chrysler Pacifica', 42999.99, 15000, 'Red', 'https://www.chrysler.com/content/dam/fca-brands/na/chrysler/en_us/2024/pacifica/hybrid/gallery/desktop/my24-chrysler-hybrid-gallery-04-exterior-desktop.jpg.image.1440.jpg'),
            ('BMW 3 Series', 47999.99, 24000, 'Blue', 'https://www.edmunds.com/assets/m/cs/bltfd77bfe883e04cf6/66562cab0d6347db0279febf/2025_BMW_3-series_3_1600.jpg'),
            ('Ford F-150', 55999.99, 28000, 'Black', 'https://vehicle-images.dealerinspire.com/ab52-110005802/1FTEW2KP2RKE17566/4d23121092bc21826489ad899274c080.jpg'),
            ('Hyundai Elantra', 21999.99, 15000, 'Silver', 'https://di-uploads-pod27.dealerinspire.com/patrickhyundai/uploads/2022/12/2023-Hyundai-ELANTRA_900x450.jpg'),
            ('Kia Sorento', 44999.99, 23000, 'Grey', 'https://www.speedsportlife.com/wp-content/2022/04/IMG_4020.jpg'),
            ('Volkswagen Golf GTI', 34999.99, 19000, 'White', 'https://images.squarespace-cdn.com/content/v1/5b2437bcc3c16a6fea91cd4d/1570668346246-QQ7ZKK20OQVCCRWTU9HQ/2019-10-08+13.11.03.jpg?format=1000w'),
            ('Ram 1500', 45999.99, 25000, 'Red', 'https://www.motortrend.com/uploads/sites/3/2021/07/008_2022_Ram_1500_Laramie_GT.jpg'),
            ('Acura MDX', 57999.99, 27000, 'Green', 'https://cdn.dealeraccelerate.com/ag/3/2430/198777/1920x1440/2007-acura-mdx'),
            ('Infiniti QX60', 62999.99, 18000, 'Brown', 'https://upload.wikimedia.org/wikipedia/commons/1/1c/Infiniti_QX60_%28L51%29%2C_2021%2C_right-front.jpg'),
            ('Buick Enclave', 49999.99, 22000, 'Blue', 'https://di-uploads-pod34.dealerinspire.com/visionbuickgmc/uploads/2024/08/Vision-Buick-GMC-Enclave.jpg'),
            ('Volvo XC90', 63999.99, 21000, 'Silver', 'https://i.ytimg.com/vi/dRbh3sLfbw8/maxresdefault.jpg')
        ])

    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO users (name, email) VALUES (?, ?)', [
            ('Alice', 'alice@example.com'),
            ('Bob', 'bob@example.com')
        ])

    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO products (name, price) VALUES (?, ?)', [
            ('Laptop', 999.99),
            ('Phone', 599.99),
            ('Tablet', 399.99)
        ])

    cursor.execute('SELECT COUNT(*) FROM orders')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)', [
            (1, 1, 1),  # Alice bought 1 Laptop
            (2, 2, 2)   # Bob bought 2 Phones
        ])

    conn.commit()
    conn.close()

# API endpoint to get users
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

# API endpoint to get products
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

# API endpoint to get orders
@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT orders.id, users.name, products.name AS product_name, orders.quantity
        FROM orders
        JOIN users ON orders.user_id = users.id
        JOIN products ON orders.product_id = products.id
    ''').fetchall()
    conn.close()
    return jsonify([dict(order) for order in orders])

# API endpoint to get cars
@app.route('/api/cars', methods=['GET'])
def get_cars():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars').fetchall()
    conn.close()
    return jsonify([dict(car) for car in cars])

if __name__ == '__main__':
    init_db()  # Initialize the database with tables and data
    app.run(debug=True)
