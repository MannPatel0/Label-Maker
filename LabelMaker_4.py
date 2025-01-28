import os
import dearpygui.dearpygui as dpg
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Dict
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors


# Model code remains the same as before
@dataclass
class Product:
    name: str
    price: float
    upc: str
    expiration_date: Optional[str] = None
    source: str = "manual"

    @classmethod
    def from_dict(cls, data: dict, source: str = "manual") -> 'Product':
        return cls(
            name=str(data['name']),
            price=float(data['price']),
            upc=str(data['upc']),
            expiration_date=str(data.get('expiration_date', '')),
            source=source
        )

class ProductModel:
    def __init__(self):
        self.manual_products: List[Product] = []
        self.csv_products: List[Product] = []

    def add_product(self, product: Product) -> None:
        if product.source == "csv":
            self.csv_products.append(product)
        else:
            self.manual_products.append(product)

    def get_all_products(self) -> List[Product]:
        return self.manual_products + self.csv_products

class LabelMakerApp:
    def __init__(self):
        self.model = ProductModel()
        self.setup_dpg()
        self.create_windows()
        self.csv_mappings = {}
        self.csv_file_path = None

    def setup_dpg(self):
        dpg.create_context()
        dpg.create_viewport(title="Label Maker Pro v4.5", width=1115, height=585)
        dpg.setup_dearpygui()

        # Create theme for disabled items
        with dpg.theme() as self.disabled_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [128, 128, 128])
                dpg.add_theme_color(dpg.mvThemeCol_Button, [64, 64, 64])

    def create_menu(self):
        with dpg.viewport_menu_bar():
            with dpg.menu(label="Windows"):
                dpg.add_menu_item(label="Show Manual Entry", callback=lambda: dpg.show_item("manual_window"))
                dpg.add_menu_item(label="Show CSV Import", callback=lambda: dpg.show_item("csv_window"))
                dpg.add_menu_item(label="Show Product List", callback=lambda: dpg.show_item("list_window"))

            with dpg.menu(label="Actions"):
                dpg.add_menu_item(label="Create Labels", callback=self.create_labels)
                dpg.add_menu_item(label="Export Products", callback=self.export_products)

    def create_windows(self):
        self.create_menu()
        self.create_manual_entry_window()
        self.create_csv_import_window()
        self.create_product_list_window()

    def create_manual_entry_window(self):
        # Manual Entry Window
        with dpg.window(label="Manual Product Entry", tag="manual_window",
                        no_close=True, no_collapse=True, pos=[5, 25],width=400, height=250, no_resize=True, no_move=True):
            with dpg.group(horizontal=False):
                dpg.add_text("Add New Product", color=[255, 255, 0])
                dpg.add_separator()

                fields = [
                    ("name_input", "Product Name:", 200),
                    ("price_input", "Price ($):", 100),
                    ("upc_input", "UPC Code:", 150),
                    ("exp_input", "Expiration Date:", 150)
                ]

                for tag, label, width in fields:
                    with dpg.group(horizontal=True):
                        dpg.add_text(label)
                        dpg.add_input_text(tag=tag, width=width)

                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add Product", callback=self.add_manual_product)
                    dpg.add_button(label="Clear Fields", callback=self.clear_manual_fields)

                dpg.add_text("", tag="manual_status")

    def create_csv_import_window(self):
        # CSV Import Window
        with dpg.window(label="CSV Import", tag="csv_window",
            no_close=True, no_collapse=True, pos=[5,280],width=400, height=300, no_resize=True, no_move=True):
            dpg.add_text("Import Products from CSV", color=[255, 255, 0])
            dpg.add_separator()

            # File selection
            with dpg.group(horizontal=True):
                dpg.add_text("CSV File:")
                dpg.add_button(label="Select File", callback=self.select_csv_file)

            dpg.add_text("No file selected", tag="csv_file_label")
            dpg.add_separator()

            # Column mapping section
            dpg.add_text("Column Mappings", tag="mapping_header")
            with dpg.group(tag="mapping_group"):
                fields = ['name', 'price', 'upc', 'expiration_date']
                for field in fields:
                    with dpg.group(horizontal=True):
                        dpg.add_text(f"{field.title()}:")
                        dpg.add_combo([], tag=f"{field}_map", width=200)

            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Import Products", callback=self.import_csv_products, tag="import_btn")
                dpg.add_button(label="Clear", callback=self.clear_csv_import)


            # Initially disable mapping controls
            self.set_mapping_enabled(False)

    def create_product_list_window(self):
        with dpg.window(label="Product List", tag="list_window",
                       no_close=True, no_collapse=True,pos=[410, 25], width=700, height=555, no_resize=True, no_move=True):
            dpg.add_separator()

            with dpg.table(tag="product_table", header_row=True,
                          policy=dpg.mvTable_SizingFixedFit,
                          borders_innerH=True, borders_outerH=True,
                          borders_innerV=True, borders_outerV=True,
                          scrollY=True):

                dpg.add_table_column(label="Name", width=150)
                dpg.add_table_column(label="Price", width=70)
                dpg.add_table_column(label="UPC", width=100)
                dpg.add_table_column(label="Exp Date", width=100)
                dpg.add_table_column(label="Source", width=80)

            dpg.add_text("", tag="list_status")

    def set_mapping_enabled(self, enabled: bool):
        """Enable or disable mapping controls"""
        if enabled:
            dpg.bind_item_theme("mapping_group", "")
            dpg.bind_item_theme("import_btn", "")
        else:
            dpg.bind_item_theme("mapping_group", self.disabled_theme)
            dpg.bind_item_theme("import_btn", self.disabled_theme)

    def select_csv_file(self):
        # In a real app, show a file dialog
        self.csv_file_path = "example.csv"  # Simulated file selection
        
        try:
            df = pd.read_csv(self.csv_file_path)
            columns = df.columns.tolist()

            # Update mapping combos
            for field in ['name', 'price', 'upc', 'expiration_date']:
                dpg.configure_item(f"{field}_map", items=columns)

            dpg.set_value("csv_file_label", f"Selected: {os.path.basename(self.csv_file_path)}")
            self.set_mapping_enabled(True)
            dpg.set_value("csv_status", "Ready to map columns")

        except Exception as e:
            dpg.set_value("csv_status", f"Error loading file: {str(e)}")
            self.set_mapping_enabled(False)

    def import_csv_products(self):
        if not self.csv_file_path:
            dpg.set_value("csv_status", "Please select a CSV file first")
            return

        try:
            # Get mappings
            mappings = {
                field: dpg.get_value(f"{field}_map")
                for field in ['','name', 'price', 'upc', 'expiration_date']
            }

            # Import products
            df = pd.read_csv(self.csv_file_path)
            for _, row in df.iterrows():
                product_data = {
                    'name': str(row[mappings['name']]),
                    'price': float(row[mappings['price']]),
                    'upc': str(row[mappings['upc']]),
                    'expiration_date': str(row[mappings['expiration_date']]) if mappings.get('expiration_date') else ''
                }
                self.model.add_product(Product.from_dict(product_data, source="csv"))

            self.update_product_list()
            dpg.set_value("csv_status", "Products imported successfully")

        except Exception as e:
            dpg.set_value("csv_status", f"Import error: {str(e)}")

    def clear_csv_import(self):
        self.csv_file_path = None
        dpg.set_value("csv_file_label", "No file selected")
        for field in ['name', 'price', 'upc', 'expiration_date']:
            dpg.set_value(f"{field}_map", "")
        self.set_mapping_enabled(False)
        dpg.set_value("csv_status", "")

    def add_manual_product(self):
        try:
            product_data = {
                'name': dpg.get_value("name_input"),
                'price': float(dpg.get_value("price_input")),
                'upc': dpg.get_value("upc_input"),
                'expiration_date': dpg.get_value("exp_input")
            }

            product = Product.from_dict(product_data)
            self.model.add_product(product)
            self.update_product_list()
            self.clear_manual_fields()
            dpg.set_value("manual_status", "Product added successfully")

        except ValueError as e:
            dpg.set_value("manual_status", f"Error: {str(e)}")

    def clear_manual_fields(self):
        for field in ["name_input", "price_input", "upc_input", "exp_input"]:
            dpg.set_value(field, "")
        dpg.set_value("manual_status", "")

    def update_product_list(self):
        if dpg.does_item_exist("product_table"):
            # Clear existing rows
            for row in dpg.get_item_children("product_table", slot=1):
                dpg.delete_item(row)

            # Add products
            for product in self.model.get_all_products():
                with dpg.table_row(parent="product_table") as row:
                    # Make cells editable with double-click
                    for col_idx, value in enumerate([
                        product.name,
                        f"${product.price:.2f}",
                        product.upc,
                        product.expiration_date or "",
                        product.source
                    ]):
                        cell = dpg.add_text(value)
                        if col_idx < 4:  # Don't make source column editable
                            with dpg.popup(cell, mousebutton=dpg.mvMouseButton_Left):
                                dpg.add_button(label="Edit",
                                             callback=lambda: self.create_edit_popup(row, col_idx, value))

    def create_labels(self):
        products = self.model.get_all_products()
        if not products:
            dpg.set_value("list_status", "No products to create labels for")
            return

        # In a real app, show file dialog here
        output_file = "labels.pdf"

        self.create_labels_pdf(products, output_file, True, False)
        dpg.set_value("list_status", f"Labels created: {os.path.basename(output_file)}")

    def create_labels_pdf(self, products: List[Product], output_file: str, color_enabled: bool, exp_enable: bool):

        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter

        # Label dimensions
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
                    product_name = str(product.name)

                    x = margin_x + j * (label_width + label_spacing_x)
                    y = height - margin_y - (i + 1) * (label_height + label_spacing_y)

                    # Draw label border
                    c.setLineWidth(0.5)
                    c.setStrokeColor(colors.black)
                    c.rect(x, y - label_height, label_width, label_height)

                    # Draw product name
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 11)

                    first_line_limit = 25
                    product_name_lines = self.split_text(product_name, first_line_limit)

                    for line_index, line in enumerate(product_name_lines):
                        c.drawString(x + 5, y - 15 - (line_index * 10), line)

                    # Draw expiration date if enabled
                    if exp_enable:
                        c.setFont("Helvetica", 6)
                        expiration_date = str(product.expiration_date if product.expiration_date else 'N/A')
                        c.drawString(x + 5, y - 35, f"EXP: {expiration_date}")

                    # Draw barcode
                    barcode_x_position = x - margin_x
                    barcode_y_position = y - label_height + 5
                    barcode_value = str(product.upc)
                    barcode = code128.Code128(barcode_value, barHeight=label_height / 3, barWidth=.75)
                    barcode.drawOn(c, barcode_x_position, barcode_y_position)

                    # Draw price
                    price_x_position = x + text_area_width-15
                    price_y_position = y - 65

                    if color_enabled:
                        c.setFillColor(colors.yellow)
                        c.rect(price_x_position-10, price_y_position-7, price_area_width+25, 30, fill=True)

                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 24)  #let users decide with a settigns pannel
                    price_value = f"{str(product.price)}"
                    c.drawString(price_x_position+1, price_y_position-2, price_value)

                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 14)
                    dollarsign= f"$"
                    c.drawString(price_x_position-8, price_y_position-2, dollarsign)

                    product_index += 1

                if product_index >= total_products:
                    break

            if product_index < total_products:
                c.showPage()

        c.save()

    # Helper method for text splitting
    def split_text(self, text: str, limit: int) -> List[str]:
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + len(current_line) <= limit:
                current_line.append(word)
                current_length += len(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def export_products(self):
        # Simplified for example - would normally show file dialog
        self.export_to_csv("products.csv")

    def run(self):
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

def main():
    app = LabelMakerApp()
    app.run()

if __name__ == "__main__":
    print("Script has started The main file")
    main()
