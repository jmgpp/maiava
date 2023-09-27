import json
import psycopg2


POSTGRESQL_URI = "postgres://crtslvzw:DHUqbbQyZZ95UjYfiuInf1ERhb9ROiXn@motty.db.elephantsql.com/crtslvzw"
connection = psycopg2.connect(POSTGRESQL_URI)
products = []


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
            print(products)