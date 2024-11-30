from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from flask_cors import CORS  # Import CORS
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages
CORS(app)  # Apply CORS to the entire app

# Global variable to store current logged in user's login_id
current_user_id = None

# Helper function to get username from login_id


def get_username(login_id):
    if not login_id:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT username FROM login_info WHERE login_id = ?', (login_id,))
    result = cursor.fetchone()
    conn.close()
    return result['username'] if result else None

# Helper function to connect to the database


def get_db_connection():
    conn = sqlite3.connect('example.db')  # SQLite DB file
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Create some example tables and insert data if they don't exist


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_info
        (
        login_id VARCHAR(10),
        username VARCHAR(20),
        password VARCHAR(20),
        user_type VARCHAR(5),
        PRIMARY KEY (login_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cust_info 
        (
        cust_id VARCHAR(10),
        login_id VARCHAR(10), 
        f_name VARCHAR(20),
        l_name VARCHAR(20),
        email VARCHAR(50),
        phone_num VARCHAR(20),
        birthday VARCHAR(20),
        acct_creation_dt VARCHAR(20),
        acct_status VARCHAR(10),
        PRIMARY KEY (cust_id),
        FOREIGN KEY (login_id)
        REFERENCES login_info
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emp_info
        (
        emp_id VARCHAR(10),
        login_id VARCHAR(10),
        f_name VARCHAR(20),
        l_name VARCHAR(20),
        email VARCHAR(50),
        phone_num VARCHAR(20),
        office_hours VARCHAR(200),
        emp_intro VARCHAR(1000),
        emp_status VARCHAR(10),
        PRIMARY KEY (emp_id),
        FOREIGN KEY (login_id) REFERENCES login_info
        )
    ''')

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

    # Create veicle inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veh_inv 
            (
            veh_inv_id VARCHAR(10),
            veh_id VARCHAR(10),
            condition VARCHAR(20),
            miles_used INT,
            price FLOAT(2),
            inventory_count INT,
            special_notes VARCHAR(1000),
            image_url varchar(200),
            location VARCHAR(20),
            PRIMARY KEY (veh_inv_id),
            FOREIGN KEY (veh_id) REFERENCES veh_info
            )
    ''')

    # Create vehicle information table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veh_info (
            veh_id VARCHAR(10) PRIMARY KEY,
            veh_name VARCHAR(50),
            ext_color VARCHAR(20),
            horsepower VARCHAR(10),
            mileage VARCHAR(10),
            year INTEGER NOT NULL,
            engine TEXT NOT NULL
            )
    ''')

    # Create sale campaign table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_camp (
        campaign_id VARCHAR(10),
        campaign_desc VARCHAR(2000),
        start_dt VARCHAR(10),
        end_dt VARCHAR(10),
        PRIMARY KEY (campaign_id)
        )
    ''')

    # Create sale campaign details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_camp_detailed (
        campaign_id VARCHAR(10),
        veh_inv_id VARCHAR(10),
        campaign_price FLOAT(2),
        PRIMARY KEY (campaign_id, veh_inv_id),
        FOREIGN KEY (campaign_id) REFERENCES sale_camp,
        FOREIGN KEY (veh_inv_id) REFERENCES veh_inv
        )
    ''')

    # Insert sample data for veh_info with new fields
    cursor.execute('SELECT COUNT(*) FROM veh_info')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO veh_info (veh_id, veh_name, ext_color, engine, horsepower, mileage, year)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        ('V001', 'Tesla Model S', 'Black', 'Electric Motor', '1020', '15000', '2024'),
        ('V002', 'BMW X5', 'White', '3.0L I6 Turbo', '335', '30000', '2022'),
        ('V003', 'Ford Mustang', 'Blue', '5.0L V8', '450', '25000', '2020'),
        ('V004', 'Audi A4', 'Red', '2.0L I4 Turbo', '248', '20000', '2023'),
        ('V005', 'Chevrolet Corvette', 'Yellow', '6.2L V8', '495', '5000', '2022'),
        ('V006', 'Mercedes-Benz C-Class', 'Silver', '2.0L I4 Turbo', '255', '10000', '2021'),
        ('V007', 'Honda Civic', 'Green', '2.0L I4', '158', '15000', '2020'),
        ('V008', 'Toyota Camry', 'Black', '2.5L I4', '203', '18000', '2021'),
        ('V009', 'Nissan Altima', 'White', '2.5L I4', '182', '22000', '2021'),
        ('V010', 'Jaguar F-Type', 'Orange', '5.0L V8', '380', '12000', '2021'),
        ('V011', 'Lexus RX', 'Blue', '3.5L V6', '295', '27000', '2023'),
        ('V012', 'Porsche 911', 'Silver', '3.0L Twin-Turbo H6', '443', '3000', '2023'),
        ('V013', 'Subaru Outback', 'Grey', '2.5L H4', '175', '32000', '2022'),
        ('V014', 'Mazda CX-5', 'Red', '2.5L I4', '187', '22000', '2021'),
        ('V015', 'Chrysler Pacifica', 'Red', '3.6L V6', '287', '15000', '2023'),
        ('V016', 'BMW 3 Series', 'Blue', '2.0L I4 Turbo', '255', '24000', '2023'),
        ('V017', 'Ford F-150', 'Black', '3.5L EcoBoost V6', '400', '28000', '2022'),
        ('V018', 'Hyundai Elantra', 'Silver', '2.0L I4', '147', '15000', '2023')
    ])

    # Insert sample data for veh_info with new fields
    cursor.execute('SELECT COUNT(*) FROM veh_inv')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO veh_inv (veh_inv_id, veh_id, condition, miles_used, price, special_notes, image_url, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('INV001', 'V001', 'Used', 15000, 79999.99, 'A high-performance electric sedan with impressive range and cutting-edge technology.', 'https://media.ed.edmunds-media.com/tesla/model-s/2024/oem/2024_tesla_model-s_sedan_plaid_fq_oem_1_815.jpg', 'Philadelphia, PA'),
            ('INV002', 'V002', 'Used', 30000, 60999.99, 'A luxury midsize SUV combining style, comfort, and sport performance for any adventure.', 'https://cache.bmwusa.com/cosy.arox?pov=walkaround&brand=WBBM&vehicle=25XO&client=byoc&paint=P0300&fabric=FKPSW&sa=S01CE,S01SF,S0255,S02TB,S0302,S0319,S0322,S03AT,S03MB,S0402,S0420,S0423,S0459,S0481,S0494,S04FL,S04KR,S04T8,S04UR,S0552,S05AC,S05AS,S05DM,S0676,S06AC,S06AK,S06C4,S06CP,S06NX,S06U2,S0775&angle=30', 'Pittsburgh, PA'),
            ('INV003', 'V003', 'New', 25000, 35999.99, 'A classic American muscle car known for its powerful V8 engine and iconic design.', 'https://i.ytimg.com/vi/lEn1jZKgXB4/sddefault.jpg', 'Allentown, PA'),
            ('INV004', 'V004', 'New', 20000, 45999.99, 'A compact luxury sedan offering high-end tech, a smooth ride, and a powerful engine.', 'https://cdn.max.auto/t_hres/110026/WAUEAAF40RN006977/665662925eacd0c1522d7c44.jpg', 'Harrisburg, PA'),
            ('INV005', 'V005', 'New', 5000, 84999.99, 'A performance-oriented sports car that embodies American engineering with thrilling speed and agility.', 'https://media.carsandbids.com/cdn-cgi/image/width=2080,quality=70/da4b9237bacccdf19c0760cab7aec4a8359010b0/photos/3zVDVjgP-bWZFfp5WaV2-A47-9Vmg57.jpg?t=165308031771', 'Scranton, PA'),
            ('INV006', 'V006', 'Used', 10000, 55999.99, 'A luxurious compact sedan that offers precision engineering, advanced safety, and premium comfort.', 'https://vehicle-photos-published.vauto.com/04/3f/40/ce-30ec-4c28-b65d-00284ef63a5d/image-2.jpg', 'Lancaster, PA'),
            ('INV007', 'V007', 'Used', 15000, 23999.99, 'A reliable compact car with great fuel efficiency, a comfortable interior, and sleek design.', 'https://www.motortrend.com/uploads/sites/5/2015/04/Honda-Civic-Concept-front-end-03.jpg', 'Reading, PA'),
            ('INV008', 'V008', 'Used', 18000, 27999.99, 'A midsize sedan known for its reliability, comfort, and excellent fuel efficiency.', 'https://vehicle-images.dealerinspire.com/f70e-110007893/4T1DBADK6SU501169/31884f6ef3bcf63a9e1a16826f93c432.jpg', 'Bethlehem, PA'),
            ('INV009', 'V009', 'Used', 22000, 28999.99, 'A stylish midsize sedan offering excellent safety features, technology, and a smooth ride.', 'https://vehicle-images.dealerinspire.com/2451-110005012/1N4BL4DV3SN303721/58cb63ca27eee6aaa3d42d214eec6837.jpg', 'Easton, PA'),
            ('INV010', 'V010', 'Used', 12000, 70999.99, 'A performance-focused luxury sports car combining a stunning design with immense power and handling precision.', 'https://www.marinoperformancemotors.com/imagetag/12929/4/l/Used-2016-Jaguar-F-TYPE-S.jpg', 'York, PA'),
            ('INV011', 'V011', 'Used', 27000, 60999.99, 'A premium crossover SUV offering luxury features, smooth performance, and top-tier safety ratings.', 'https://www.kbb.com/wp-content/uploads/2022/11/2023-lexus-rx350-f-sport-front-left-3qtr.jpg', 'King of Prussia, PA'),
            ('INV012', 'V012', 'Used', 3000, 99999.99, 'An iconic sports car with stunning performance and handling, and a timeless design.', 'https://i.ytimg.com/vi/qnhuEveXoM8/maxresdefault.jpg', 'Chester, PA'),
            ('INV013', 'V013', 'Used', 32000, 35999.99, 'A rugged and versatile crossover SUV ideal for outdoor adventures with all-wheel drive and ample cargo space.', 'https://i.ytimg.com/vi/-grrSULw9hk/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLARiMzy9YuDE4wkvVcoQ9OsKsLenw', 'Pottstown, PA'),
            ('INV014', 'V014', 'Used', 22000, 37999.99, 'A compact crossover with exceptional handling, a premium interior, and great fuel economy.', 'https://www.carpro.com/hs-fs/hubfs/img-6688-1404x1112.jpg?width=1020&name=img-6688-1404x1112.jpg', 'West Chester, PA'),
            ('INV015', 'V015', 'Used', 15000, 42999.99, 'A family-friendly minivan offering ample seating, cargo space, and a hybrid option for better fuel efficiency.', 'https://www.chrysler.com/content/dam/fca-brands/na/chrysler/en_us/2024/pacifica/hybrid/gallery/desktop/my24-chrysler-hybrid-gallery-04-exterior-desktop.jpg.image.1440.jpg', 'Huntingdon Valley, PA'),
            ('INV016', 'V016', 'Used', 24000, 47999.99, 'A compact luxury sedan known for its dynamic driving experience and sophisticated interior.', 'https://www.edmunds.com/assets/m/cs/bltfd77bfe883e04cf6/66562cab0d6347db0279febf/2025_BMW_3-series_3_1600.jpg', 'New Hope, PA'),
            ('INV017', 'V017', 'Used', 28000, 55999.99, 'A powerful and versatile full-size pickup truck designed for heavy-duty tasks and off-road adventures.', 'https://vehicle-images.dealerinspire.com/ab52-110005802/1FTEW2KP2RKE17566/4d23121092bc21826489ad899274c080.jpg', 'Media, PA'),
            ('INV018', 'V018', 'Used', 15000, 21999.99, 'A compact sedan offering a modern design, advanced tech features, and great fuel economy at an affordable price.', 'https://di-uploads-pod27.dealerinspire.com/patrickhyundai/uploads/2022/12/2023-Hyundai-ELANTRA_900x450.jpg', 'Lebanon, PA')
        ])

    # Insert sample data for sale_camp
    cursor.execute('SELECT COUNT(*) FROM sale_camp')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO sale_camp (campaign_id, campaign_desc, start_dt, end_dt)
        VALUES (?, ?, ?, ?)
    ''', [
            ('BF2024', 'Black Friday Sale - Huge discounts on all vehicles.', '2024-11-29', '2024-12-02'),
            ('MD2024', 'Memorial Day Sale - Save big on top models this Memorial Day.', '2024-05-25', '2024-05-28'),
            ('TG2024', 'Thanksgiving Sale - Special offers on luxury and family cars.', '2024-11-22', '2024-11-25')
        ])

        # Insert sample data for sale_camp
    cursor.execute('SELECT COUNT(*) FROM sale_camp_detailed')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO sale_camp_detailed (campaign_id, veh_inv_id, campaign_price)
            VALUES (?, ?, ?)
        ''', [
            # Black Friday Sale
            ('BF2024', 'INV001', 79999.99 * 0.90),  # 10% off
            ('BF2024', 'INV002', 60999.99 * 0.90),
            ('BF2024', 'INV003', 35999.99 * 0.90),
            ('BF2024', 'INV004', 45999.99 * 0.90),
            ('BF2024', 'INV006', 55999.99 * 0.90),
            ('BF2024', 'INV007', 23999.99 * 0.90),
            ('BF2024', 'INV008', 27999.99 * 0.90),
            ('BF2024', 'INV009', 28999.99 * 0.90),
            ('BF2024', 'INV010', 70999.99 * 0.90),
            ('BF2024', 'INV011', 60999.99 * 0.90),
            ('BF2024', 'INV012', 99999.99 * 0.90),
            ('BF2024', 'INV013', 35999.99 * 0.90),
            ('BF2024', 'INV014', 37999.99 * 0.90),
            ('BF2024', 'INV015', 42999.99 * 0.90),
            ('BF2024', 'INV016', 47999.99 * 0.90),
            ('BF2024', 'INV017', 55999.99 * 0.90),
            ('BF2024', 'INV018', 21999.99 * 0.90),

            # Memorial Day Sale
            ('MD2024', 'INV001', 79999.99 * 0.95),  # 5% off
            ('MD2024', 'INV002', 60999.99 * 0.95),
            ('MD2024', 'INV003', 35999.99 * 0.95),
            ('MD2024', 'INV004', 45999.99 * 0.95),
            ('MD2024', 'INV006', 55999.99 * 0.95),
            ('MD2024', 'INV007', 23999.99 * 0.95),
            ('MD2024', 'INV008', 27999.99 * 0.95),
            ('MD2024', 'INV009', 28999.99 * 0.95),
            ('MD2024', 'INV010', 70999.99 * 0.95),
            ('MD2024', 'INV011', 60999.99 * 0.95),
            ('MD2024', 'INV012', 99999.99 * 0.95),
            ('MD2024', 'INV013', 35999.99 * 0.95),
            ('MD2024', 'INV014', 37999.99 * 0.95),
            ('MD2024', 'INV015', 42999.99 * 0.95),
            ('MD2024', 'INV016', 47999.99 * 0.95),
            ('MD2024', 'INV017', 55999.99 * 0.95),
            ('MD2024', 'INV018', 21999.99 * 0.95),

            # Thanksgiving Sale
            ('TG2024', 'INV001', 79999.99 * 0.85),  # 15% off
            ('TG2024', 'INV002', 60999.99 * 0.85),
            ('TG2024', 'INV003', 35999.99 * 0.85),
            ('TG2024', 'INV004', 45999.99 * 0.85),
            ('TG2024', 'INV006', 55999.99 * 0.85),
            ('TG2024', 'INV007', 23999.99 * 0.85),
            ('TG2024', 'INV008', 27999.99 * 0.85),
            ('TG2024', 'INV009', 28999.99 * 0.85),
            ('TG2024', 'INV010', 70999.99 * 0.85),
            ('TG2024', 'INV011', 60999.99 * 0.85),
            ('TG2024', 'INV012', 99999.99 * 0.85),
            ('TG2024', 'INV013', 35999.99 * 0.85),
            ('TG2024', 'INV014', 37999.99 * 0.85),
            ('TG2024', 'INV015', 42999.99 * 0.85),
            ('TG2024', 'INV016', 47999.99 * 0.85),
            ('TG2024', 'INV017', 55999.99 * 0.85),
            ('TG2024', 'INV018', 21999.99 * 0.85)
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

# API endpoint to get all cars (from veh_info table)
@app.route('/api/cars', methods=['GET'])
def get_cars():
    conn = get_db_connection()
    # Fetch all car details from veh_info and veh_inv tables, joining on veh_id
    query = '''
    SELECT veh_inv.veh_inv_id, veh_info.veh_id, veh_info.veh_name, veh_info.ext_color, veh_info.horsepower, veh_info.mileage, 
        veh_inv.condition, veh_inv.price, veh_inv.inventory_count, veh_inv.special_notes, veh_inv.image_url,
        veh_info.year, veh_inv.location
    FROM veh_info
    LEFT JOIN veh_inv ON veh_info.veh_id = veh_inv.veh_id
    '''
    cars = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(car) for car in cars])

# API endpoint to get car details by ID (from veh_info and veh_inv tables)
@app.route('/api/cars/<string:car_id>', methods=['GET'])
def get_car_details(car_id):
    conn = get_db_connection()
    # Fetch detailed car info by ID, joining both tables
    query = '''
    SELECT veh_info.veh_id, veh_info.veh_name, veh_info.ext_color, 
            veh_info.horsepower, veh_info.mileage, veh_inv.condition, veh_inv.miles_used, 
            veh_inv.price, veh_inv.inventory_count, veh_inv.special_notes, veh_inv.image_url, 
           veh_info.year, veh_info.engine, veh_inv.location
    FROM veh_info
    LEFT JOIN veh_inv ON veh_info.veh_id = veh_inv.veh_id
    WHERE veh_info.veh_id = ?
    '''
    car = conn.execute(query, (car_id,)).fetchone()
    conn.close()
    if car:
        return jsonify(dict(car))
    else:
        return jsonify({'error': 'Car not found'}), 404
    
# Endpoint to check if a vehicle is on sale
@app.route('/api/car_sale/<string:veh_inv_id>', methods=['GET'])
def get_vehicle_sale(veh_inv_id):
    try:
        conn = get_db_connection()
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Check if the vehicle is on sale and fetch the sale price
        sale_info = conn.execute('''
            SELECT d.campaign_price 
            FROM sale_camp s
            JOIN sale_camp_detailed d ON s.campaign_id = d.campaign_id
            WHERE d.veh_inv_id = ? AND s.start_dt <= ? AND s.end_dt >= ?
        ''', (veh_inv_id, current_date, current_date)).fetchone()

        conn.close()

        if sale_info:
            return jsonify({
                'veh_inv_id': veh_inv_id,
                'campaign_price': sale_info['campaign_price'],
                'message': 'Vehicle is on sale'
            })
        else:
            # No active sale, return price as normal
            return jsonify({
                'veh_inv_id': veh_inv_id,
                'message': 'No active sale for this vehicle'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/")
def connect():
    if current_user_id:
        current_user = get_username(current_user_id)
        return render_template("index.html").replace('var currentUser = null;', f'var currentUser = "{current_user}";')
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query the database for the user
        cursor.execute('SELECT * FROM login_info WHERE username = ? AND password = ?',
                       (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            global current_user_id
            current_user_id = user['login_id']
            return redirect('/account')
        else:
            # Redirect to login page with error parameter
            return redirect('/login?error=1')

    return render_template('login.html')


@app.route("/logout")
def logout():
    global current_user_id
    current_user_id = None
    return redirect('/')


@app.route("/register/", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        email = request.form['email']
        phone_num = request.form['phone_num']
        birthday = request.form['birthday']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if username already exists
            cursor.execute(
                'SELECT * FROM login_info WHERE username = ?', (username,))
            if cursor.fetchone() is not None:
                return redirect('/register?error=username_exists')

            # Generate login_id (10 digit random number)
            while True:
                login_id = str(random.randint(1000000000, 9999999999))
                cursor.execute(
                    'SELECT * FROM login_info WHERE login_id = ?', (login_id,))
                if cursor.fetchone() is None:
                    break

            # Get current date for account creation
            acct_creation_dt = datetime.now().strftime('%Y-%m-%d')

            print(f"Inserting into login_info: {login_id}, {
                  username}, {password}, customer")
            # Insert into login_info table
            cursor.execute('''
                INSERT INTO login_info (login_id, username, password, user_type)
                VALUES (?, ?, ?, ?)
            ''', (login_id, username, password, 'customer'))

            # Generate customer ID (CUST + last 6 digits of login_id)
            cust_id = 'CUST' + login_id[-6:]

            print(f"Inserting into cust_info: {cust_id}, {login_id}, {f_name}, {
                  l_name}, {email}, {phone_num}, {birthday}, {acct_creation_dt}, active")
            # Insert into cust_info table
            cursor.execute('''
                INSERT INTO cust_info (cust_id, login_id, f_name, l_name, email, phone_num, birthday, acct_creation_dt, acct_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cust_id, login_id, f_name, l_name, email, phone_num, birthday, acct_creation_dt, 'active'))

            conn.commit()
            print("Database commit successful")
            return render_template('registration_success.html')

        except Exception as e:
            conn.rollback()
            print(f"Error during registration: {str(e)}")
            return redirect('/register?error=registration_failed')

        finally:
            conn.close()

    return render_template('regist.html')


