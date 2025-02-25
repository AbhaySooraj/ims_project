from flask import Flask, render_template, request, redirect, flash
import csv
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

CSV_FILE = "inventory.csv"

# Ensure the CSV file exists
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Product ID", "Product Name", "Category", "Price", "Stock", "Total Sales"])

initialize_csv()

# Load inventory data
def load_inventory():
    with open(CSV_FILE, "r") as file:
        return list(csv.DictReader(file))

# Save inventory data
def save_inventory(inventory):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Product ID", "Product Name", "Category", "Price", "Stock", "Total Sales"])
        writer.writeheader()
        writer.writerows(inventory)

# Home Page - Displays Inventory
@app.route("/")
def index():
    inventory = load_inventory()
    return render_template("index.html", inventory=inventory)

# Add Product
@app.route("/add", methods=["POST"])
def add_product():
    inventory = load_inventory()
    product_id = request.form["product_id"]
    
    # Check if product exists
    if any(item["Product ID"] == product_id for item in inventory):
        flash("Error: Product ID already exists!", "danger")
        return redirect("/")
    
    new_product = {
        "Product ID": product_id,
        "Product Name": request.form["product_name"],
        "Category": request.form["category"],
        "Price": request.form["price"],
        "Stock": request.form["stock"],
        "Total Sales": "0"
    }
    
    inventory.append(new_product)
    save_inventory(inventory)
    flash("Product added successfully!", "success")
    return redirect("/")

# Update Stock or Price
@app.route("/update", methods=["POST"])
def update_product():
    inventory = load_inventory()
    product_id = request.form["product_id"]
    
    for item in inventory:
        if item["Product ID"] == product_id:
            field = request.form["field"]
            new_value = request.form["new_value"]
            
            if field == "Price":
                item[field] = float(new_value)
            elif field == "Stock":
                item[field] = int(new_value)
            else:
                flash("Invalid field selection!", "danger")
                return redirect("/")
            
            save_inventory(inventory)
            flash("Product updated successfully!", "success")
            return redirect("/")
    
    flash("Error: Product ID not found!", "danger")
    return redirect("/")

# Record a Sale
@app.route("/sell", methods=["POST"])
def record_sale():
    inventory = load_inventory()
    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])
    
    for item in inventory:
        if item["Product ID"] == product_id:
            stock = int(item["Stock"])
            if stock >= quantity:
                item["Stock"] = stock - quantity
                item["Total Sales"] = int(item["Total Sales"]) + quantity
                save_inventory(inventory)
                flash("Sale recorded successfully!", "success")
                return redirect("/")
            else:
                flash("Error: Insufficient stock!", "danger")
                return redirect("/")
    
    flash("Error: Product ID not found!", "danger")
    return redirect("/")

# Recommend Restock
@app.route("/recommend")
def recommend_restock():
    threshold = 5  # You can change this threshold
    inventory = load_inventory()
    recommendations = [item for item in inventory if int(item["Stock"]) < threshold]
    return render_template("recommend.html", recommendations=recommendations)

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
