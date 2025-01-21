import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Dict, Callable
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

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

# ============= View =============
class ColumnMappingDialog(tk.Toplevel):
    def __init__(self, parent, csv_file):
        super().__init__(parent)
        self.title("Map CSV Columns")
        self.result = None
        
        df = pd.read_csv(csv_file)
        columns = df.columns.tolist()
        
        self.mappings = {}
        required_fields = ['name', 'price', 'upc']
        optional_fields = ['expiration_date']
        
        for field in required_fields + optional_fields:
            ttk.Label(self, text=f"{field.title()}:").pack(padx=5, pady=2)
            var = tk.StringVar()
            combo = ttk.Combobox(self, textvariable=var, values=columns)
            combo.pack(padx=5, pady=2)
            self.mappings[field] = var
            
        ttk.Button(self, text="OK", command=self.save_mappings).pack(pady=10)
        
    def save_mappings(self):
        self.result = {k: v.get() for k, v in self.mappings.items() if v.get()}
        self.destroy()

class LabelMakerView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Label Maker Pro v3.0")
        self.geometry("1000x800")
        self.configure(bg='#f0f0f0')
        
        self.create_widgets()
        self.create_layout()
        
    def create_widgets(self):
        self.create_manual_entry_frame()
        self.create_product_list_frame()
        self.create_button_frame()
        self.create_status_bar()
        
    def create_manual_entry_frame(self):
        self.entry_frame = ttk.LabelFrame(self, text="Add Product")
        
        self.entries = {}
        fields = [
            ('name', "Product Name:"),
            ('price', "Price:"),
            ('upc', "UPC:"),
            ('expiration_date', "Expiration Date:")
        ]
        
        for row, (field, label) in enumerate(fields):
            ttk.Label(self.entry_frame, text=label).grid(row=row, column=0, padx=5, pady=2)
            self.entries[field] = ttk.Entry(self.entry_frame)
            self.entries[field].grid(row=row, column=1, padx=5, pady=2)
            
    def create_product_list_frame(self):
        self.tree_frame = ttk.Frame(self)
        columns = ("Name", "Price", "UPC", "Expiration Date", "Source")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        # Configure columns
        self.tree.column("Name", width=200)
        self.tree.column("Price", width=100, anchor="e")
        self.tree.column("UPC", width=150)
        self.tree.column("Expiration Date", width=150)
        self.tree.column("Source", width=100)
        
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.tag_configure('manual', background='#ffffff')
        self.tree.tag_configure('csv', background='#f0f0ff')
            
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Right-click menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Remove Product")
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def create_button_frame(self):
        self.button_frame = ttk.Frame(self)
        self.add_button = ttk.Button(self.button_frame, text="Add Product")
        self.create_labels_button = ttk.Button(self.button_frame, text="Create Labels")
        self.load_csv_button = ttk.Button(self.button_frame, text="Load CSV")
        self.export_button = ttk.Button(self.button_frame, text="Export Products")
        
    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN)
        
    def create_layout(self):
        self.entry_frame.pack(fill=tk.X, padx=10, pady=5)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        for btn in (self.add_button, self.create_labels_button, self.load_csv_button, self.export_button):
            btn.pack(side=tk.LEFT, padx=5)
            
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def get_entry_values(self) -> dict:
        return {field: entry.get() for field, entry in self.entries.items()}
        
    def clear_entry_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            
    def update_product_list(self, products: List[Product]):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for product in products:
            self.tree.insert("", tk.END, values=(
                product.name,
                f"${product.price:.2f}",
                product.upc,
                product.expiration_date or "",
                product.source
            ), tags=(product.source,))
            
    def show_status(self, message: str):
        self.status_var.set(message)

# ============= Controller =============
class LabelMakerController:
    def __init__(self, model: ProductModel, view: LabelMakerView):
        self.model = model
        self.view = view
        self.setup_event_handlers()
        
    def setup_event_handlers(self):
        self.view.add_button.config(command=self.handle_add_product)
        self.view.create_labels_button.config(command=self.handle_create_labels)
        self.view.load_csv_button.config(command=self.handle_load_csv)
        self.view.export_button.config(command=self.handle_export_products)
        self.view.context_menu.entryconfigure(0, command=self.handle_remove_product)
        
    def handle_add_product(self):
        try:
            product_data = self.view.get_entry_values()
            product = Product.from_dict(product_data, source="manual")
            self.model.add_product(product)
            self.view.update_product_list(self.model.get_all_products())
            self.view.clear_entry_fields()
            self.view.show_status("Product added successfully")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid product data: {str(e)}")
            
    def handle_remove_product(self):
        selected = self.view.tree.selection()
        if selected:
            index = self.view.tree.index(selected[0])
            self.model.remove_product(index)
            self.view.update_product_list(self.model.get_all_products())
            self.view.show_status("Product removed successfully")
            
    def handle_load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            mapping_dialog = ColumnMappingDialog(self.view, file_path)
            self.view.wait_window(mapping_dialog)
            if mapping_dialog.result:
                try:
                    self.model.import_from_csv(file_path, mapping_dialog.result)
                    self.view.update_product_list(self.model.get_all_products())
                    self.view.show_status(f"CSV loaded: {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
                    
    def handle_export_products(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            try:
                self.model.export_to_csv(file_path)
                self.view.show_status(f"Products exported: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export products: {str(e)}")
                
    def handle_create_labels(self):
        products = self.model.get_all_products()
        if not products:
            messagebox.showwarning("Warning", "No products to create labels for")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            try:
                self.create_labels_pdf(products, file_path)
                self.view.show_status(f"Labels created: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create labels: {str(e)}")
                
    def create_labels_pdf(self, products: List[Product], output_file: str):
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        
        # Label dimensions
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
            
            # Draw label border
            c.rect(x, y, label_width, label_height)
            
            # Draw product name
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x + 5, y + label_height - 15, product.name[:30])
            
            # Draw barcode
            barcode = code128.Code128(product.upc, barHeight=label_height/3)
            barcode.drawOn(c, x + 5, y + 5)
            
            # Draw price
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x + label_width - 50, y + 15, f"${product.price:.2f}")
            
        c.save()

def main():
    model = ProductModel()
    view = LabelMakerView()
    controller = LabelMakerController(model, view)
    view.mainloop()

if __name__ == "__main__":
    main()