import os
import json
import sqlite3
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# অ্যাডমিন কনফিগারেশন
ADMIN_ID = "8919985167"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

DB_FILE = "store_database.db"

# প্রতিটি প্রক্সির ডিফল্ট ডাটা ও হাই-কোয়ালিটি ভেক্টর আইকন
DEFAULT_PRODUCTS = [
    {"name": "711 proxy", "category": "Proxy", "plan": "200 MB – 1 GB", "price": 35.0, "stock": 100, "icon": "https://api.iconify.design/logos:cloudflare-icon.svg"},
    {"name": "hub proxy", "category": "Proxy", "plan": "200 MB – 1 GB", "price": 35.0, "stock": 85, "icon": "https://api.iconify.design/fluent-emoji:shield.svg"},
    {"name": "proxy001", "category": "Proxy", "plan": "200 MB – 1 GB", "price": 35.0, "stock": 40, "icon": "https://api.iconify.design/flat-color-icons:radar-plot.svg"},
    {"name": "miyaproxy", "category": "Proxy", "plan": "1 GB", "price": 115.0, "stock": 50, "icon": "https://api.iconify.design/emojione-v1:lightning.svg"},
    {"name": "owlproxy proxy", "category": "Proxy", "plan": "200 MB", "price": 15.0, "stock": 200, "icon": "https://api.iconify.design/twemoji:owl.svg"},
    {"name": "9 proxy", "category": "Proxy", "plan": "200 MB – 1 GB", "price": 25.0, "stock": 120, "icon": "https://api.iconify.design/flat-color-icons:number-9.svg"},
    {"name": "dataimpulse proxy", "category": "Proxy", "plan": "1 GB", "price": 130.0, "stock": 35, "icon": "https://api.iconify.design/carbon:data-blob.svg"},
    {"name": "rapid proxy", "category": "Proxy", "plan": "200 – 1 GB", "price": 30.0, "stock": 60, "icon": "https://api.iconify.design/flat-color-icons:flash-on.svg"},
    {"name": "cli proxy", "category": "Proxy", "plan": "1 GB", "price": 99.0, "stock": 15, "icon": "https://api.iconify.design/vscode-icons:file-type-terminal.svg"},
    {"name": "H143 Proxy Lite 100(Mb)", "category": "Proxy", "plan": "100 MB", "price": 6.5, "stock": 330, "icon": "https://api.iconify.design/flat-color-icons:data-shield.svg"},
    {"name": "Abc Proxy", "category": "Proxy", "plan": "1 GB", "price": 225.0, "stock": 80, "icon": "https://api.iconify.design/emojione:input-latin-letters.svg"},
    {"name": "proxy seller", "category": "Proxy", "plan": "1 GB", "price": 165.0, "stock": 25, "icon": "https://api.iconify.design/flat-color-icons:shop.svg"},
    {"name": "bunny proxy", "category": "Proxy", "plan": "1 GB", "price": 110.0, "stock": 90, "icon": "https://api.iconify.design/noto:rabbit-face.svg"},
    {"name": "H143 Proxy (1Gb)", "category": "Proxy", "plan": "1 GB", "price": 65.0, "stock": 6, "icon": "https://api.iconify.design/flat-color-icons:lock.svg"},
    {"name": "metamax proxy", "category": "Proxy", "plan": "1 GB", "price": 110.0, "stock": 110, "icon": "https://api.iconify.design/flat-color-icons:cube.svg"},
    {"name": "nov proxy", "category": "Proxy", "plan": "1 GB", "price": 125.0, "stock": 45, "icon": "https://api.iconify.design/flat-color-icons:globe.svg"},
    {"name": "rocket proxy", "category": "Proxy", "plan": "1 GB", "price": 165.0, "stock": 30, "icon": "https://api.iconify.design/fluent-emoji:rocket.svg"},
    {"name": "1024 proxy", "category": "Proxy", "plan": "1 GB", "price": 110.0, "stock": 40, "icon": "https://api.iconify.design/flat-color-icons:database.svg"},
    {"name": "922 proxy", "category": "Proxy", "plan": "1 GB", "price": 115.0, "stock": 70, "icon": "https://api.iconify.design/twemoji:globe-showing-americas.svg"},
    {"name": "b2 proxy", "category": "Proxy", "plan": "1 GB", "price": 130.0, "stock": 12, "icon": "https://api.iconify.design/flat-color-icons:key.svg"},
    {"name": "helodata proxy", "category": "Proxy", "plan": "1 GB", "price": 130.0, "stock": 50, "icon": "https://api.iconify.design/flat-color-icons:cloud.svg"},
    {"name": "iproket proxy", "category": "Proxy", "plan": "2 GB", "price": 245.0, "stock": 15, "icon": "https://api.iconify.design/twemoji:satellite-antenna.svg"},
    {"name": "loki proxy", "category": "Proxy", "plan": "1 GB", "price": 130.0, "stock": 25, "icon": "https://api.iconify.design/flat-color-icons:broken-link.svg"},
    {"name": "nodemaven proxy", "category": "Proxy", "plan": "240 MB", "price": 99.0, "stock": 18, "icon": "https://api.iconify.design/flat-color-icons:mind-map.svg"},
    {"name": "proxy deal", "category": "Proxy", "plan": "2 GB", "price": 220.0, "stock": 44, "icon": "https://api.iconify.design/flat-color-icons:money-transfer.svg"},
    {"name": "rola proxy residential", "category": "Proxy", "plan": "1 GB", "price": 165.0, "stock": 60, "icon": "https://api.iconify.design/flat-color-icons:internal.svg"},
    {"name": "safari proxy", "category": "Proxy", "plan": "1 GB", "price": 90.0, "stock": 35, "icon": "https://api.iconify.design/flat-color-icons:compass.svg"},
    {"name": "swift proxy", "category": "Proxy", "plan": "10 GB", "price": 1299.0, "stock": 10, "icon": "https://api.iconify.design/fluent-emoji:high-voltage.svg"},
    {"name": "thordata proxy", "category": "Proxy", "plan": "2 GB", "price": 250.0, "stock": 80, "icon": "https://api.iconify.design/flat-color-icons:electronics.svg"}
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    username TEXT,
                    balance REAL DEFAULT 0.0
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    category TEXT,
                    plan TEXT,
                    price REAL,
                    stock INTEGER,
                    icon TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    product_name TEXT,
                    amount REAL,
                    delivered_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # প্রাথমিক প্রোডাক্ট লোড করা
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        for p in DEFAULT_PRODUCTS:
            c.execute("INSERT INTO products (name, category, plan, price, stock, icon) VALUES (?, ?, ?, ?, ?, ?)",
                      (p['name'], p['category'], p['plan'], p['price'], p['stock'], p['icon']))
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def send_telegram(chat_id, text):
    if BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=5)
        except Exception as e:
            print("Telegram Error:", e)

