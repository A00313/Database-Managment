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

    # Table drop to ensure data is not duplicated
    cursor.execute('''
        DROP TABLE IF EXISTS veh_info
    ''')

    cursor.execute('''
        DROP TABLE IF EXISTS sale_camp
    ''')

    cursor.execute('''
        DROP TABLE IF EXISTS sale_camp_detailed
    ''')
    
    cursor.execute('''
        DROP TABLE IF EXISTS veh_inv
    ''')

    cursor.execute('''
        DROP TABLE IF EXISTS emp_info
    ''')

    cursor.execute('''
        DROP TABLE IF EXISTS purchases
    ''')

    cursor.execute('''
        DROP TABLE IF EXISTS cust_reviews
    ''')

    # Create employee information table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emp_info
        (
        emp_id VARCHAR(10),
        f_name VARCHAR(20),
        l_name VARCHAR(20),
        email VARCHAR(50),
        phone_num VARCHAR(20),
        office_hours VARCHAR(200),
        emp_intro VARCHAR(1000),
        emp_status VARCHAR(10),
        image_url VARCHAR(200),
        PRIMARY KEY (emp_id)
        )
    ''')

    # Insert sample data for emp_info
    cursor.execute('SELECT COUNT(*) FROM emp_info')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO emp_info (emp_id, f_name, l_name, email, phone_num, office_hours, emp_intro, emp_status, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [('emp0', 'online', 'online', 'online@example.com', '123-456-7890', 'N/A', 'This is for online sales', 'active', 
              'no_url'),
              ('emp1', 'John', 'Doe', 'JohnDoe@example.com', '123-456-7890', 'Mon-Fri: 9am-5pm', 
              "John Doe brings years of expertise and a passion for cars to every customer interaction. Whether you’re searching for the latest models or a dependable pre-owned vehicle, John is dedicated to finding the right fit for your lifestyle and budget. Known for his straightforward advice and exceptional customer care, John ensures a hassle-free buying experience from start to finish.", 'active',
              'https://media.gettyimages.com/id/1919265357/photo/close-up-portrait-of-confident-businessman-standing-in-office.jpg?s=2048x2048&w=gi&k=20&c=Y0-O4sl85iNuYPC9U4PEagLOOuGOC0xHWnhR_YOSJYk='),
              ('emp2', 'Jane', 'Smith', 'JaneSmith@example.com', '987-654-3210', 'Mon-Fri: 11am-8pm', 
              "With over a decade of experience, Jane Smith is dedicated to helping you find the perfect car for your needs and budget. Known for her friendly approach and expert knowledge, she creates a stress-free, transparent buying experience. Whether you’re after a brand-new model or a reliable pre-owned vehicle, Jane ensures you drive away happy.", 'active',
              'https://media.gettyimages.com/id/945061408/photo/portrait-of-beautiful-young-businesswoman.jpg?s=2048x2048&w=gi&k=20&c=GRrW26Eu7NE23TsmZJNinnn-EqL-G2EpdHti6qS2Xh8='),
              ('emp3', 'Bob', 'Johnson', 'BobJohnson@example.com', '555-555-5555', 'Sat-Sun: 9AM-5pm', 
              "Bob Johnson is a knowledgeable and approachable car specialist with a passion for matching people with the perfect vehicle. With a focus on understanding your unique needs, Bob provides honest advice and ensures a smooth, enjoyable car-buying experience. Whether it’s a sleek sedan, a rugged truck, or anything in between, Bob is here to guide you every step of the way.", 'active',
              'https://media.gettyimages.com/id/1179420343/photo/smiling-man-outdoors-in-the-city.jpg?s=2048x2048&w=gi&k=20&c=A5rKi_wYh0EL2Xv3GHSIzEwG9TyralNq_CjoSXIzfb8='),
              ('emp4', 'Alice', 'Williams', 'AliceWilliams@example.com', '111-222-3333', 'Sat-Sun: 9AM-5pm', 
              "Alice Williams is dedicated to making your car-buying journey simple, enjoyable, and stress-free. With her deep industry knowledge and a knack for understanding her customers' needs, Alice takes the time to find the perfect car for your lifestyle and budget. From first-time buyers to seasoned drivers, she offers personalized guidance every step of the way. ", 'active',
              'https://media.gettyimages.com/id/831902150/photo/ive-solidified-my-name-in-the-business-world.jpg?s=2048x2048&w=gi&k=20&c=zajbxqgcyLEhKdhwwHo0bHIcsyP0WEEefTsZnxSfe14=')
        ])

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

    # Create purchase table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            transaction_id VARCHAR(20) PRIMARY KEY,
            cust_id VARCHAR(10),
            emp_id VARCHAR(10),
            veh_inv_id VARCHAR(10),
            campaign_id VARCHAR(10),
            price DECIMAL(10, 2) NOT NULL,
            quantity INT NOT NULL,
            payment_status VARCHAR(50) DEFAULT 'pending',
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            credit_card VARCHAR(20),
            expiration VARCHAR(20),
            cvv VARCHAR(4),
            FOREIGN KEY (veh_inv_id) REFERENCES veh_inv(veh_inv_id),
            FOREIGN KEY (cust_id) REFERENCES cust_info(cust_id),
            FOREIGN KEY (emp_id) REFERENCES emp_info(emp_id),
            FOREIGN KEY (campaign_id) REFERENCES sale_camp(campaign_id)
        )
    ''')

    # Insert sample data for veh_info with new fields
    cursor.execute('SELECT COUNT(*) FROM veh_info')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO veh_info (veh_id, veh_name, ext_color, engine, horsepower, mileage, year)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        ('V001', 'Tesla Model S', 'Black', 'Electric Motor', '1020', '25', '2024'),
        ('V002', 'BMW X5', 'White', '3.0L I6 Turbo', '335', '25', '2022'),
        ('V003', 'Ford Mustang', 'Blue', '5.0L V8', '450', '25', '2020'),
        ('V004', 'Audi A4', 'Red', '2.0L I4 Turbo', '248', '23', '2023'),
        ('V005', 'Chevrolet Corvette', 'Yellow', '6.2L V8', '495', '26', '2022'),
        ('V006', 'Mercedes-Benz C-Class', 'Silver', '2.0L I4 Turbo', '255', '21', '2021'),
        ('V007', 'Honda Civic', 'Green', '2.0L I4', '158', '18', '2020'),
        ('V008', 'Toyota Camry', 'Black', '2.5L I4', '203', '23', '2021'),
        ('V009', 'Nissan Altima', 'White', '2.5L I4', '182', '25', '2021'),
        ('V010', 'Jaguar F-Type', 'Orange', '5.0L V8', '380', '30', '2021'),
        ('V011', 'Lexus RX', 'Blue', '3.5L V6', '295', '28', '2023'),
        ('V012', 'Porsche 911', 'Silver', '3.0L Twin-Turbo H6', '443', '15', '2023'),
        ('V013', 'Subaru Outback', 'Grey', '2.5L H4', '175', '23', '2022'),
        ('V014', 'Mazda CX-5', 'Red', '2.5L I4', '187', '24', '2021'),
        ('V015', 'Chrysler Pacifica', 'Red', '3.6L V6', '287', '25', '2023'),
        ('V016', 'BMW 3 Series', 'Blue', '2.0L I4 Turbo', '255', '27', '2023'),
        ('V017', 'Ford F-150', 'Black', '3.5L EcoBoost V6', '400', '28', '2022'),
        ('V018', 'Hyundai Elantra', 'Silver', '2.0L I4', '147', '29', '2023')
    ])

    # Insert sample data for veh_info with new fields
    cursor.execute('SELECT COUNT(*) FROM veh_inv')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO veh_inv (veh_inv_id, veh_id, condition, miles_used, price, inventory_count, special_notes, image_url, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('INV001', 'V001', 'Used', 15000, 79999.99, 1, 'A high-performance electric sedan with impressive range and cutting-edge technology.', 'https://media.ed.edmunds-media.com/tesla/model-s/2024/oem/2024_tesla_model-s_sedan_plaid_fq_oem_1_815.jpg', 'Philadelphia, PA'),
            ('INV002', 'V002', 'Used', 30000, 60999.99, 2,'A luxury midsize SUV combining style, comfort, and sport performance for any adventure.', 'https://cache.bmwusa.com/cosy.arox?pov=walkaround&brand=WBBM&vehicle=25XO&client=byoc&paint=P0300&fabric=FKPSW&sa=S01CE,S01SF,S0255,S02TB,S0302,S0319,S0322,S03AT,S03MB,S0402,S0420,S0423,S0459,S0481,S0494,S04FL,S04KR,S04T8,S04UR,S0552,S05AC,S05AS,S05DM,S0676,S06AC,S06AK,S06C4,S06CP,S06NX,S06U2,S0775&angle=30', 'Pittsburgh, PA'),
            ('INV003', 'V003', 'New', 25000, 35999.99, 1,'A classic American muscle car known for its powerful V8 engine and iconic design.', 'https://i.ytimg.com/vi/lEn1jZKgXB4/sddefault.jpg', 'Allentown, PA'),
            ('INV004', 'V004', 'New', 20000, 45999.99, 1, 'A compact luxury sedan offering high-end tech, a smooth ride, and a powerful engine.', 'https://cdn.max.auto/t_hres/110026/WAUEAAF40RN006977/665662925eacd0c1522d7c44.jpg', 'Harrisburg, PA'),
            ('INV005', 'V005', 'New', 5000, 84999.99, 1,'A performance-oriented sports car that embodies American engineering with thrilling speed and agility.', 'https://media.carsandbids.com/cdn-cgi/image/width=2080,quality=70/da4b9237bacccdf19c0760cab7aec4a8359010b0/photos/3zVDVjgP-bWZFfp5WaV2-A47-9Vmg57.jpg?t=165308031771', 'Scranton, PA'),
            ('INV006', 'V006', 'Used', 10000, 55999.99, 2, 'A luxurious compact sedan that offers precision engineering, advanced safety, and premium comfort.', 'https://vehicle-photos-published.vauto.com/04/3f/40/ce-30ec-4c28-b65d-00284ef63a5d/image-2.jpg', 'Lancaster, PA'),
            ('INV007', 'V007', 'Used', 15000, 23999.99, 1, 'A reliable compact car with great fuel efficiency, a comfortable interior, and sleek design.', 'https://www.motortrend.com/uploads/sites/5/2015/04/Honda-Civic-Concept-front-end-03.jpg', 'Reading, PA'),
            ('INV008', 'V008', 'Used', 18000, 27999.99, 1, 'A midsize sedan known for its reliability, comfort, and excellent fuel efficiency.', 'https://vehicle-images.dealerinspire.com/f70e-110007893/4T1DBADK6SU501169/31884f6ef3bcf63a9e1a16826f93c432.jpg', 'Bethlehem, PA'),
            ('INV009', 'V009', 'Used', 22000, 28999.99, 1, 'A stylish midsize sedan offering excellent safety features, technology, and a smooth ride.', 'https://vehicle-images.dealerinspire.com/2451-110005012/1N4BL4DV3SN303721/58cb63ca27eee6aaa3d42d214eec6837.jpg', 'Easton, PA'),
            ('INV010', 'V010', 'Used', 12000, 70999.99, 1, 'A performance-focused luxury sports car combining a stunning design with immense power and handling precision.', 'https://www.marinoperformancemotors.com/imagetag/12929/4/l/Used-2016-Jaguar-F-TYPE-S.jpg', 'York, PA'),
            ('INV011', 'V011', 'Used', 27000, 60999.99, 1, 'A premium crossover SUV offering luxury features, smooth performance, and top-tier safety ratings.', 'https://www.kbb.com/wp-content/uploads/2022/11/2023-lexus-rx350-f-sport-front-left-3qtr.jpg', 'King of Prussia, PA'),
            ('INV012', 'V012', 'Used', 3000, 99999.99, 1, 'An iconic sports car with stunning performance and handling, and a timeless design.', 'https://i.ytimg.com/vi/qnhuEveXoM8/maxresdefault.jpg', 'Chester, PA'),
            ('INV013', 'V013', 'Used', 32000, 35999.99, 1, 'A rugged and versatile crossover SUV ideal for outdoor adventures with all-wheel drive and ample cargo space.', 'https://i.ytimg.com/vi/-grrSULw9hk/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLARiMzy9YuDE4wkvVcoQ9OsKsLenw', 'Pottstown, PA'),
            ('INV014', 'V014', 'Used', 22000, 37999.99, 1, 'A compact crossover with exceptional handling, a premium interior, and great fuel economy.', 'https://www.carpro.com/hs-fs/hubfs/img-6688-1404x1112.jpg?width=1020&name=img-6688-1404x1112.jpg', 'West Chester, PA'),
            ('INV015', 'V015', 'Used', 15000, 42999.99, 1, 'A family-friendly minivan offering ample seating, cargo space, and a hybrid option for better fuel efficiency.', 'https://www.chrysler.com/content/dam/fca-brands/na/chrysler/en_us/2024/pacifica/hybrid/gallery/desktop/my24-chrysler-hybrid-gallery-04-exterior-desktop.jpg.image.1440.jpg', 'Huntingdon Valley, PA'),
            ('INV016', 'V016', 'Used', 24000, 47999.99, 1, 'A compact luxury sedan known for its dynamic driving experience and sophisticated interior.', 'https://www.edmunds.com/assets/m/cs/bltfd77bfe883e04cf6/66562cab0d6347db0279febf/2025_BMW_3-series_3_1600.jpg', 'New Hope, PA'),
            ('INV017', 'V017', 'Used', 28000, 55999.99, 1, 'A powerful and versatile full-size pickup truck designed for heavy-duty tasks and off-road adventures.', 'https://vehicle-images.dealerinspire.com/ab52-110005802/1FTEW2KP2RKE17566/4d23121092bc21826489ad899274c080.jpg', 'Media, PA'),
            ('INV018', 'V018', 'Used', 15000, 21999.99, 1, 'A compact sedan offering a modern design, advanced tech features, and great fuel economy at an affordable price.', 'https://di-uploads-pod27.dealerinspire.com/patrickhyundai/uploads/2022/12/2023-Hyundai-ELANTRA_900x450.jpg', 'Lebanon, PA')
        ])

    # Insert sample data for sale_camp
    cursor.execute('SELECT COUNT(*) FROM sale_camp')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO sale_camp (campaign_id, campaign_desc, start_dt, end_dt)
        VALUES (?, ?, ?, ?)
    ''', [
            ('BF2024', 'Black Friday Sale - Huge discounts on all vehicles.', '2024-11-29', '2024-12-08'),
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
            ('BF2024', 'INV001', round(79999.99 * 0.90, 2)),  # 10% off
            ('BF2024', 'INV002', round(60999.99 * 0.90, 2)),
            ('BF2024', 'INV003', round(35999.99 * 0.90, 2)),
            ('BF2024', 'INV004', round(45999.99 * 0.90, 2)),
            ('BF2024', 'INV006', round(55999.99 * 0.90, 2)),
            ('BF2024', 'INV007', round(23999.99 * 0.90, 2)),
            ('BF2024', 'INV008', round(27999.99 * 0.90, 2)),
            ('BF2024', 'INV009', round(28999.99 * 0.90, 2)),
            ('BF2024', 'INV010', round(70999.99 * 0.90, 2)),
            ('BF2024', 'INV011', round(60999.99 * 0.90, 2)),
            ('BF2024', 'INV012', round(99999.99 * 0.90, 2)),
            ('BF2024', 'INV013', round(35999.99 * 0.90, 2)),
            ('BF2024', 'INV014', round(37999.99 * 0.90, 2)),
            ('BF2024', 'INV015', round(42999.99 * 0.90, 2)),
            ('BF2024', 'INV016', round(47999.99 * 0.90, 2)),
            ('BF2024', 'INV017', round(55999.99 * 0.90, 2)),
            ('BF2024', 'INV018', round(21999.99 * 0.90, 2)),

            # Memorial Day Sale
            ('MD2024', 'INV001', round(79999.99 * 0.95, 2)),  # 5% off
            ('MD2024', 'INV002', round(60999.99 * 0.95, 2)),
            ('MD2024', 'INV003', round(35999.99 * 0.95, 2)),
            ('MD2024', 'INV004', round(45999.99 * 0.95, 2)),
            ('MD2024', 'INV006', round(55999.99 * 0.95, 2)),
            ('MD2024', 'INV007', round(23999.99 * 0.95, 2)),
            ('MD2024', 'INV008', round(27999.99 * 0.95, 2)),
            ('MD2024', 'INV009', round(28999.99 * 0.95, 2)),
            ('MD2024', 'INV010', round(70999.99 * 0.95, 2)),
            ('MD2024', 'INV011', round(60999.99 * 0.95, 2)),
            ('MD2024', 'INV012', round(99999.99 * 0.95, 2)),
            ('MD2024', 'INV013', round(35999.99 * 0.95, 2)),
            ('MD2024', 'INV014', round(37999.99 * 0.95, 2)),
            ('MD2024', 'INV015', round(42999.99 * 0.95, 2)),
            ('MD2024', 'INV016', round(47999.99 * 0.95, 2)),
            ('MD2024', 'INV017', round(55999.99 * 0.95, 2)),
            ('MD2024', 'INV018', round(21999.99 * 0.95, 2)),

            # Thanksgiving Sale
            ('TG2024', 'INV001', round(79999.99 * 0.85, 2)),  # 15% off
            ('TG2024', 'INV002', round(60999.99 * 0.85, 2)),
            ('TG2024', 'INV003', round(35999.99 * 0.85, 2)),
            ('TG2024', 'INV004', round(45999.99 * 0.85, 2)),
            ('TG2024', 'INV006', round(55999.99 * 0.85, 2)),
            ('TG2024', 'INV007', round(23999.99 * 0.85, 2)),
            ('TG2024', 'INV008', round(27999.99 * 0.85, 2)),
            ('TG2024', 'INV009', round(28999.99 * 0.85, 2)),
            ('TG2024', 'INV010', round(70999.99 * 0.85, 2)),
            ('TG2024', 'INV011', round(60999.99 * 0.85, 2)),
            ('TG2024', 'INV012', round(99999.99 * 0.85, 2)),
            ('TG2024', 'INV013', round(35999.99 * 0.85, 2)),
            ('TG2024', 'INV014', round(37999.99 * 0.85, 2)),
            ('TG2024', 'INV015', round(42999.99 * 0.85, 2)),
            ('TG2024', 'INV016', round(47999.99 * 0.85, 2)),
            ('TG2024', 'INV017', round(55999.99 * 0.85, 2)),
            ('TG2024', 'INV018', round(21999.99 * 0.85, 2))
        ])

    # Create cust_reviews  table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cust_reviews  (
           review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cust_id VARCHAR(10),
            veh_inv_id VARCHAR(10),
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            review_text TEXT,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cust_id) REFERENCES cust_info(cust_id),
            FOREIGN KEY (veh_inv_id) REFERENCES veh_inv(veh_inv_id)
        )
    ''')

    conn.commit()
    conn.close()

