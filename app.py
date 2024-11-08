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

if __name__ == '__main__':
    init_db()  # Initialize the database with tables and data
    app.run(debug=True)
