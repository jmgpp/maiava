# Maiava Store
#### Video Demo:
#### Site URL: https://maiava-project.onrender.com/
#### Source code: https://github.com/jmgpp/maiava
#### Description:
    It is a simple E-commerce solution made with Flask for the backend connected to a PosgreSQL database and to Firebase Storage for the product images.


## Structure
    The project is structured in 2 entities: A web shop for the clients and the admin tool for the store manager. Clients in the store can search, add and remove items from the cart and when ready proceed with tha purchase. The admin tool allows the manager to see the pending orders and chance the state accordingly and add, edit or hide the products available in the store.


## Client Store

## Home Page
# "/" route - Python
    The initial route when the app is launched is "/".
    The index function will first fetch products with 'stock > 0' and the 'visible == true' from the DB and populate a list 'products' that will be passed as an argument to index.html to render.

# index.html
    Index inherits the header and footer from 'templates/layout.html' is composed of a main body and an offcanvas item hiding at the right of the screen for the shopping cart.

    The main container is populated by the 'drawGrid()' function with the list of products of the DB that were passed by the router.
    
    The offcanvas main body is a container with an <ul> list that will be populated by the JS function 'drawList()' using the items of the 'cartItems' array. And a button that will trigger 'goToCheckout()' that will convert the items in the cart in a JSON string and submit the form to proceed to checkout.

    Additionally there are functions for adding and removing items from the cart and utility functions to display stylized alerts and format numbers as currency.

## Checkout
# "/checkout" route - Python
    This route simply recieves the string of items in the cart via a POST form, parses it as a JSON dictionary and passes it to checkout.html.

# checkout.html
    The checkout page is composed of 2 main Divs, one with the looks and functionality of the offcanvas cart of the homepage that is populated by en event triggered when the page loads and captures the passed data using the Jinja sintax. And the second being just a form to complete the buyer's information. 'completeOrder()' will complete a series and submit the form for the router to perform the final validations at '/purchase' and complete the order.

# "/purchase" route - Python
    Purchase will recieve the client info and the products to buy. Check with de DB that the items are still in stock, and if so check if the client 'email' is already in 'clients' and add or use the client to create a new entry in 'orders', add the items to the table 'order-items', reduce the stock from the table 'products' and redirect the user to 'success.html' where the user will be able to return to the store. If any of these fails the client will be redirected to 'failed.html'.


## Admin Tool

## Orders
# "/admin" route - Python
    This could potentially present a dashboard, currently inly redirects to "/orders".

 # "/orders" route - Python
    Orders queries the DB for all the orders, and the items of each one and composses all in a dictionary to pass pass to 'orders.html'.

# orders.html
    This documents starts with an Event Listener that is triggered when the page loads, parses the list sent by the router and passes it as a parameter for 'drawOrders()' to create the mail list on in the body.
    In this list we can see the order information, expand details to see the items in the order and change the selected order state as necessary. 'updateOrder()' will be in charge to compose the information about the selected order and submit it to "/update_orders".
    There are also functions to filter the Orders list and to format dates and currencies as needed.

# "/update_orders" route - Python
    This is a simple route. It pick up the submitted 'id' and 'status', updates the corresponding order in the DB and returns the user to "/orders". In the case the order is being cancelled it will alse run 'cancel_order()' that will take care of updating the stock in 'products' for each item in the cancelled order.
    
# "/products" route - Python
    Products can be reached by either GET or POST methods.
    In the case of GET it will query the DB for all the products, create a list of dictionaries 'products' and pass it to "products.html". The route will be accessed via 'POST' in the case we are adding a new product to the DB, so it will perform this action first and then continue with the same process as GET.

 # products.html
    The page is composed by 3 parts. The main table in the middle and 2 offcanvas windows (invisible) at the right.
    The table is populated with the 'drawProducts()' function and then reformatted using the DataTables library for JS to add the functionality to sort the items by the different columns which I considered neccessary to handle a big number of potential products. There is a complemetary function 'getVisibleButton()' creates the 'hide' or 'show' button depending of the product current state. 
    The 2 offcanvas windows look the same to the user and are for either creating a new product or editing an existing one.
    Products also has the credentials for a connection with Firebase (I will remove them soon, this is just a demo). While the app it is not using a Firebase DB, it is using a storage bucket for product images through the service.
    The functions 'addProduct()', 'submitEdit()' and 'productVisible()' will submit the corresponding forms for the products to update.
    'previewImage()' and 'previewEditImage()' are triggered by an event when the user selects a file in the corresponding offcanvas window.
    The changes in this page can route to "/visible", "/edit" or come back to "/products" as by POST.

 # "/visible" and "/edit" routes - Python
    Both these routes will update the 'products' table in the DB after parsing the 'id' of the product to modify and the values submitted in the corresponding form before redirecting the user back to "/products";