# API endpoint to get all cars (from veh_info table)
@app.route('/api/cars', methods=['GET'])
def get_cars():
    conn = get_db_connection()
    # Fetch all car details from veh_info and veh_inv tables, joining on veh_id
    query = '''
    SELECT veh_inv.veh_inv_id, veh_info.veh_id, veh_info.veh_name, veh_info.ext_color, veh_info.horsepower, veh_inv.miles_used as mileage, 
        veh_inv.condition, veh_inv.price, veh_inv.inventory_count, veh_inv.special_notes, veh_inv.image_url,
        veh_info.year, veh_inv.location
    FROM veh_info
    LEFT JOIN veh_inv ON veh_info.veh_id = veh_inv.veh_id
    WHERE veh_inv.inventory_count > 0
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
            veh_info.horsepower, veh_inv.miles_used as mileage, veh_inv.condition, 
            veh_inv.price, veh_inv.inventory_count, veh_inv.special_notes, veh_inv.image_url, 
           veh_info.year, veh_info.engine, veh_inv.location
    FROM veh_info
    LEFT JOIN veh_inv ON veh_info.veh_id = veh_inv.veh_id
    WHERE veh_info.veh_id = ?
    AND veh_inv.inventory_count > 0
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM emp_info WHERE emp_id <> "emp0"')
    employee_count = cursor.fetchone()['count']
    cursor.execute('SELECT SUM(inventory_count) as count FROM veh_inv')
    vehicle_count = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM cust_info')
    customer_count = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM purchases')
    transaction_count = cursor.fetchone()['count']
    conn.close()

    if current_user_id:
        current_user = get_username(current_user_id)
        return render_template('index.html', employee_count=employee_count, vehicle_count=vehicle_count, customer_count=customer_count, transaction_count=transaction_count).replace('var currentUser = null;', f'var currentUser = "{current_user}";')
    return render_template('index.html', employee_count=employee_count, vehicle_count=vehicle_count, customer_count=customer_count, transaction_count=transaction_count)



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
            print(f"Current user ID: {current_user_id}")
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

            print(f"Inserting into login_info: {login_id}, {username}, {password}, customer")
            # Insert into login_info table
            cursor.execute('''
                INSERT INTO login_info (login_id, username, password, user_type)
                VALUES (?, ?, ?, ?)
            ''', (login_id, username, password, 'customer'))

            # Generate customer ID (CUST + last 6 digits of login_id)
            cust_id = 'CUST' + login_id[-6:]

            print(f"Inserting into cust_info: {cust_id}, {login_id}, {f_name}, {l_name}, {email}, {phone_num}, {birthday}, {acct_creation_dt}, active")
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

@app.route('/api/cars/search', methods=['GET'])
def search_cars():
    query = request.args.get('query', '').lower()  # Get the search query
    year = request.args.get('year', '')  # Get the year filter
    price_range = request.args.get('price_range', '')  # Get the price range filter
    on_sale = request.args.get('on_sale', 'false').lower() == 'true'  # Check if the 'on_sale' filter is true

    # If there's no query, year, or price range, return empty result
    if not query and not year and not price_range and not on_sale:
        return jsonify([])

    # Build the SQL query for partial matching with optional filters
    query_str = '''
        SELECT veh_info.veh_id, veh_info.veh_name, veh_info.year, veh_inv.price, veh_inv.image_url,
               veh_info.ext_color, veh_info.horsepower, veh_inv.condition, veh_inv.miles_used as mileage,
               sale_camp_detailed.campaign_price AS sale_price
        FROM veh_info
        LEFT JOIN veh_inv ON veh_info.veh_id = veh_inv.veh_id
        LEFT JOIN sale_camp_detailed ON veh_inv.veh_id = sale_camp_detailed.veh_inv_id AND sale_camp_detailed.campaign_price IS NOT NULL
        WHERE LOWER(veh_info.veh_name) LIKE ?
        AND veh_inv.inventory_count > 0
    '''

    # Add the year filter if provided
    if year:
        query_str += ' AND veh_info.year = ?'

    # Add the price range filter if provided
    if price_range:
        # Parse the price range into min and max price
        min_price, max_price = price_range.split('-')
        if max_price:
            query_str += ' AND veh_inv.price BETWEEN ? AND ?'
        else:
            query_str += ' AND veh_inv.price < ?'

    # If the on_sale filter is true, add condition to check for sale_price
    if on_sale:
        query_str += ' AND sale_camp_detailed.campaign_price IS NOT NULL'

    query_str += ' LIMIT 5'  # Limit to top 5 results

    # Execute the query with the search term, optional year, and price range filter
    conn = get_db_connection()
    if year and price_range:
        cars = conn.execute(query_str, ('%' + query + '%', year, min_price, max_price)).fetchall()
    elif year:
        cars = conn.execute(query_str, ('%' + query + '%', year)).fetchall()
    elif price_range:
        cars = conn.execute(query_str, ('%' + query + '%', min_price, max_price)).fetchall()
    elif on_sale:
        cars = conn.execute(query_str, ('%' + query + '%',)).fetchall()  # Just the query and on_sale filter
    else:
        cars = conn.execute(query_str, ('%' + query + '%',)).fetchall()
    conn.close()

    # Return the cars in JSON format
    return jsonify([dict(car) for car in cars])

@app.route('/api/process_payment', methods=['POST'])
def process_payment():
    try:
        # Get the payment data from the request
        payment_data = request.get_json()

        veh_inv_id = payment_data.get('car_id')
        cust_id = current_user_id
        price = payment_data.get('price')
        quantity = payment_data.get('quantity')
        credit_card = payment_data.get('credit_card')
        expiration = payment_data.get('expiration')
        cvv = payment_data.get('cvv')
        emp_id = 'emp00'

        conn = get_db_connection()
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Check if the vehicle is on sale and fetch the sale price
        sale_info = conn.execute('''
            SELECT d.campaign_id 
            FROM sale_camp s
            JOIN sale_camp_detailed d ON s.campaign_id = d.campaign_id
            WHERE d.veh_inv_id = ? AND s.start_dt <= ? AND s.end_dt >= ?
        ''', (veh_inv_id, current_date, current_date)).fetchone()

        conn.close()

        if sale_info:
            campaign_id = sale_info['campaign_id']
        else:
            campaign_id = None

        # Validate input
        if not veh_inv_id or not cust_id or not price or not quantity or not credit_card or not expiration or not cvv:
            return jsonify({"success": False, "message": "Missing payment information"}), 400

        # Check inventory count
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT inventory_count FROM veh_inv WHERE veh_inv_id = ?', (veh_inv_id,))
        car = cursor.fetchone()

        if car is None or car[0] < quantity:
            # If not enough inventory, return error
            return jsonify({"success": False, "message": "Not enough inventory for the selected quantity."}), 400

        # Process the payment (simulated here)
        dupe = True
        while dupe:
            transaction_id = str(random.randint(1000000000, 9999999999))  # Simulate transaction ID
            cursor.execute('SELECT transaction_id FROM purchases WHERE transaction_id = ?', (transaction_id,))
            if cursor.fetchone() is None:
                dupe = False

        # Update inventory
        cursor.execute('UPDATE veh_inv SET inventory_count = inventory_count - ? WHERE veh_inv_id = ?', (quantity, veh_inv_id))
        conn.commit()

        complete_purchase(transaction_id, veh_inv_id, cust_id, campaign_id, emp_id, price, quantity, credit_card, expiration, cvv)

        return jsonify({"success": True, "transaction_id": transaction_id}), 200

    except Exception as e:
        print(f"Error during payment processing: {e}")
        return jsonify({"success": False, "message": "Payment processing failed"}), 500


@app.route('/confirmation')
def confirmation():
    # Get the transaction_id from the query parameters
    transaction_id = request.args.get('transaction_id')

    # Ensure we have a valid transaction ID
    if transaction_id:
        # You can render a confirmation page and pass the transaction ID to it
        return render_template('confirmation.html', transaction_id=transaction_id)
    else:
        # If no transaction_id is found, show an error message
        return 'Error: Transaction ID not found.', 400
    
@app.route('/api/complete_purchase', methods=['POST'])
def complete_purchase(transaction_id, veh_inv_id, cust_id, campaign_id, emp_id, price, quantity, credit_card, expiration, cvv):
    try:
        # Get the request data
        data = request.get_json()
        # Simulate payment processing here (you can use a real payment gateway like Stripe or another service)

        # Assuming payment was successful, create a transaction record
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO purchases (transaction_id, cust_id, emp_id, veh_inv_id, campaign_id, price, quantity, credit_card, expiration, cvv, transaction_date, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_id, cust_id, emp_id, veh_inv_id, campaign_id, price, quantity, credit_card, expiration, cvv, datetime.now(), 'Successful'))
        conn.commit()
        conn.close()
        print("Transaction completed successfully. with values:", transaction_id, veh_inv_id, cust_id, campaign_id, emp_id, price, quantity, credit_card, expiration, cvv)
        # Respond with success
        return jsonify({'success': True, 'transaction_id': transaction_id})

    except Exception as e:
        print("Error processing payment:", e)
        return jsonify({'success': False, 'message': 'Payment failed. Please try again.'}), 500

@app.route('/payment')
def payment():
    if not current_user_id:
        return redirect(url_for('login'))
    return render_template('payment.html')

@app.route('/cars')
def cars():
    return render_template('cars.html')

# Employee list page
@app.route('/employees')
def employees():
    return render_template('employee.html')

# Employee detail page
@app.route('/employee/<emp_id>')
def employee_detail(emp_id):
    return render_template('employee_detail.html')

# API endpoint to get all employees
@app.route('/api/employees')
def get_employees():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ignore employee 0 (online)
    cursor.execute('''
        SELECT emp_id, f_name, l_name, email, phone_num, office_hours, emp_intro, image_url
        FROM emp_info
        WHERE emp_status = 'active'
        AND emp_id <> 'emp0'
    ''')
    
    employees = cursor.fetchall()
    conn.close()
    
    # Convert employees to list of dictionaries
    employee_list = []
    for emp in employees:
        employee_list.append({
            'id': emp['emp_id'],
            'first_name': emp['f_name'],
            'last_name': emp['l_name'],
            'email': emp['email'],
            'phone_number': emp['phone_num'],
            'office_hours': emp['office_hours'],
            'intro': emp['emp_intro'],
            'image_url': emp['image_url']
        })
    
    return jsonify(employee_list)

# API endpoint to get specific employee details
@app.route('/api/employee/<emp_id>')
def get_employee(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT emp_id, f_name, l_name, email, phone_num, office_hours, emp_intro, image_url
        FROM emp_info
        WHERE emp_id = ? AND emp_status = 'active'
    ''', (emp_id,))
    
    emp = cursor.fetchone()
    conn.close()
    
    if emp is None:
        return jsonify({'error': 'Employee not found'}), 404
    
    employee_data = {
        'id': emp['emp_id'],
        'first_name': emp['f_name'],
        'last_name': emp['l_name'],
        'email': emp['email'],
        'phone_number': emp['phone_num'],
        'office_hours': emp['office_hours'],
        'intro': emp['emp_intro'],
        'image_url': emp['image_url']
    }
    
    return jsonify(employee_data)

