from flask import Flask, render_template, redirect, request
import json
import locale
import psycopg2


app = Flask(__name__)

POSTGRESQL_URI = "postgres://crtslvzw:DHUqbbQyZZ95UjYfiuInf1ERhb9ROiXn@motty.db.elephantsql.com/crtslvzw"


@app.route('/')
def index():
    
    products = []
    """ with open('static/products.json', 'r') as file:
        data = json.load(file)
        products = data["products"] """
    connection = psycopg2.connect(POSTGRESQL_URI)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT id, brand, title, price, stock, thumbnail
            FROM "public"."products"
            WHERE "visible" = true LIMIT 100""")
            # Fetch all rows as a list of tuples
            rows = cursor.fetchall()

            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description]

            # Convert each row into a dictionary
            for row in rows:
                product_dict = dict(zip(columns, row))
                products.append(product_dict)
    cursor.close()
    connection.close()
       

    for p in products:
        p['priceStr'] = format_currency(p['price'])
        p['price'] = float(p['price'])
        

    return render_template('index.html', products=products)

@app.route("/checkout", methods=["POST"])
def checkout():
    if request.method == "POST":
        data = request.form.get("products")
        items = json.loads(data)
        
        return render_template('checkout.html', items=items)

@app.route("/purchase", methods=["POST"])
def purchase():
    if request.method == "POST":
        data = request.form.get("products")
        products = json.loads(data)
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")

        db_products = []
        ids = [product["id"] for product in products]

        connection = psycopg2.connect(POSTGRESQL_URI)
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id, brand, title, price, stock, thumbnail FROM products WHERE id IN %s"
                cursor.execute(query, (tuple(ids),))
                # Fetch all rows as a list of tuples
                rows = cursor.fetchall()

                # Get column names from cursor description
                columns = [desc[0] for desc in cursor.description]

                # Convert each row into a dictionary
                for row in rows:
                    product_dict = dict(zip(columns, row))
                    product_dict['price'] = float(product_dict['price'])
                    db_products.append(product_dict)
        cursor.close()
        connection.close()
        
        products = sorted(products, key=lambda x: x['id'])
        db_products = sorted(db_products, key=lambda x: x['id'])
        
        for i, p in enumerate(products):
            if p['amount'] > db_products[i]['stock']:
                return render_template('failed.html')
        
        client_id = get_client(name=name,email=email,phone=phone)
        

    return redirect("/")
        
def format_currency(amount):
    locale.setlocale(locale.LC_ALL, '')

    num = locale.format_string("%.2f", amount, grouping=True)
    return f"$ {num}"

def get_client(name, email, phone):
    connection = psycopg2.connect(POSTGRESQL_URI)
    with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM clients WHERE email = %s", (email,))
                existing_client_id = cursor.fetchone()

                if existing_client_id:
                    return existing_client_id[0]
                else:
                    # Email doesn't exist, add a new client
                    cursor.execute("INSERT INTO clients (name, email, phone) VALUES (%s, %s, %s) RETURNING id", (name, email, phone))
                    new_client_id = cursor.fetchone()[0]
                    connection.commit()
                    return new_client_id
    
if __name__ == '__main__':
    app.debug = True
    app.run()