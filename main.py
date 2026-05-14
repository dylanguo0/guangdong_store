from flask import Flask, render_template

app = Flask(__name__,
            template_folder='website/templates', 
            static_folder='website/static')

@app.route('/')
def home():
    return render_template('store.html')

if __name__ == '__main__':
    app.run(debug=True)