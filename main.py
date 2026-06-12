from flask import Flask, g, render_template
import sqlite3

# Defines the database constant
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

# Gets the database
def database():
    db = get_db()
    cursor = db.cursor()

    # Define the database tables
    tables = ['products', 'customers', 'wishlist', 'categories', 'checkout', 'orders']
    
    # Loops through each table and fetches it's rows
    all_database_data = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        all_database_data[table] = cursor.fetchall()
    return all_database_data

# App route for store page
@app.route('/')
def store():
    # Gets the tables from the database
    all_database_data = database()

    # Renders the store page
    return render_template('store.html', database=all_database_data)

# App route for wishlist page
@app.route('/wishlist')
def wishlist():
    db = get_db()
    cursor = db.cursor()

    # Joins the products table onto the wishlist table
    query = """
            SELECT products.*, wishlist.username FROM wishlist
            LEFT JOIN products ON products.product_id = wishlist.product_id
            WHERE wishlist.username = ?
    """
    
    # Which user's wishlist to look at
    user = "john_doe23"

    # Fetches the data
    cursor.execute(query, (user,))
    wishlist_data = cursor.fetchall()

    # Renders the wishlist page
    return render_template('wishlist.html', database=wishlist_data)

# App route for checkout page
@app.route('/checkout')
def checkout():
    db = get_db()
    cursor = db.cursor()

    # Joins the products table onto the wishlist table
    query = """
            SELECT products.*, checkout.username FROM checkout
            LEFT JOIN products ON products.product_id = checkout.product_id
            WHERE checkout.username = ?
    """
    
    # Which user's wishlist to look at
    user = "john_doe23"

    # Fetches the data
    cursor.execute(query, (user,))
    checkout_data = cursor.fetchall()

    # Renders the checkout page
    return render_template('checkout.html', database=checkout_data)

# App route for profile page
@app.route('/profile')
def profile():
    db = get_db()
    cursor = db.cursor()

    # Joins the products table onto the wishlist table
    query = """
            SELECT products.*, orders.username FROM orders
            LEFT JOIN products ON products.product_id = orders.product_id
            WHERE orders.username = ?
    """
    
    # Which user's wishlist to look at
    user = "john_doe23"

    # Fetches the data
    cursor.execute(query, (user,))
    order_data = cursor.fetchall()

    # Renders the profile page
    return render_template('profile.html', database=order_data)

# App route for login page
@app.route('/login')
def login():
    # Gets the tables from the database
    all_database_data = database()

    # Renders the login page
    return render_template('login.html', database=all_database_data)

# App route for signup page
@app.route('/signup')
def signup():
    # Gets the tables from the database
    all_database_data = database()

    # Renders the signup page
    return render_template('signup.html', database=all_database_data)

# Runs the app
if __name__ == '__main__':
    app.run(debug=True)