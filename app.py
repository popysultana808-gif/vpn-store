import os
import json
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ডাটাবেজ সেটআপ (ডাটা সেভ রাখার জন্য)
DB_FILE = "store_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # ইউজার টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    username TEXT,
                    balance REAL DEFAULT 0.0,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    # প্রোডাক্ট টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    category TEXT,
                    price REAL,
                    stock_count INTEGER DEFAULT 0,
                    icon_url TEXT
                )''')
    # স্টক/আইটেম টেবিল (ভিপিএন কী / অ্যাকাউন্ট ডাটা)
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    item_data TEXT,
                    is_sold INTEGER DEFAULT 0
                )''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

# ইউজার অথেন্টিকেশন ও ব্যালেন্স আনা
@app.route('/api/user/sync', methods=['POST'])
def sync_user():
    data = request.json or {}
    user_id = str(data.get('user_id', ''))
    first_name = data.get('first_name', 'User')
    username = data.get('username', '')

    if not user_id:
        return jsonify({'error': 'No user id'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()

    if not user:
        c.execute("INSERT INTO users (user_id, first_name, username, balance) VALUES (?, ?, ?, ?)",
                  (user_id, first_name, username, 0.0))
        conn.commit()
        balance = 0.0
    else:
        balance = user['balance']

    conn.close()
    return jsonify({'success': True, 'balance': balance, 'user_id': user_id})

# প্রোডাক্ট লিস্ট পাওয়া
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'products': products})

# অ্যাডমিন: নতুন প্রোডাক্ট যোগ করা
@app.route('/api/admin/add-product', methods=['POST'])
def add_product():
    data = request.json or {}
    name = data.get('name')
    category = data.get('category', 'VPN')
    price = float(data.get('price', 0))
    icon_url = data.get('icon_url', '')

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO products (name, category, price, stock_count, icon_url) VALUES (?, ?, ?, ?, ?)",
              (name, category, price, 0, icon_url))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Product added!'})

# অ্যাডমিন: ব্যালেন্স অ্যাড করা
@app.route('/api/admin/add-balance', methods=['POST'])
def add_balance():
    data = request.json or {}
    user_id = str(data.get('user_id'))
    amount = float(data.get('amount', 0))

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Balance updated!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
  
