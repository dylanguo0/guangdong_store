from flask import Flask, g, render_template, request, redirect, url_for, session
import sqlite3

# Defines the database constant
DATABASE = 'guangdong_store.db'

app = Flask(__name__,
            template_folder='website/templates', 
            static_folder='website/static')

app.config['SECRET_KEY'] = 'test'

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
    tables = ['products', 'customers', 'wishlist', 'categories', 'checkout', 'order_ids', 'order_items']
    
    # Loops through each table and fetches it's rows
    all_database_data = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        all_database_data[table] = cursor.fetchall()
    return all_database_data

# App route for store page
@app.route('/store')
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
    user = session.get('user')

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
    user = session.get('user')

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
            SELECT customers.*, products.*, order_ids.*, order_items.* FROM order_items
            LEFT JOIN order_ids ON order_ids.order_id = order_items.order_id
            LEFT JOIN products ON products.product_id = order_items.product_id
            LEFT JOIN customers ON customers.username = order_ids.username
            WHERE order_ids.username = ?
    """
    
    # Which user's wishlist to look at
    user = session.get('user')
    # Fetches the data
    cursor.execute(query, (user,))
    order_data = cursor.fetchall()

    # Renders the profile page
    return render_template('profile.html', database=order_data)

# App route for login page
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get the form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Fetch all data
        all_tables = database()
        
        # Extract only the users table
        users = all_tables.get("customers", []) 

        # Loop through the list to look for a match
        user_found = False
        for user in users:
            if user[0] == username and user[1] == password:
                user_found = True
                break

        # Check credentials
        if user_found:
            session['user'] = username
            return redirect(url_for("store"))
        else:
            return render_template("login.html",
                                   error="Invalid username or password")

    # Renders the login page
    return render_template('login.html', error=None)

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