@app.route('/order_history')
def order_history():
    if not current_user_id:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            p.transaction_id as transaction_id, 
            p.price as price, 
            p.transaction_date as date,
            p.quantity as quantity,
            v.veh_name as vehicle, 
            v.ext_color as color, 
            v.year as year
        FROM purchases p
        JOIN veh_inv vi ON p.veh_inv_id = vi.veh_inv_id
        JOIN veh_info v ON vi.veh_id = v.veh_id
        WHERE p.cust_id = ?
        ORDER BY p.transaction_date DESC
    ''', (current_user_id,))
    
    purchases = cursor.fetchall()
    conn.close()
    
    return render_template('order_history.html', purchases=purchases)


@app.route('/api/reviews/<veh_inv_id>', methods=['GET'])
def get_reviews(veh_inv_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    reviews = cursor.execute('''
        SELECT r.review_id, r.rating, r.review_text, r.review_date,
               c.f_name || " " || c.l_name AS reviewer_name
        FROM cust_reviews r 
        JOIN cust_info c ON r.cust_id = c.login_id 
        WHERE r.veh_inv_id = ?
        ORDER BY r.review_date DESC
        ''',
        (veh_inv_id,)
    ).fetchall()
    
    conn.close()
    
    return jsonify([{
        'review_id': r['review_id'],
        'rating': r['rating'],
        'review_text': r['review_text'],
        'review_date': r['review_date'],
        'reviewer_name': r['reviewer_name']
    } for r in reviews])

@app.route('/api/review', methods=['POST'])
def submit_review():
    if current_user_id is None:
        return jsonify({'error': 'Please log in to submit a review'}), 401

    data = request.get_json()
    veh_inv_id = data.get('veh_inv_id')
    rating = data.get('rating')
    review_text = data.get('review_text')

    if not all([veh_inv_id, rating]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert the review
        cursor.execute('''
            INSERT INTO cust_reviews (cust_id, veh_inv_id, rating, review_text, review_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_user_id, veh_inv_id, rating, review_text, datetime.now()))
        
        conn.commit()
        conn.close()
    except:
        return jsonify({'success': False, 'error': 'Error submitting review'}), 500
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()  # Initialize the database with tables and data
    app.run(debug=True)
