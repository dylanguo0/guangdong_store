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

    # Finds all the wishlist items
    wishlist_items = []
    if 'user' in session:
        current_user = session.get('user')
        wishlist_items = [
            row[1] for row in all_database_data['wishlist'] 
            if row[0] == current_user
        ]

    # Renders the store page
    return render_template('store.html', database=all_database_data, wishlist_items=wishlist_items)

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

    # Which users profile to look at
    user = session.get('user')

    # Query for account details
    cursor.execute("SELECT * FROM customers WHERE username = ?", (user,))
    user_info = cursor.fetchone()

    # Query for orders
    query = """
            SELECT products.*, order_ids.*, order_items.* FROM order_items
            LEFT JOIN order_ids ON order_ids.order_id = order_items.order_id
            LEFT JOIN products ON products.product_id = order_items.product_id
            WHERE order_ids.username = ?
    """

    # Fetches the data
    cursor.execute(query, (user,))
    order_data = cursor.fetchall()

    # Renders the profile page
    return render_template('profile.html', user_info=user_info, database=order_data)

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
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get the form data
        email = request.form.get("email")
        address = request.form.get("address")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        password = request.form.get("password")

        # Fetch all data
        all_tables = database()
        
        # Extract only the users table
        users = all_tables.get("customers", []) 

        # Loop through the list to check if username is already taken
        username_exists = False
        for user in users:
            if user[0] == username:  
                username_exists = True
                break

        # Gives error if username is already in use
        if username_exists:
            return render_template("signup.html", 
                                   error="Username already in use")
        else:
            db = get_db()
            cursor = db.cursor()
            
            # Insert the user into the database
            query = """
                INSERT INTO customers (username, password, first_name, last_name, address, email) 
                VALUES (?, ?, ?, ?, ?, ?)
            """

            # Saves the database
            cursor.execute(query, (username, password, first_name, last_name, address, email))
            db.commit()

            # Logs them in then goes to the store page
            session['user'] = username
            return redirect(url_for("store"))

    # Renders the signup page initially
    return render_template('signup.html', error=None)

# App route to logout
@app.route('/logout')
def logout():
    # Logs out
    session.clear() 
    
    # Returns to login page
    return redirect(url_for('login'))

# App route to add to cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Gets the product ID
    product_id = request.form.get('product_id')
    
    # Gets the current logged in user
    user = session.get('user')

    # Gets the URL so it returns to either the store or wishlist page depending where the user is
    url = request.form.get('url')
    
    # Insert into checkout table
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO checkout (username, product_id) VALUES (?, ?)", (user, product_id))
    db.commit()
    
    # Refreshes store page
    return redirect(url)

# App route to add to wishlist
@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    # Gets the product ID
    product_id = request.form.get('product_id')

    # Gets the current logged in user
    user = session.get('user')

    db = get_db()
    cursor = db.cursor()

    # Check if the user already has this item in their wishlist
    cursor.execute("SELECT 1 FROM wishlist WHERE username = ? AND product_id = ?", (user, product_id))
    wishlist_exists = cursor.fetchone()

    if wishlist_exists:
        all_database_data = database()
        return render_template("store.html", database=all_database_data,
                                error="Already wishlisted")
    else:
        # Insert into wishlist table
        cursor.execute("INSERT INTO wishlist (username, product_id) VALUES (?, ?)", (user, product_id))
        db.commit()
    
    # Refreshes the page the user is on
    return redirect(url_for('store'))

# App route to remove from wishlist
@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    # Gets the product ID
    product_id = request.form.get('product_id')
    
    # Gets the current logged in user
    user = session.get('user')
    
    # Delete from wishlist table
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM wishlist WHERE username = ? AND product_id = ?", 
        (user, product_id)
    )
    db.commit()
    
    # Refreshes wishlist page
    return redirect(url_for('wishlist'))

# App route to remove from checkout
@app.route('/remove_from_checkout', methods=['POST'])
def remove_from_checkout():
    # Gets the product ID
    product_id = request.form.get('product_id')
    
    # Gets the current logged in user
    user = session.get('user')
    
    # Delete from checkout table
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """DELETE FROM checkout 
        WHERE ROWID = (
            SELECT ROWID FROM checkout 
            WHERE username = ? AND product_id = ? 
            LIMIT 1)""", 
        (user, product_id)
    )
    db.commit()
    
    # Refreshes checkout page
    return redirect(url_for('checkout'))

# Runs the app
if __name__ == '__main__':
    app.run(debug=True)