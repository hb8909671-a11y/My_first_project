import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# ================= DATABASE =================

conn = sqlite3.connect("billing_database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_no TEXT,
    customer_name TEXT,
    phone TEXT,
    date TEXT,
    subtotal REAL,
    gst REAL,
    discount REAL,
    total REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_no TEXT,
    product TEXT,
    quantity INTEGER,
    price REAL,
    amount REAL
)
""")

conn.commit()


# ================= MAIN WINDOW =================

root = tk.Tk()
root.title("Professional Billing System")
root.geometry("1100x700")
root.minsize(950, 600)


# ================= VARIABLES =================

customer_name = tk.StringVar()
phone = tk.StringVar()

product_name = tk.StringVar()
quantity = tk.IntVar(value=1)
price = tk.DoubleVar(value=0)

subtotal_var = tk.DoubleVar(value=0)
gst_var = tk.DoubleVar(value=0)
discount_var = tk.DoubleVar(value=0)
total_var = tk.DoubleVar(value=0)


# ================= FUNCTIONS =================

def add_item():

    product = product_name.get().strip()

    if product == "":
        messagebox.showwarning("Warning", "Please enter product name")
        return

    try:
        qty = int(quantity.get())
        item_price = float(price.get())
    except:
        messagebox.showerror("Error", "Enter valid quantity and price")
        return

    if qty <= 0 or item_price < 0:
        messagebox.showerror("Error", "Invalid quantity or price")
        return

    amount = qty * item_price

    table.insert(
        "",
        "end",
        values=(product, qty, f"{item_price:.2f}", f"{amount:.2f}")
    )

    calculate_total()

    product_name.set("")
    quantity.set(1)
    price.set(0)


def delete_item():

    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Please select an item to delete"
        )
        return

    for item in selected:
        table.delete(item)

    calculate_total()


def calculate_total():

    subtotal = 0

    for item in table.get_children():

        values = table.item(item)["values"]

        amount = float(values[3])

        subtotal += amount

    gst = subtotal * 0.05

    discount = subtotal * (discount_var.get() / 100)

    total = subtotal + gst - discount

    subtotal_var.set(round(subtotal, 2))
    gst_var.set(round(gst, 2))
    total_var.set(round(total, 2))


def clear_all():

    customer_name.set("")
    phone.set("")
    product_name.set("")
    quantity.set(1)
    price.set(0)
    discount_var.set(0)

    for item in table.get_children():
        table.delete(item)

    subtotal_var.set(0)
    gst_var.set(0)
    total_var.set(0)


def generate_bill():

    if customer_name.get().strip() == "":
        messagebox.showwarning(
            "Warning",
            "Please enter customer name"
        )
        return

    if not table.get_children():
        messagebox.showwarning(
            "Warning",
            "Please add at least one product"
        )
        return

    bill_no = "BILL" + datetime.now().strftime("%Y%m%d%H%M%S")

    date = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    subtotal = subtotal_var.get()
    gst = gst_var.get()
    discount = discount_var.get()
    total = total_var.get()

    # Save bill
    cursor.execute("""
    INSERT INTO bills
    (bill_no, customer_name, phone, date,
     subtotal, gst, discount, total)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bill_no,
        customer_name.get(),
        phone.get(),
        date,
        subtotal,
        gst,
        discount,
        total
    ))

    # Save products
    for item in table.get_children():

        values = table.item(item)["values"]

        product = values[0]
        qty = int(values[1])
        item_price = float(values[2])
        amount = float(values[3])

        cursor.execute("""
        INSERT INTO bill_items
        (bill_no, product, quantity, price, amount)
        VALUES (?, ?, ?, ?, ?)
        """, (
            bill_no,
            product,
            qty,
            item_price,
            amount
        ))

    conn.commit()

    show_bill(
        bill_no,
        date,
        subtotal,
        gst,
        discount,
        total
    )


def show_bill(bill_no, date, subtotal, gst, discount, total):

    bill_window = tk.Toplevel(root)

    bill_window.title("Generated Bill")
    bill_window.geometry("600x700")

    bill_text = tk.Text(
        bill_window,
        font=("Courier New", 11)
    )

    bill_text.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    bill_text.insert("end", "\n")
    bill_text.insert(
        "end",
        "             MY COLLEGE STORE\n"
    )
    bill_text.insert(
        "end",
        "          PROFESSIONAL BILLING\n"
    )
    bill_text.insert(
        "end",
        "------------------------------------------\n"
    )

    bill_text.insert("end", f"Bill No : {bill_no}\n")
    bill_text.insert("end", f"Customer: {customer_name.get()}\n")
    bill_text.insert("end", f"Phone   : {phone.get()}\n")
    bill_text.insert("end", f"Date    : {date}\n")

    bill_text.insert(
        "end",
        "------------------------------------------\n"
    )

    bill_text.insert(
        "end",
        "Product             Qty     Price     Amount\n"
    )

    bill_text.insert(
        "end",
        "------------------------------------------\n"
    )

    for item in table.get_children():

        values = table.item(item)["values"]

        product = str(values[0])[:18]
        qty = values[1]
        item_price = values[2]
        amount = values[3]

        bill_text.insert(
            "end",
            f"{product:<18} {qty:<5} "
            f"{item_price:<9} {amount}\n"
        )

    bill_text.insert(
        "end",
        "------------------------------------------\n"
    )

    bill_text.insert(
        "end",
        f"Subtotal                ₹ {subtotal:.2f}\n"
    )

    bill_text.insert(
        "end",
        f"GST (5%)                ₹ {gst:.2f}\n"
    )

    bill_text.insert(
        "end",
        f"Discount                ₹ {discount:.2f}\n"
    )

    bill_text.insert(
        "end",
        "------------------------------------------\n"
    )

    bill_text.insert(
        "end",
        f"GRAND TOTAL             ₹ {total:.2f}\n"
    )

    bill_text.insert(
        "end",
        "------------------------------------------\n"
    )

    bill_text.insert(
        "end",
        "\n             Thank You!\n"
    )

    bill_text.config(state="disabled")


