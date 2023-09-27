from flask import Flask, render_template, request
import json
import locale
import sys


app = Flask(__name__)

@app.route('/')
def index():
    
    products = []
    with open('static/products.json', 'r') as file:
        data = json.load(file)
        products = data["products"]

    for p in products:
        p['priceStr'] = format_currency(p['price'])
        

    return render_template('index.html', products=products)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        data = request.form.get("products")
        items = json.loads(data)
        
        return render_template('checkout.html', items=items)
        
def format_currency(amount):
    locale.setlocale(locale.LC_ALL, '')

    num = locale.format_string("%.2f", amount, grouping=True)
    return f"$ {num}"

if __name__ == '__main__':
    app.debug = True
    app.run()