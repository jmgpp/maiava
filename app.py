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
            WHERE "visible" = true AND "stock" > 0""")
            
            rows = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]

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
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

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
        
        client_id = get_client(name,email,phone)
        order_id = generate_order(client_id, products)
        

    return render_template("success.html")

@app.route("/admin", methods=["GET"])
def success():
    return render_template("admin.html")

@app.route("/orders", methods=["GET"])
def orders():
    orders = []
    connection = psycopg2.connect(POSTGRESQL_URI)
    with connection:
        with connection.cursor() as cursor:
            query = """
                        SELECT orders.id as id, orders.date as date, clients.name as client, orders.total as total, "order-status".status as status
                        FROM orders 
                        JOIN clients ON orders.client_id = clients.id
                        JOIN "order-status" ON orders.status_id = "order-status".id
                        ORDER BY id DESC;
                    """
            cursor.execute(query)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            for row in rows:
                order_dict = dict(zip(columns, row))
                order_dict['total'] = float(order_dict['total'])
                orders.append(order_dict)
    cursor.close()
    connection.close()


    return render_template("orders.html", orders=orders)

@app.route("/update_orders", methods=["POST"])
def update_orders():
    if request.method == "POST":
        data_id = request.form.get("id")
        data_status = request.form.get("status")
        
        connection = psycopg2.connect(POSTGRESQL_URI)
        with connection:
            with connection.cursor() as cursor:
                query = """
                            UPDATE orders
                            SET status_id = %s
                            WHERE id = %s;

                        """
                cursor.execute(query, (data_status, data_id))
        connection.commit()


        return redirect('/orders')
    

"""
@app.route("/success", methods=["GET"])
def success():
    return render_template("success.html")

@app.route("/failed", methods=["GET"])
def failed():
    return render_template("failed.html")
 """        
def format_currency(amount):
    locale.setlocale(locale.LC_ALL, '')

    num = locale.format_string("%.2f", amount, grouping=True)
    return f"$ {num}"

def generate_order(client_id, products):
    total = 0
    for p in products:
        total += p['price'] * p['amount']
    
    connection = psycopg2.connect(POSTGRESQL_URI)
    with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO orders (client_id, total, status_id) VALUES (%s, %s, 1) RETURNING id", (client_id, total))
                order_id = cursor.fetchone()

                for p in products:
                    cursor.execute("INSERT INTO \"order-items\" (order_id, product_id, price, amount) VALUES (%s, %s, %s, %s)", (order_id, p['id'], p['price'], p['amount']))

                    cursor.execute("UPDATE products SET stock = stock - %s", (p['amount'],))

            connection.commit()

    return order_id
    

def get_client(name, email, phone):
    connection = psycopg2.connect(POSTGRESQL_URI)
    with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM clients WHERE email = %s", (email,))
                existing_client_id = cursor.fetchone()

                if existing_client_id:
                    return existing_client_id[0]
                else:
                    cursor.execute("INSERT INTO clients (name, email, phone) VALUES (%s, %s, %s) RETURNING id", (name, email, phone))
                    new_client_id = cursor.fetchone()[0]
                    connection.commit()
                    return new_client_id
    
if __name__ == '__main__':
    app.debug = True
    app.run()