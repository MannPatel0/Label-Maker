import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import pandas as pd
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

class LabelMakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Label Maker Pro v2.0")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')

        # Global variables
        self.products = []
        self.label_config = {
            'yellow_background': False,
            'enable_expiry': False,
            'label_width': 2.5,
            'label_height': 1,
            'font_size': 11
        }

        self.create_menu_bar()
        self.create_main_notebook()
        self.create_label_maker_tab()
        self.create_status_bar()

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CSV (Label Maker)", command=self.load_csv)
        file_menu.add_command(label="Export Products (Label Maker)", command=self.export_products)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Label Menu
        label_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Label Settings", menu=label_menu)
        label_menu.add_command(label="Configure Label", command=None)
        label_menu.add_separator()
        label_menu.add_command(label="Future Feature 1", state=tk.DISABLED)
        label_menu.add_command(label="Future Feature 2", state=tk.DISABLED)
        label_menu.add_command(label="Future Feature 3", state=tk.DISABLED)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", state=tk.DISABLED)
        edit_menu.add_command(label="Redo", state=tk.DISABLED)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", state=tk.DISABLED)
        edit_menu.add_command(label="Copy", state=tk.DISABLED)
        edit_menu.add_command(label="Paste", state=tk.DISABLED)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", state=tk.DISABLED)
        view_menu.add_command(label="Zoom Out", state=tk.DISABLED)
        view_menu.add_command(label="Reset Zoom", state=tk.DISABLED)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Options", state=tk.DISABLED)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="Future Help 1", state=tk.DISABLED)
        help_menu.add_command(label="Future Help 2", state=tk.DISABLED)

    def create_main_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.label_maker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.label_maker_frame, text="Label Maker")

    def create_label_maker_tab(self):
        # Main container for label maker
        main_container = ttk.Frame(self.label_maker_frame, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left frame for manual entry
        self.left_frame = ttk.Frame(main_container, padding="10")
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Right frame for CSV upload
        self.right_frame = ttk.Frame(main_container, padding="10")
        self.right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Bottom frame for product list
        self.bottom_frame = ttk.Frame(main_container, padding="10")
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)

        self.create_manual_entry_frame()
        self.create_csv_upload_frame()
        self.create_product_list_frame()

    def create_manual_entry_frame(self):
        manual_entry_frame = ttk.LabelFrame(self.left_frame, text="Manual Product Entry", padding="10")
        manual_entry_frame.pack(fill=tk.BOTH, expand=True)

        # Entry fields
        ttk.Label(manual_entry_frame, text="Product Name:").grid(row=1, column=0, sticky=tk.W)
        self.entry_name = ttk.Entry(manual_entry_frame)
        self.entry_name.grid(row=1, column=1)

        ttk.Label(manual_entry_frame, text="Price:").grid(row=2, column=0, sticky=tk.W)
        self.entry_price = ttk.Entry(manual_entry_frame)
        self.entry_price.grid(row=2, column=1)

        ttk.Label(manual_entry_frame, text="UPC:").grid(row=3, column=0, sticky=tk.W)
        self.entry_upc = ttk.Entry(manual_entry_frame)
        self.entry_upc.grid(row=3, column=1)

        ttk.Label(manual_entry_frame, text="Expiration Date:").grid(row=4, column=0, sticky=tk.W)
        self.entry_expiration_date = ttk.Entry(manual_entry_frame)
        self.entry_expiration_date.grid(row=4, column=1)

        # Checkboxes
        self.color_var_man = tk.BooleanVar(value=self.label_config['yellow_background'])
        self.exp_enable_man = tk.BooleanVar(value=self.label_config['enable_expiry'])

        ttk.Checkbutton(manual_entry_frame, text="Yellow Background", variable=self.color_var_man).grid(row=5, column=0, columnspan=1, pady=10)
        ttk.Checkbutton(manual_entry_frame, text="Enable Expiry Date", variable=self.exp_enable_man).grid(row=5, column=1, columnspan=1, pady=10)

        # Buttons
        ttk.Button(manual_entry_frame, text="Add Product", command=self.add_product).grid(row=6, column=0, columnspan=1, pady=10)
        ttk.Button(manual_entry_frame, text="Create Labels", command=self.create_labels_from_tree).grid(row=6, column=1, columnspan=1, pady=10)

    def create_csv_upload_frame(self):
        csv_upload_frame = ttk.LabelFrame(self.right_frame, text="Load Products from CSV", padding="10")
        csv_upload_frame.pack(fill=tk.BOTH, expand=True)

        # CSV Column Configuration
        ttk.Label(csv_upload_frame, text="Name Column:").grid(row=2, column=0, sticky=tk.W)
        self.column_name_var = tk.StringVar()
        self.column_name_menu = ttk.OptionMenu(csv_upload_frame, self.column_name_var, "")
        self.column_name_menu.grid(row=2, column=1)

        ttk.Label(csv_upload_frame, text="Price Column:").grid(row=3, column=0, sticky=tk.W)
        self.column_price_var = tk.StringVar()
        self.column_price_menu = ttk.OptionMenu(csv_upload_frame, self.column_price_var, "")
        self.column_price_menu.grid(row=3, column=1)

        ttk.Label(csv_upload_frame, text="UPC Column:").grid(row=4, column=0, sticky=tk.W)
        self.column_upc_var = tk.StringVar()
        self.column_upc_menu = ttk.OptionMenu(csv_upload_frame, self.column_upc_var, "")
        self.column_upc_menu.grid(row=4, column=1)

        ttk.Label(csv_upload_frame, text="Expiration Date Column:").grid(row=5, column=0, sticky=tk.W)
        self.column_expiration_date_var = tk.StringVar()
        self.column_expiration_date_menu = ttk.OptionMenu(csv_upload_frame, self.column_expiration_date_var, "")
        self.column_expiration_date_menu.grid(row=5, column=1)

        # Checkboxes
        self.color_var = tk.BooleanVar(value=self.label_config['yellow_background'])
        self.exp_enable = tk.BooleanVar(value=self.label_config['enable_expiry'])

        ttk.Checkbutton(csv_upload_frame, text="Yellow Background", variable=self.color_var).grid(row=6, column=0, columnspan=1, pady=10)
        ttk.Checkbutton(csv_upload_frame, text="Enable Expiry Date", variable=self.exp_enable).grid(row=6, column=1, columnspan=1, pady=10)

        # CSV File Name Display
        self.csv_file_name = tk.StringVar()
        ttk.Label(csv_upload_frame, text="Selected File:").grid(row=7, column=0, sticky=tk.W)
        ttk.Entry(csv_upload_frame, textvariable=self.csv_file_name, state='readonly').grid(row=7, column=1, sticky=(tk.W, tk.E))

        # Buttons
        ttk.Button(csv_upload_frame, text="Load CSV", command=self.load_csv).grid(row=8, column=0, columnspan=1, pady=10)
        ttk.Button(csv_upload_frame, text="Create Labels", command=self.create_labels_from_tree).grid(row=8, column=1, columnspan=1, pady=10)

    def create_product_list_frame(self):
        # Treeview to display products
        self.tree = ttk.Treeview(self.bottom_frame, columns=("Name", "Price", "UPC", "Expiration Date"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("UPC", text="UPC")
        self.tree.heading("Expiration Date", text="Expiration Date")

        # Add right-click menu for CRUD operations
        self.tree.bind("<Button-3>", self.show_tree_context_menu)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def split_text(self, text, max_length):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def create_labels(self, products, output_file, color_enabled, exp_enable):
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter

        label_width = 2.5 * inch
        label_height = 1 * inch

        text_area_width = 1.75 * inch
        price_area_width = 0.75 * inch

        margin_x = 0.1875 * inch
        margin_y = -1 * inch

        labels_per_row = 3
        labels_per_col = 9

        label_spacing_x = 0.2 * inch
        label_spacing_y = 0.2 * inch

        total_products = len(products)
        product_index = 0

        while product_index < total_products:
            for i in range(labels_per_col):
                for j in range(labels_per_row):
                    if product_index >= total_products:
                        break

                    product = products[product_index]

                    product_name = str(product.get('name', 'Unknown Product'))

                    x = margin_x + j * (label_width + label_spacing_x)
                    y = height - margin_y - (i + 1) * (label_height + label_spacing_y)

                    c.setLineWidth(0.5)
                    c.setStrokeColor(colors.black)
                    c.rect(x, y - label_height, label_width, label_height)

                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 11)

                    first_line_limit = 25
                    product_name_lines = self.split_text(product_name, first_line_limit)

                    for line_index, line in enumerate(product_name_lines):
                        c.drawString(x + 5, y - 15 - (line_index * 10), line)

                    if exp_enable:
                        c.setFont("Helvetica", 6)
                        expiration_date = str(product.get('expiration_date', 'N/A'))
                        c.drawString(x + 5, y - 35, f"EXP: {expiration_date}")

                    barcode_x_position = x - margin_x
                    barcode_y_position = y - label_height + 5
                    barcode_value = str(product.get('upc', '000000000000'))
                    barcode = code128.Code128(barcode_value, barHeight=label_height / 3, barWidth=.75)
                    barcode.drawOn(c, barcode_x_position, barcode_y_position)

                    price_x_position = x + text_area_width
                    price_y_position = y - 65

                    if color_enabled:
                        c.setFillColor(colors.yellow)
                        c.rect(price_x_position, price_y_position, price_area_width, 20, fill=True)

                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 18)
                    price_value = f"${str(product.get('price', '0.00'))}"
                    c.drawString(price_x_position + 3, price_y_position + 5, price_value)

                    product_index += 1

                if product_index >= total_products:
                    break

            if product_index < total_products:
                c.showPage()

        c.save()

    def add_product(self):
        name = self.entry_name.get()
        price = self.entry_price.get()
        upc = self.entry_upc.get()
        expiration_date = self.entry_expiration_date.get()

        if not (name and price and upc):
            messagebox.showwarning("Input Error", "Name, Price, and UPC are required.")
            return

        self.products.append({
            'name': name,
            'price': price,
            'upc': str(upc),
            'expiration_date': expiration_date
        })

        self.tree.insert("", "end", values=(name, price, upc, expiration_date))

        # Clear entry fields
        self.entry_name.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_upc.delete(0, tk.END)
        self.entry_expiration_date.delete(0, tk.END)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = pd.read_csv(file_path)
            columns = df.columns.tolist()

            # Clear existing menu items
            self.column_name_menu['menu'].delete(0, 'end')
            self.column_price_menu['menu'].delete(0, 'end')
            self.column_upc_menu['menu'].delete(0, 'end')
            self.column_expiration_date_menu['menu'].delete(0, 'end')

            # Populate dropdown menus with CSV columns
            for col in columns:
                self.column_name_menu['menu'].add_command(
                    label=col,
                    command=tk._setit(self.column_name_var, col)
                )
                self.column_price_menu['menu'].add_command(
                    label=col,
                    command=tk._setit(self.column_price_var, col)
                )
                self.column_upc_menu['menu'].add_command(
                    label=col,
                    command=tk._setit(self.column_upc_var, col)
                )
                self.column_expiration_date_menu['menu'].add_command(
                    label=col,
                    command=tk._setit(self.column_expiration_date_var, col)
                )

            self.csv_data = df

            # Clear previous data in product list
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.products.clear()

            # Load data into Treeview
            for _, row in df.iterrows():
                self.tree.insert("", "end", values=(row[self.column_name_var.get()], row[self.column_price_var.get()], row[self.column_upc_var.get()], row[self.column_expiration_date_var.get()]))

            # Set the file name in the entry
            self.csv_file_name.set(os.path.basename(file_path))

            # Update status
            self.status_var.set(f"CSV Loaded: {os.path.basename(file_path)}")

    def create_labels_from_tree(self):
        products = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            product = {
                'name': values[0],
                'price': values[1],
                'upc': values[2],
                'expiration_date': values[3]
            }
            products.append(product)

        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if output_file:
            self.create_labels(
                products,
                output_file,
                self.color_var.get(),
                self.exp_enable.get()
            )
            messagebox.showinfo("Success", f"PDF saved as {output_file}")
            self.status_var.set(f"Labels created: {os.path.basename(output_file)}")

    def export_products(self):
        if not self.tree.get_children():
            messagebox.showwarning("Export Error", "No products to export.")
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if output_file:
            products = []
            for item in self.tree.get_children():
                values = self.tree.item(item, "values")
                product = {
                    'name': values[0],
                    'price': values[1],
                    'upc': values[2],
                    'expiration_date': values[3]
                }
                products.append(product)

            export_df = pd.DataFrame(products)
            export_df.to_csv(output_file, index=False)
            messagebox.showinfo("Success", f"Products exported to {output_file}")
            self.status_var.set(f"Products exported: {os.path.basename(output_file)}")

    def show_tree_context_menu(self, event):
            # Show context menu for CRUD operations
            selected_item = self.tree.selection()
            menu = tk.Menu(self.root, tearoff=0)
            if selected_item:
                menu.add_command(label="Edit Product", command=self.edit_selected_product)
                menu.add_command(label="Remove Product", command=self.remove_selected_product)
            menu.add_command(label="Add Product", command=self.add_product_dialog)
            menu.post(event.x_root, event.y_root)

    def add_product_dialog(self):
        self.product_dialog("Add Product", self.add_product)

    def edit_selected_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.product_dialog("Edit Product", lambda: self.update_product(selected_item), values)

    def product_dialog(self, title, save_command, values=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x200")

        ttk.Label(dialog, text="Product Name:").grid(row=0, column=0, sticky=tk.W)
        entry_name = ttk.Entry(dialog)
        entry_name.grid(row=0, column=1)
        if values:
            entry_name.insert(0, values[0])

        ttk.Label(dialog, text="Price:").grid(row=1, column=0, sticky=tk.W)
        entry_price = ttk.Entry(dialog)
        entry_price.grid(row=1, column=1)
        if values:
            entry_price.insert(0, values[1])

        ttk.Label(dialog, text="UPC:").grid(row=2, column=0, sticky=tk.W)
        entry_upc = ttk.Entry(dialog)
        entry_upc.grid(row=2, column=1)
        if values:
            entry_upc.insert(0, values[2])

        ttk.Label(dialog, text="Expiration Date:").grid(row=3, column=0, sticky=tk.W)
        entry_expiration_date = ttk.Entry(dialog)
        entry_expiration_date.grid(row=3, column=1)
        if values:
            entry_expiration_date.insert(0, values[3])

        def save():
            save_command(entry_name.get(), entry_price.get(), entry_upc.get(), entry_expiration_date.get())
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def add_product(self, name, price, upc, expiration_date):
        if not (name and price and upc):
            messagebox.showwarning("Input Error", "Name, Price, and UPC are required.")
            return

        self.tree.insert("", "end", values=(name, price, upc, expiration_date))

    def update_product(self, item, name, price, upc, expiration_date):
        if not (name and price and upc):
            messagebox.showwarning("Input Error", "Name, Price, and UPC are required.")
            return

        self.tree.item(item, values=(name, price, upc, expiration_date))

    def remove_selected_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = pd.read_csv(file_path)
            self.csv_data = df

            # Clear previous data in product list
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Populate treeview with CSV data
            for _, row in df.iterrows():
                self.tree.insert("", "end", values=(row['name'], row['price'], row['upc'], row['expiration_date']))

            # Set the file name in the entry
            self.csv_file_name.set(os.path.basename(file_path))

            # Update status
            self.status_var.set(f"CSV Loaded: {os.path.basename(file_path)}")

    def create_labels_from_tree(self):
        products = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            product = {
                'name': values[0],
                'price': values[1],
                'upc': values[2],
                'expiration_date': values[3]
            }
            products.append(product)

        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if output_file:
            self.create_labels(
                products,
                output_file,
                self.color_var.get(),
                self.exp_enable.get()
            )
            messagebox.showinfo("Success", f"PDF saved as {output_file}")
            self.status_var.set(f"Labels created: {os.path.basename(output_file)}")
        
    
            self.label_config['label_width'] = width_var.get()
            self.label_config['label_height'] = height_var.get()
            self.label_config['font_size'] = font_var.get()
            config_window.destroy()
            self.status_var.set("Label configuration updated")

        def reset_defaults():
            width_var.set(2.5)
            height_var.set(1)
            font_var.set(11)

        ttk.Button(config_window, text="Save", command=save_config).pack(pady=20)

    def show_about(self):
        messagebox.showinfo(
            "About Label Maker Pro",
            "Label Maker Pro v2.0\n\n"
            "A comprehensive tool for creating product labels.\n"
            "© 2024 Hyperion Labs, Inc."
        )

def main():
    root = tk.Tk()
    app = LabelMakerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()