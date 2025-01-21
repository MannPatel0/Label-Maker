from dataclasses import dataclass
from typing import List, Optional
import pandas as pd

@dataclass
class Product:
    name: str
    price: float
    upc: str
    expiration_date: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        return cls(
            name=str(data['name']),
            price=float(data['price']),
            upc=str(data['upc']),
            expiration_date=str(data.get('expiration_date', ''))
        )

class ProductModel:
    def __init__(self):
        self.products: List[Product] = []
        
    def add_product(self, product: Product) -> None:
        self.products.append(product)
        
    def remove_product(self, index: int) -> None:
        if 0 <= index < len(self.products):
            del self.products[index]
            
    def update_product(self, index: int, product: Product) -> None:
        if 0 <= index < len(self.products):
            self.products[index] = product
            
    def get_product(self, index: int) -> Optional[Product]:
        if 0 <= index < len(self.products):
            return self.products[index]
        return None
        
    def get_all_products(self) -> List[Product]:
        return self.products.copy()
        
    def clear_products(self) -> None:
        self.products.clear()
        
    def import_from_csv(self, file_path: str, mappings: dict) -> None:
        df = pd.read_csv(file_path)
        self.clear_products()
        
        for _, row in df.iterrows():
            product_data = {
                'name': str(row[mappings['name']]),
                'price': float(row[mappings['price']]),
                'upc': str(row[mappings['upc']]),
                'expiration_date': str(row[mappings.get('expiration_date', '')]) if 'expiration_date' in mappings else ''
            }
            self.add_product(Product.from_dict(product_data))
            
    def export_to_csv(self, file_path: str) -> None:
        df = pd.DataFrame([vars(p) for p in self.products])
        df.to_csv(file_path, index=False)
