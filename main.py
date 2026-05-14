from flask import Flask, render_template

app = Flask(__name__,
            template_folder='website/templates', 
            static_folder='website/static')

@app.route('/')
def home():
    return render_template('store.html')

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

if __name__ == '__main__':
    app.run(debug=True)