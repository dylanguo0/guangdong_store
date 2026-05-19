from flask import Flask, g, render_template
import sqlite3

DATABASE = 'guangdong_store.db'

app = Flask(__name__,
            template_folder='website/templates', 
            static_folder='website/static')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    
    # 1. Fetch data from your database table
    cursor.execute("SELECT * FROM products")
    all_products = cursor.fetchall()
    
    # 2. Extract the first row if data exists, otherwise use fallback text
    product_data = all_products[0] if all_products else ["", "", "Default Product", "", ""]
    
    # 3. Pass the variable into the template using products=product_data
    return render_template('store.html', products=product_data)

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)