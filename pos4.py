import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class POS:
    def __init__(self, root):
        self.root = root
        self.root.title("POS System")
        self.create_login_screen()

    def create_login_screen(self):
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(padx=10, pady=10)

        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.check_login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=5)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "adminpass":
            self.user_role = "admin"
            self.login_frame.destroy()
            self.create_gui()
        elif username == "user" and password == "userpass":
            self.user_role = "user"
            self.login_frame.destroy()
            self.create_gui()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def create_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True)

        self.sales_tab = ttk.Frame(notebook)
        notebook.add(self.sales_tab, text='Sales')
        self.create_sales_tab()

        if self.user_role == "admin":
            self.inventory_tab = ttk.Frame(notebook)
            self.accounting_tab = ttk.Frame(notebook)

            notebook.add(self.inventory_tab, text='Inventory')
            notebook.add(self.accounting_tab, text='Accounting')

            self.create_inventory_tab()
            self.create_accounting_tab()

    def create_sales_tab(self):
        ttk.Label(self.sales_tab, text="Select Item:").grid(row=0, column=0, padx=10, pady=10)
        self.item_combobox = ttk.Combobox(self.sales_tab)
        self.item_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.update_combobox()

        ttk.Label(self.sales_tab, text="Quantity:").grid(row=1, column=0, padx=10, pady=10)
        self.quantity_entry = ttk.Entry(self.sales_tab)
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        self.add_to_cart_button = ttk.Button(self.sales_tab, text="Add to Cart", command=self.add_to_cart)
        self.add_to_cart_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.cart_listbox = tk.Listbox(self.sales_tab, width=50)
        self.cart_listbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(self.sales_tab, text="Total:").grid(row=4, column=0, padx=10, pady=10)
        self.total_label = ttk.Label(self.sales_tab, text="0.00")
        self.total_label.grid(row=4, column=1, padx=10, pady=10)

        self.checkout_button = ttk.Button(self.sales_tab, text="Checkout", command=self.checkout)
        self.checkout_button.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Label(self.sales_tab, text="Cash Tender:").grid(row=0, column=2, padx=10, pady=10)
        self.cash_tender_entry = ttk.Entry(self.sales_tab)
        self.cash_tender_entry.grid(row=0, column=3, padx=10, pady=10)
        
        self.dial_pad_frame = ttk.Frame(self.sales_tab)
        self.dial_pad_frame.grid(row=1, column=2, columnspan=2, rowspan=4, pady=10)
        self.create_dial_pad()

        ttk.Label(self.sales_tab, text="Change:").grid(row=5, column=2, padx=10, pady=10)
        self.change_label = ttk.Label(self.sales_tab, text="0.00")
        self.change_label.grid(row=5, column=3, padx=10, pady=10)

        self.print_receipt_button = ttk.Button(self.sales_tab, text="Print Receipt", command=self.print_receipt)
        self.print_receipt_button.grid(row=6, column=0, columnspan=4, pady=10)

    def create_dial_pad(self):
        buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '0', '.', 'C'
        ]
        row_val = 0
        col_val = 0
        for button in buttons:
            action = lambda x=button: self.dial_pad_click(x)
            ttk.Button(self.dial_pad_frame, text=button, command=action, width=5).grid(row=row_val, column=col_val)
            col_val += 1
            if col_val > 2:
                col_val = 0
                row_val += 1

    def dial_pad_click(self, value):
        current_value = self.cash_tender_entry.get()
        if value == 'C':
            self.cash_tender_entry.delete(0, tk.END)
        else:
            self.cash_tender_entry.insert(tk.END, value)

    def update_combobox(self):
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Inventory")
        items = cursor.fetchall()
        conn.close()
        
        item_list = [f"{item[0]} - {item[1]}" for item in items]
        self.item_combobox['values'] = item_list

    def add_to_cart(self):
        item_info = self.item_combobox.get()
        quantity = self.quantity_entry.get()

        if not item_info or not quantity.isdigit():
            messagebox.showerror("Error", "Please select an item and enter a valid quantity.")
            return

        self.cart_listbox.insert(tk.END, f"{item_info} x {quantity}")
        self.quantity_entry.delete(0, tk.END)
        self.update_total()

    def update_total(self):
        total = 0.0
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cart_items = self.cart_listbox.get(0, tk.END)
        for item in cart_items:
            item_id, _ = item.split(' - ')[0], ' - '.join(item.split(' - ')[1:]).split(' x ')[0]
            quantity = int(item.split(' x ')[1])
            cursor.execute("SELECT price FROM Inventory WHERE id=?", (item_id,))
            price = cursor.fetchone()[0]
            total += price * quantity
        conn.close()
        self.total_label.config(text=f"{total:.2f}")

    def checkout(self):
        cart_items = self.cart_listbox.get(0, tk.END)
        if not cart_items:
            messagebox.showerror("Error", "Cart is empty.")
            return
        
        total = float(self.total_label.cget("text"))
        cash_tender = self.cash_tender_entry.get()
        if not cash_tender.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Please enter a valid cash tender.")
            return
        cash_tender = float(cash_tender)
        
        if cash_tender < total:
            messagebox.showerror("Error", "Insufficient cash tendered.")
            return
        
        change = cash_tender - total
        self.change_label.config(text=f"{change:.2f}")

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        for item in cart_items:
            item_id, item_name = item.split(' - ')[0], ' - '.join(item.split(' - ')[1:]).split(' x ')[0]
            quantity = int(item.split(' x ')[1])
            
            cursor.execute("SELECT quantity, price FROM Inventory WHERE id=?", (item_id,))
            result = cursor.fetchone()
            if not result:
                continue
            
            stock_quantity, price = result
            if stock_quantity < quantity:
                messagebox.showerror("Error", f"Insufficient stock for {item_name}.")
                continue

            new_quantity = stock_quantity - quantity
            cursor.execute("UPDATE Inventory SET quantity=? WHERE id=?", (new_quantity, item_id))
            total_price = price * quantity
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO Transactions (item_id, quantity, total_price, date) VALUES (?, ?, ?, ?)",
                           (item_id, quantity, total_price, date))

        conn.commit()
        conn.close()
        self.cart_listbox.delete(0, tk.END)
        self.update_combobox()
        self.update_total()
        self.update_transactions_tree()
        messagebox.showinfo("Success", "Checkout completed.")

    def print_receipt(self):
        receipt_text = ""
        cart_items = self.cart_listbox.get(0, tk.END)
        if not cart_items:
            messagebox.showerror("Error", "Cart is empty.")
            return
        
        total = self.total_label.cget("text")
        cash_tender = self.cash_tender_entry.get()
        change = self.change_label.cget("text")

        receipt_text += "Receipt\n"
        receipt_text += "--------------------------\n"
        for item in cart_items:
            receipt_text += f"{item}\n"
        receipt_text += "--------------------------\n"
        receipt_text += f"Total: {total}\n"
        receipt_text += f"Cash Tender: {cash_tender}\n"
        receipt_text += f"Change: {change}\n"
        
        with open("receipt.txt", "w") as file:
            file.write(receipt_text)
        
        messagebox.showinfo("Receipt", "Receipt printed to receipt.txt")

    def create_inventory_tab(self):
        ttk.Label(self.inventory_tab, text="Item Name:").grid(row=0, column=0, padx=10, pady=10)
        self.item_name_entry = ttk.Entry(self.inventory_tab)
        self.item_name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.inventory_tab, text="Quantity:").grid(row=1, column=0, padx=10, pady=10)
        self.item_quantity_entry = ttk.Entry(self.inventory_tab)
        self.item_quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.inventory_tab, text="Price:").grid(row=2, column=0, padx=10, pady=10)
        self.item_price_entry = ttk.Entry(self.inventory_tab)
        self.item_price_entry.grid(row=2, column=1, padx=10, pady=10)

        self.add_item_button = ttk.Button(self.inventory_tab, text="Add Item", command=self.add_item)
        self.add_item_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.update_inventory_button = ttk.Button(self.inventory_tab, text="Update Item", command=self.update_item)
        self.update_inventory_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.delete_item_button = ttk.Button(self.inventory_tab, text="Delete Item", command=self.delete_item)
        self.delete_item_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.inventory_tree = ttk.Treeview(self.inventory_tab, columns=("ID", "Name", "Quantity", "Price"), show='headings')
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        self.update_inventory_tree()

    def add_item(self):
        name = self.item_name_entry.get()
        quantity = self.item_quantity_entry.get()
        price = self.item_price_entry.get()

        if not name or not quantity.isdigit() or not price.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Please enter valid item details.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Inventory (name, quantity, price) VALUES (?, ?, ?)",
                       (name, int(quantity), float(price)))
        conn.commit()
        conn.close()

        self.item_name_entry.delete(0, tk.END)
        self.item_quantity_entry.delete(0, tk.END)
        self.item_price_entry.delete(0, tk.END)
        self.update_inventory_tree()
        self.update_combobox()
        messagebox.showinfo("Success", "Item added.")

    def update_item(self):
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to update.")
            return

        item_id = self.inventory_tree.item(selected_item, 'values')[0]
        name = self.item_name_entry.get()
        quantity = self.item_quantity_entry.get()
        price = self.item_price_entry.get()

        if not name or not quantity.isdigit() or not price.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Please enter valid item details.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Inventory SET name=?, quantity=?, price=? WHERE id=?",
                       (name, int(quantity), float(price), item_id))
        conn.commit()
        conn.close()

        self.item_name_entry.delete(0, tk.END)
        self.item_quantity_entry.delete(0, tk.END)
        self.item_price_entry.delete(0, tk.END)
        self.update_inventory_tree()
        self.update_combobox()
        messagebox.showinfo("Success", "Item updated.")

    def delete_item(self):
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to delete.")
            return

        item_id = self.inventory_tree.item(selected_item, 'values')[0]
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Inventory WHERE id=?", (item_id,))
        conn.commit()
        conn.close()

        self.update_inventory_tree()
        self.update_combobox()
        messagebox.showinfo("Success", "Item deleted.")

    def update_inventory_tree(self):
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Inventory")
        items = cursor.fetchall()
        conn.close()

        for item in items:
            self.inventory_tree.insert('', tk.END, values=item)

    def create_accounting_tab(self):
        self.transactions_tree = ttk.Treeview(self.accounting_tab, columns=("ID", "Item ID", "Quantity", "Total Price", "Date"), show='headings')
        self.transactions_tree.heading("ID", text="ID")
        self.transactions_tree.heading("Item ID", text="Item ID")
        self.transactions_tree.heading("Quantity", text="Quantity")
        self.transactions_tree.heading("Total Price", text="Total Price")
        self.transactions_tree.heading("Date", text="Date")
        self.transactions_tree.grid(row=0, column=0, padx=10, pady=10)
        self.update_transactions_tree()

    def update_transactions_tree(self):
        for row in self.transactions_tree.get_children():
            self.transactions_tree.delete(row)

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Transactions")
        transactions = cursor.fetchall()
        conn.close()

        for transaction in transactions:
            self.transactions_tree.insert('', tk.END, values=transaction)


if __name__ == "__main__":
    root = tk.Tk()
    pos_system = POS(root)
    root.mainloop()