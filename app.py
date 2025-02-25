from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

CSV_FILE = 'inventory.csv'

def initialize_csv():
    """Creates a CSV file if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Product ID', 'Product Name', 'Category', 'Price', 'Stock', 'Total Sales'])

def load_inventory():
    with open(CSV_FILE, 'r') as file:
        return list(csv.DictReader(file))

def save_inventory(inventory):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Product ID', 'Product Name', 'Category', 'Price', 'Stock', 'Total Sales'])
        writer.writeheader()
        writer.writerows(inventory)

@app.route('/')
def home():
    inventory = load_inventory()
    return render_template('index.html', inventory=inventory)

@app.route('/add', methods=['POST'])
def add_product():
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    category = request.form['category']
    price = request.form['price']
    stock = request.form['stock']

    inventory = load_inventory()
    if any(item['Product ID'] == product_id for item in inventory):
        flash("Error: Product ID already exists.", "danger")
        return redirect(url_for('home'))

    inventory.append({
        'Product ID': product_id,
        'Product Name': product_name,
        'Category': category,
        'Price': price,
        'Stock': stock,
        'Total Sales': 0
    })

    save_inventory(inventory)
    flash("Product added successfully!", "success")
    return redirect(url_for('home'))

@app.route('/update', methods=['POST'])
def update_product():
    product_id = request.form['product_id']
    field = request.form['field']
    new_value = request.form['new_value']

    inventory = load_inventory()
    product = next((item for item in inventory if item['Product ID'] == product_id), None)

    if not product:
        flash("Error: Product ID not found.", "danger")
        return redirect(url_for('home'))

    product[field] = float(new_value) if field == 'Price' else int(new_value)
    save_inventory(inventory)
    flash("Product updated successfully!", "success")
    return redirect(url_for('home'))

@app.route('/sale', methods=['POST'])
def record_sale():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])

    inventory = load_inventory()
    product = next((item for item in inventory if item['Product ID'] == product_id), None)

    if not product:
        flash("Error: Product ID not found.", "danger")
        return redirect(url_for('home'))

    stock = int(product['Stock'])
    if stock >= quantity:
        product['Stock'] = stock - quantity
        product['Total Sales'] = int(product['Total Sales']) + quantity
        save_inventory(inventory)
        flash("Sale recorded successfully!", "success")
    else:
        flash("Error: Insufficient stock.", "danger")

    return redirect(url_for('home'))

@app.route('/recommend', methods=['POST'])
def recommend_restock():
    threshold = int(request.form['threshold'])
    inventory = load_inventory()
    recommendations = [item for item in inventory if int(item['Stock']) < threshold]
    return render_template('recommend.html', recommendations=recommendations)

if __name__ == "__main__":
    initialize_csv()
    app.run(debug=True)