@app.route('/')
def home():
    return render_template('index.html')

# ইউজার অথেন্টিকেশন ও ব্যালেন্স লোড
@app.route('/api/user/sync', methods=['POST'])
def sync_user():
    data = request.json or {}
    user_id = str(data.get('user_id', ''))
    first_name = data.get('first_name', 'Guest')
    username = data.get('username', '')

    if not user_id:
        return jsonify({'error': 'Missing ID'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    u = c.fetchone()
    if not u:
        c.execute("INSERT INTO users (user_id, first_name, username, balance) VALUES (?, ?, ?, 0.0)",
                  (user_id, first_name, username))
        conn.commit()
        balance = 0.0
    else:
        balance = u['balance']

    is_admin = (user_id == ADMIN_ID)
    conn.close()
    return jsonify({'success': True, 'balance': balance, 'is_admin': is_admin})

# প্রোডাক্ট লিস্ট
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY id ASC")
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'products': products})

# প্রোডাক্ট অর্ডার ও ইনস্ট্যান্ট ডেলিভারি
@app.route('/api/buy', methods=['POST'])
def buy_product():
    data = request.json or {}
    user_id = str(data.get('user_id', ''))
    prod_id = data.get('product_id')

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    c.execute("SELECT * FROM products WHERE id = ?", (prod_id,))
    prod = c.fetchone()

    if not user or not prod:
        conn.close()
        return jsonify({'success': False, 'message': 'অর্ডার ব্যর্থ হয়েছে!'}), 400

    if prod['stock'] <= 0:
        conn.close()
        return jsonify({'success': False, 'message': 'স্টক শেষ হয়ে গেছে!'}), 400

    if user['balance'] < prod['price']:
        conn.close()
        return jsonify({'success': False, 'message': 'পর্যাপ্ত ব্যালেন্স নেই! ডিপোজিট করুন।'}), 400

    # ব্যালেন্স ও স্টক আপডেট
    new_bal = user['balance'] - prod['price']
    c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_bal, user_id))
    c.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (prod_id,))

    # স্বয়ংক্রিয় প্রক্সি কি তৈরি
    generated_key = f"PRX-{prod['name'][:4].upper()}-{os.urandom(4).hex().upper()}"
    c.execute("INSERT INTO orders (user_id, product_name, amount, delivered_key) VALUES (?, ?, ?, ?)",
              (user_id, prod['name'], prod['price'], generated_key))
    conn.commit()
    conn.close()

    # টেলিগ্রামে মেসেজ পাঠানো
    msg = (f"🎉 <b>অর্ডার সফল হয়েছে!</b>\n\n"
           f"📦 <b>প্রোডাক্ট:</b> {prod['name']} ({prod['plan']})\n"
           f"💰 <b>মূল্য:</b> ৳{prod['price']}\n"
           f"🔑 <b>আপনার কী/কনফিগ:</b> <code>{generated_key}</code>\n\n"
           f"ধন্যবাদ আমাদের সাথে থাকার জন্য!")
    send_telegram(user_id, msg)

    return jsonify({'success': True, 'key': generated_key, 'new_balance': new_bal})

