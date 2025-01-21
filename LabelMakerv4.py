import dearpygui.dearpygui as dpg
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Dict
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

# ============= Model =============
@dataclass
class Product:
    name: str
    price: float
    upc: str
    expiration_date: Optional[str] = None
    source: str = "manual"  # Can be "manual" or "csv"
    
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
        
    def remove_product(self, index: int) -> None:
        all_products = self.get_all_products()
        if 0 <= index < len(all_products):
            product = all_products[index]
            if product.source == "csv":
                self.csv_products.remove(product)
            else:
                self.manual_products.remove(product)
            
    def get_all_products(self) -> List[Product]:
        return self.manual_products + self.csv_products
        
    def clear_csv_products(self) -> None:
        self.csv_products.clear()

    def import_from_csv(self, file_path: str, mappings: dict) -> None:
        df = pd.read_csv(file_path)
        self.clear_csv_products()
        
        for _, row in df.iterrows():
            product_data = {
                'name': str(row[mappings['name']]),
                'price': float(row[mappings['price']]),
                'upc': str(row[mappings['upc']]),
                'expiration_date': str(row[mappings.get('expiration_date', '')]) if 'expiration_date' in mappings else ''
            }
            self.add_product(Product.from_dict(product_data, source="csv"))

    def export_to_csv(self, file_path: str) -> None:
        all_products = self.get_all_products()
        df = pd.DataFrame([{
            'name': p.name,
            'price': p.price,
            'upc': p.upc,
            'expiration_date': p.expiration_date,
            'source': p.source
        } for p in all_products])
        df.to_csv(file_path, index=False)

# ============= View & Controller =============
class LabelMakerApp:
    def __init__(self):
        self.model = ProductModel()
        self.setup_dpg()
        self.create_windows()
        self.selected_item = None
        self.csv_mappings = {}
        
    def setup_dpg(self):
        dpg.create_context()
        dpg.create_viewport(title="Label Maker Pro v3.0", width=1000, height=800)
        dpg.setup_dearpygui()
        
    def create_windows(self):
        # Main window
        with dpg.window(label="Label Maker Pro", tag="primary_window"):
            # Product Entry Section
            with dpg.group(horizontal=False):
                with dpg.group(horizontal=True):
                    dpg.add_text("Product Name:")
                    dpg.add_input_text(tag="name_input", width=200)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Price:")
                    dpg.add_input_text(tag="price_input", width=100)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("UPC:")
                    dpg.add_input_text(tag="upc_input", width=150)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Expiration Date:")
                    dpg.add_input_text(tag="expiration_input", width=150)
                
            # Buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add Product", callback=self.add_product)
                dpg.add_button(label="Create Labels", callback=self.create_labels)
                dpg.add_button(label="Load CSV", callback=self.load_csv)
                dpg.add_button(label="Export Products", callback=self.export_products)
            
            # Product List Table
            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp,
                          borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True):
                dpg.add_table_column(label="Name", width_stretch=True)
                dpg.add_table_column(label="Price", width_stretch=True)
                dpg.add_table_column(label="UPC", width_stretch=True)
                dpg.add_table_column(label="Expiration Date", width_stretch=True)
                dpg.add_table_column(label="Source", width_stretch=True)
                
            # Status Bar
            dpg.add_text("Ready", tag="status_bar")
            
        dpg.set_primary_window("primary_window", True)
        
    def update_product_list(self):
        # Clear existing rows
        for row in dpg.get_item_children("primary_window", slot=1)[1:]:  # Skip header
            dpg.delete_item(row)
            
        # Add products
        for product in self.model.get_all_products():
            with dpg.table_row():
                dpg.add_text(product.name)
                dpg.add_text(f"${product.price:.2f}")
                dpg.add_text(product.upc)
                dpg.add_text(product.expiration_date or "")
                dpg.add_text(product.source)
                
    def add_product(self):
        try:
            product_data = {
                'name': dpg.get_value("name_input"),
                'price': dpg.get_value("price_input"),
                'upc': dpg.get_value("upc_input"),
                'expiration_date': dpg.get_value("expiration_input")
            }
            product = Product.from_dict(product_data)
            self.model.add_product(product)
            self.update_product_list()
            
            # Clear inputs
            dpg.set_value("name_input", "")
            dpg.set_value("price_input", "")
            dpg.set_value("upc_input", "")
            dpg.set_value("expiration_date", "")
            
            dpg.set_value("status_bar", "Product added successfully")
        except ValueError as e:
            dpg.set_value("status_bar", f"Error: {str(e)}")
            
    def create_labels(self):
        products = self.model.get_all_products()
        if not products:
            dpg.set_value("status_bar", "No products to create labels for")
            return
            
        # Open file dialog (simplified for example)
        file_path = "labels.pdf"  # In real app, use a file dialog
        try:
            self.create_labels_pdf(products, file_path)
            dpg.set_value("status_bar", f"Labels created: {os.path.basename(file_path)}")
        except Exception as e:
            dpg.set_value("status_bar", f"Error creating labels: {str(e)}")
            
    def create_labels_pdf(self, products: List[Product], output_file: str):
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        
        label_width = 2.5 * inch
        label_height = 1 * inch
        labels_per_row = 3
        labels_per_col = 9
        
        for i, product in enumerate(products):
            page_index = i // (labels_per_row * labels_per_col)
            if i > 0 and i % (labels_per_row * labels_per_col) == 0:
                c.showPage()
                
            row = (i % (labels_per_row * labels_per_col)) // labels_per_row
            col = i % labels_per_row
            
            x = col * (label_width + 0.2 * inch) + 0.1875 * inch
            y = height - (row * (label_height + 0.2 * inch) + label_height + inch)
            
            c.rect(x, y, label_width, label_height)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x + 5, y + label_height - 15, product.name[:30])
            
            barcode = code128.Code128(product.upc, barHeight=label_height/3)
            barcode.drawOn(c, x + 5, y + 5)
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x + label_width - 50, y + 15, f"${product.price:.2f}")
            
        c.save()
        
    def load_csv(self):
        # In a real app, you'd show a file dialog here
        file_path = "products.csv"  # Example path
        try:
            df = pd.read_csv(file_path)
            columns = df.columns.tolist()
            
            # Show column mapping dialog
            with dpg.window(label="Map CSV Columns", modal=True):
                for field in ['name', 'price', 'upc', 'expiration_date']:
                    dpg.add_combo(label=field, items=columns, callback=lambda s, a, u: self.csv_mappings.update({u: a}), user_data=field)
                dpg.add_button(label="Import", callback=lambda: self.import_csv(file_path))
                
        except Exception as e:
            dpg.set_value("status_bar", f"Error loading CSV: {str(e)}")
            
    def import_csv(self, file_path: str):
        try:
            self.model.import_from_csv(file_path, self.csv_mappings)
            self.update_product_list()
            dpg.set_value("status_bar", f"CSV imported: {os.path.basename(file_path)}")
        except Exception as e:
            dpg.set_value("status_bar", f"Error importing CSV: {str(e)}")
            
    def export_products(self):
        # In a real app, you'd show a file dialog here
        file_path = "export.csv"  # Example path
        try:
            self.model.export_to_csv(file_path)
            dpg.set_value("status_bar", f"Products exported: {os.path.basename(file_path)}")
        except Exception as e:
            dpg.set_value("status_bar", f"Error exporting products: {str(e)}")
            
    def run(self):
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

def main():
    app = LabelMakerApp()
    app.run()

if __name__ == "__main__":
    main()