from flask import Flask, render_template, request
import json
import locale
import psycopg2


app = Flask(__name__)

POSTGRESQL_URI = "postgres://crtslvzw:DHUqbbQyZZ95UjYfiuInf1ERhb9ROiXn@motty.db.elephantsql.com/crtslvzw"
connection = psycopg2.connect(POSTGRESQL_URI)

@app.route('/')
def index():
    
    products = []
    """ with open('static/products.json', 'r') as file:
        data = json.load(file)
        products = data["products"] """

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM "public"."products" LIMIT 100""")
            # Fetch all rows as a list of tuples
            rows = cursor.fetchall()

            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description]

            # Convert each row into a dictionary
            for row in rows:
                product_dict = dict(zip(columns, row))
                products.append(product_dict)
            
       

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