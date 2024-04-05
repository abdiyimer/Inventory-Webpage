# Import necessary modules
import bottle
import sqlite3
from bottle import Bottle, run, request, redirect, template

# Initialize the Bottle app
app = Bottle()

# SQLite database setup
db_path =  'C:/Users/asus/Desktop/Spare Part/Bottle Frame work/spare_part_shop.db'

def create_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT,
                       password TEXT)''')
    conn.commit()
    conn.close()

# Function to validate user credentials
def validate_login(username, password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Create the login page
@app.route('/')
def login():
    return template('login', error=None)

# Handle login form submission
@app.route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')

    if validate_login(username, password):
        redirect('/main')
    else:
        return template('login', error='Login failed. Please try again.')

# Create the main page
@app.route('/main')
def main_page():
    return template('main')

# Create the fancy brown page
#@app.route('/fancy')
#def fancy_page():
 #   return template('fancy')


# Update the fancy_page route to pass the necessary data
@app.route('/fancy')
def fancy_page():
    # Retrieve the list of products from the database or any other source
    products = retrieve_products_from_database()  # Update this function as needed
    return template('fancy', Products=products)



# Function to retrieve employees from the database
def retrieve_employees():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Employees")
    employees = cursor.fetchall()
    conn.close()
    return employees

# Route to display the Employees page
@app.route('/employees')
def employees_page():
    employees = retrieve_employees()
    return bottle.template('employees_page', employees=employees)


# Function to retrieve loyal customers from the database
def retrieve_loyal_customers():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    loyal_customers = cursor.fetchall()
    conn.close()
    return loyal_customers


# Route to display the Loyal Customers page
@app.route('/loyal_customers')
def loyal_customers_page():
    loyal_customers = retrieve_loyal_customers()
    print("Loyal Customers data:", loyal_customers)  # Add this line
    return template('loyal_customers', loyal_customers=loyal_customers)




# Route for the statistics page
@app.route('/statistics')
def statistics_page():
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)

        # Create a cursor object
        cursor = conn.cursor()

        # Fetch the total sales for each employee
        cursor.execute("""
            SELECT Employees.Name, SUM([Transaction].Qty * Products.Price_Per_Unit) AS TotalSales
            FROM [Transaction]
            JOIN Employees ON [Transaction].Employee_ID = Employees.Employee_ID
            JOIN Products ON [Transaction].Product_ID = Products.Product_ID
            GROUP BY Employees.Name
        """)
        # Fetch all the results
        sales_data = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Create a histogram using Matplotlib
        plt.figure(figsize=(10, 6))
        names = [entry[0] for entry in sales_data]
        total_sales = [entry[1] for entry in sales_data]
        plt.bar(names, total_sales, color='blue')
        plt.xlabel('Employee Name')
        plt.ylabel('Total Sales')
        plt.title('Total Sales by Employee')
        plt.xticks(rotation=45, ha='right')

        # Save the plot to a BytesIO object
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode('utf-8')

        # Generate HTML with the base64 image
        html_content = f'<img src="data:image/png;base64,{img_str}" alt="Total Sales Histogram">'

        return template('base', content=html_content)

    except sqlite3.Error as e:
        print("SQLite error:", e)
        return template('error', message='An error occurred while fetching statistics.')



# Function to fetch data from the database
def fetch_category_counts():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch the count of products in each category
    cursor.execute("""
        SELECT Category_ID, COUNT(*) AS ProductCount
        FROM Products
        GROUP BY Category_ID
    """)

    category_counts = dict(cursor.fetchall())
    conn.close()

    return category_counts

@app.route('/statistics')
def statistics_page():
    # Fetch product list
    product_list = get_product_list()

    # Count the number of products in each category
    category_counts = {}
    for product in product_list:
        category_id = product['Category_ID']
        if isinstance(category_id, int):  # Check if the key is numeric
            if category_id in category_counts:
                category_counts[category_id] += 1
            else:
                category_counts[category_id] = 1

    print("Category Counts:", category_counts)

    # Prepare data for the template
    category_data = json.dumps(category_counts)

    return template('statistics', category_data=category_data)



from bottle import route, static_file

@route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='./static')

# Run the application
if __name__ == '__main__':
    create_table()
    run(app, host='localhost', port=8080)




