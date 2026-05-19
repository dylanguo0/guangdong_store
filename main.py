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

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def store():
    db = get_db()
    cursor = db.cursor()

    tables = ['products', 'customers', 'wishlist', 'categories', 'orders']
    
    all_database_data = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        all_database_data[table] = cursor.fetchall()
    
    return render_template('store.html', database=all_database_data)


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