from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    products = []
    with open('static/products.json', 'r') as file:
        data = json.load(file)
        products = data["products"]



    return render_template('index.html', products=products)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "GET":
        return render_template('checkout.html')

if __name__ == '__main__':
    app.debug = True
    app.run()