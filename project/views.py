import tkinter as tk
import os
from tkinter import ttk, filedialog, messagebox
from typing import Callable, List, Dict
from controllers import LabelMakerController
from models import Product, ProductModel
class LabelMakerView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Label Maker Pro v3.0 (MVC)")
        self.geometry("1000x800")
        self.configure(bg='#f0f0f0')
        
        self.create_widgets()
        self.create_layout()
        
    def create_product_list_frame(self):
        self.tree_frame = ttk.Frame(self)
        columns = ("Name", "Price", "UPC", "Expiration Date", "Source")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        # Configure column widths and alignments
        self.tree.column("Name", width=200)
        self.tree.column("Price", width=100, anchor="e")
        self.tree.column("UPC", width=150)
        self.tree.column("Expiration Date", width=150)
        self.tree.column("Source", width=100)
        
        for col in columns:
            self.tree.heading(col, text=col)
            
        # Add different colors for manual vs CSV products
        self.tree.tag_configure('manual', background='#ffffff')
        self.tree.tag_configure('csv', background='#f0f0ff')
            
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
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

# controllers.py
class LabelMakerController:
    def __init__(self, model: ProductModel, view: LabelMakerView):
        self.model = model
        self.view = view
        self.setup_event_handlers()
        
    def handle_load_csv(self, file_path: str, mappings: dict) -> None:
        try:
            self.model.import_from_csv(file_path, mappings)
            self.view.update_product_list(self.model.get_all_products())
            self.view.show_status(f"CSV loaded: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            
    def handle_add_product(self, product_data: Dict) -> None:
        try:
            product = Product.from_dict(product_data, source="manual")
            self.model.add_product(product)
            self.view.update_product_list(self.model.get_all_products())
            self.view.clear_entry_fields()
            self.view.show_status("Product added successfully")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid product data: {str(e)}")

# main.py remains the same
def main():
    model = ProductModel()
    view = LabelMakerView()
    controller = LabelMakerController(model, view)
    view.mainloop()

if __name__ == "__main__":
    main()