# ================= HEADER =================

header = tk.Frame(
    root,
    bg="#1f2937",
    height=70
)

header.pack(
    fill="x"
)

title = tk.Label(
    header,
    text="SHOP BILLING SYSTEM",
    font=("Arial", 24, "bold"),
    bg="#1f2937",
    fg="white"
)

title.pack(pady=18)


# ================= CUSTOMER FRAME =================

customer_frame = ttk.LabelFrame(
    root,
    text="Customer Information",
    padding=15
)

customer_frame.pack(
    fill="x",
    padx=15,
    pady=10
)


ttk.Label(
    customer_frame,
    text="Customer Name:"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=5
)

ttk.Entry(
    customer_frame,
    textvariable=customer_name,
    width=30
).grid(
    row=0,
    column=1,
    padx=10
)


ttk.Label(
    customer_frame,
    text="Phone:"
).grid(
    row=0,
    column=2,
    padx=10
)

ttk.Entry(
    customer_frame,
    textvariable=phone,
    width=20
).grid(
    row=0,
    column=3,
    padx=10
)


# ================= PRODUCT FRAME =================

product_frame = ttk.LabelFrame(
    root,
    text="Add Product",
    padding=15
)

product_frame.pack(
    fill="x",
    padx=15,
    pady=5
)


ttk.Label(
    product_frame,
    text="Product Name:"
).grid(
    row=0,
    column=0,
    padx=10
)

ttk.Entry(
    product_frame,
    textvariable=product_name,
    width=25
).grid(
    row=0,
    column=1,
    padx=10
)


ttk.Label(
    product_frame,
    text="Quantity:"
).grid(
    row=0,
    column=2,
    padx=10
)

ttk.Entry(
    product_frame,
    textvariable=quantity,
    width=10
).grid(
    row=0,
    column=3,
    padx=10
)


ttk.Label(
    product_frame,
    text="Price:"
).grid(
    row=0,
    column=4,
    padx=10
)

ttk.Entry(
    product_frame,
    textvariable=price,
    width=12
).grid(
    row=0,
    column=5,
    padx=10
)


ttk.Button(
    product_frame,
    text="Add Product",
    command=add_item
).grid(
    row=0,
    column=6,
    padx=15
)


# ================= TABLE =================

table_frame = ttk.Frame(root)

table_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=10
)


columns = (
    "Product",
    "Quantity",
    "Price",
    "Amount"
)

table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)

table.heading(
    "Product",
    text="Product"
)

table.heading(
    "Quantity",
    text="Quantity"
)

table.heading(
    "Price",
    text="Price"
)

table.heading(
    "Amount",
    text="Amount"
)


table.column(
    "Product",
    width=300
)

table.column(
    "Quantity",
    width=100,
    anchor="center"
)

table.column(
    "Price",
    width=150,
    anchor="center"
)

table.column(
    "Amount",
    width=150,
    anchor="center"
)


table.pack(
    fill="both",
    expand=True
)


# ================= DELETE BUTTON =================

ttk.Button(
    root,
    text="Delete Selected Product",
    command=delete_item
).pack(
    pady=5
)


# ================= TOTAL FRAME =================

total_frame = ttk.LabelFrame(
    root,
    text="Bill Summary",
    padding=10
)

total_frame.pack(
    fill="x",
    padx=15,
    pady=5
)


ttk.Label(
    total_frame,
    text="Subtotal:"
).grid(
    row=0,
    column=0,
    padx=15
)

ttk.Label(
    total_frame,
    textvariable=subtotal_var
).grid(
    row=0,
    column=1
)


ttk.Label(
    total_frame,
    text="GST 5%:"
).grid(
    row=0,
    column=2,
    padx=15
)

ttk.Label(
    total_frame,
    textvariable=gst_var
).grid(
    row=0,
    column=3
)


ttk.Label(
    total_frame,
    text="Discount %:"
).grid(
    row=0,
    column=4,
    padx=15
)

ttk.Entry(
    total_frame,
    textvariable=discount_var,
    width=8
).grid(
    row=0,
    column=5
)


ttk.Button(
    total_frame,
    text="Calculate",
    command=calculate_total
).grid(
    row=0,
    column=6,
    padx=15
)


ttk.Label(
    total_frame,
    text="Grand Total:"
).grid(
    row=0,
    column=7,
    padx=15
)

ttk.Label(
    total_frame,
    textvariable=total_var,
    font=("Arial", 13, "bold")
).grid(
    row=0,
    column=8
)


# ================= BOTTOM BUTTONS =================

button_frame = ttk.Frame(root)

button_frame.pack(
    pady=10
)


ttk.Button(
    button_frame,
    text="Generate Bill",
    command=generate_bill
).grid(
    row=0,
    column=0,
    padx=10
)


ttk.Button(
    button_frame,
    text="Clear",
    command=clear_all
).grid(
    row=0,
    column=1,
    padx=10
)


ttk.Button(
    button_frame,
    text="Exit",
    command=root.destroy
).grid(
    row=0,
    column=2,
    padx=10
)


# ================= RUN =================

root.mainloop()

conn.close()