# ডিপোজিট রিকোয়েস্ট পাঠানো
@app.route('/api/deposit/request', methods=['POST'])
def deposit_req():
    data = request.json or {}
    user_id = str(data.get('user_id', ''))
    method = data.get('method', 'bKash')
    amount = data.get('amount', 0)
    trxid = data.get('trxid', '')

    alert_text = (f"🔔 <b>নতুন ডিপোজিট রিকোয়েস্ট!</b>\n\n"
                  f"👤 ইউজার আইডি: <code>{user_id}</code>\n"
                  f"💳 মেথড: {method}\n"
                  f"💵 পরিমাণ: ৳{amount}\n"
                  f"🧾 TrxID: <code>{trxid}</code>\n\n"
                  f"ব্যালেন্স যুক্ত করতে অ্যাডমিন প্যানেল ব্যবহার করুন।")
    send_telegram(ADMIN_ID, alert_text)
    return jsonify({'success': True, 'message': 'ডিপোজিট রিকোয়েস্ট অ্যাডমিনের কাছে পাঠানো হয়েছে!'})

# অ্যাডমিন: নতুন প্রোডাক্ট যোগ
@app.route('/api/admin/add-product', methods=['POST'])
def admin_add_prod():
    data = request.json or {}
    if str(data.get('admin_id')) != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 403

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO products (name, category, plan, price, stock, icon) VALUES (?, ?, ?, ?, ?, ?)",
              (data['name'], data['category'], data['plan'], float(data['price']), int(data['stock']), data['icon']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'নতুন প্রোডাক্ট যুক্ত হয়েছে!'})

# অ্যাডমিন: ব্যালেন্স যোগ করা
@app.route('/api/admin/add-balance', methods=['POST'])
def admin_add_bal():
    data = request.json or {}
    if str(data.get('admin_id')) != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 403

    target_id = str(data.get('target_user_id'))
    amount = float(data.get('amount', 0))

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_id))
    conn.commit()
    conn.close()

    send_telegram(target_id, f"✅ আপনার অ্যাকাউন্টে <b>৳{amount}</b> যুক্ত করা হয়েছে!")
    return jsonify({'success': True, 'message': 'ব্যালেন্স আপডেট সফল!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