@app.route("/registration_success")
def registration_success():
    return render_template('registration_success.html')


@app.route("/account")
def account():
    if not current_user_id:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get user information from both tables
    cursor.execute('''
        SELECT li.username, ci.f_name, ci.l_name, ci.email, ci.phone_num, ci.birthday
        FROM login_info li
        JOIN cust_info ci ON li.login_id = ci.login_id
        WHERE li.login_id = ?
    ''', (current_user_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        user_info = {
            'username': row['username'],
            'f_name': row['f_name'],
            'l_name': row['l_name'],
            'email': row['email'],
            'phone_num': row['phone_num'],
            'birthday': row['birthday']
        }
        # Get message from query parameter if it exists
        message = request.args.get('message', '')
        message_type = request.args.get('message_type', '')
        return render_template('account.html', user_info=user_info, message=message, message_type=message_type)
    return redirect('/login')


@app.route("/update_account", methods=['POST'])
def update_account():
    if not current_user_id:
        return redirect('/login')

    # Get form data
    current_password = request.form.get('current_password')
    new_password = request.form.get('password')
    f_name = request.form['f_name']
    l_name = request.form['l_name']
    email = request.form['email']
    phone_num = request.form['phone_num']
    birthday = request.form['birthday']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verify current password
        cursor.execute(
            'SELECT password FROM login_info WHERE login_id = ?', (current_user_id,))
        stored_password = cursor.fetchone()['password']

        if not stored_password or stored_password != current_password:
            return redirect('/account?message=Incorrect current password. No changes were made.&message_type=error')

        # Update customer information
        cursor.execute('''
            UPDATE cust_info 
            SET f_name = ?, l_name = ?, email = ?, phone_num = ?, birthday = ?
            WHERE login_id = ?
        ''', (f_name, l_name, email, phone_num, birthday, current_user_id))

        # Update password if a new one is provided
        if new_password and new_password.strip():
            cursor.execute('''
                UPDATE login_info 
                SET password = ?
                WHERE login_id = ?
            ''', (new_password, current_user_id))

        conn.commit()
        return redirect('/account?message=Your information has been updated successfully!&message_type=success')
    except Exception as e:
        conn.rollback()
        return redirect('/account?message=An error occurred while updating your information.&message_type=error')
    finally:
        conn.close()

    return redirect('/account')


if __name__ == '__main__':
    init_db()  # Initialize the database with tables and data
    app.run(debug=True)
