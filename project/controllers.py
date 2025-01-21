import tkinter as tk
from tkinter import messagebox, filedialog
from models import Product, ProductModel
from typing import Optional, Dict
import os

class LabelMakerController:
    def __init__(self, model: ProductModel, view: 'LabelMakerView'):
        self.model = model
        self.view = view
        self.setup_event_handlers()
        
    def setup_event_handlers(self):
        self.view.bind_add_product(self.handle_add_product)
        self.view.bind_remove_product(self.handle_remove_product)
        self.view.bind_create_labels(self.handle_create_labels)
        self.view.bind_load_csv(self.handle_load_csv)
        self.view.bind_export_products(self.handle_export_products)
        
    def handle_add_product(self, product_data: Dict) -> None:
        try:
            product = Product.from_dict(product_data)
            self.model.add_product(product)
            self.view.update_product_list(self.model.get_all_products())
            self.view.clear_entry_fields()
            self.view.show_status("Product added successfully")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid product data: {str(e)}")
            
    def handle_remove_product(self, index: int) -> None:
        self.model.remove_product(index)
        self.view.update_product_list(self.model.get_all_products())
        self.view.show_status("Product removed successfully")
        
    def handle_create_labels(self, output_file: str, config: dict) -> None:
        if not self.model.get_all_products():
            messagebox.showwarning("Warning", "No products to create labels for")
            return
            
        try:
            self.create_labels(output_file, config)
            self.view.show_status(f"Labels created: {os.path.basename(output_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create labels: {str(e)}")
            
    def handle_load_csv(self, file_path: str, mappings: dict) -> None:
        try:
            self.model.import_from_csv(file_path, mappings)
            self.view.update_product_list(self.model.get_all_products())
            self.view.show_status(f"CSV loaded: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            
    def handle_export_products(self, file_path: str) -> None:
        try:
            self.model.export_to_csv(file_path)
            self.view.show_status(f"Products exported: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export products: {str(e)}")
