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

# App route for store page
@app.route('/')
def store():
    db = get_db()
    cursor = db.cursor()

    # Define the database tables
    tables = ['products', 'customers', 'wishlist', 'categories', 'orders']
    
    # Loops through each table and fetches it's rows
    all_database_data = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        all_database_data[table] = cursor.fetchall()
    
    # Renders the store page
    return render_template('store.html', database=all_database_data)

# App route for wishlist page
@app.route('/wishlist')
def wishlist():
    # Renders the wishlist page
    return render_template('wishlist.html')

# App route for checkout page
@app.route('/checkout')
def checkout():
    # Renders the checkout page
    return render_template('checkout.html')

# App route for profile page
@app.route('/profile')
def profile():
    # Renders the profile page
    return render_template('profile.html')

# App route for login page
@app.route('/login')
def login():
    # Renders the login page
    return render_template('login.html')

# App route for signup page
@app.route('/signup')
def signup():
    # Renders the signup page
    return render_template('signup.html')

# Runs the app
if __name__ == '__main__':
    app.run(debug=True)