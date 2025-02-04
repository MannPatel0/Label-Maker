import dearpygui.dearpygui as dpg


def create_product_list_window(self):
    with dpg.window(label="Product List", tag="list_window", no_close=True, no_collapse=True, pos=[410, 25], width=700, height=555, no_resize=True, no_move=True):
        # Button Row
        with dpg.group(horizontal=True):
            dpg.add_button(label="Update", callback=self.update_selected_row)
            dpg.add_button(label="Delete", callback=self.delete_selected_row)
            dpg.add_button(label="Delete All", callback=self.clear_table_fields)
        dpg.add_separator()

        # Table Styling
        with dpg.theme() as table_theme:
            with dpg.theme_component(dpg.mvTable):
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)

        # Product Table
        with dpg.table(tag="product_table", header_row=True,
                       policy=dpg.mvTable_SizingFixedFit,
                       borders_innerH=True, borders_outerH=True,
                       borders_innerV=True, borders_outerV=True,
                       scrollY=True, resizable=True,
                       on_item_clicked=self.on_row_click):

            # Table Columns
            dpg.add_table_column(label="Name", width=200)
            dpg.add_table_column(label="Price", width=100)
            dpg.add_table_column(label="UPC Code", width=200)
            dpg.add_table_column(label="Exp Date", width=200)

            # Example product data (replace with your actual data)
            self.product_data = [
                {"name": "Product 1", "price": "$10.99", "upc": "123456789", "exp_date": "2025-12-31"},
                {"name": "Product 2", "price": "$15.99", "upc": "987654321", "exp_date": "2026-06-30"},
                # Add more products here
            ]

            # Populating the table with data
            for index, product in enumerate(self.product_data):
                with dpg.table_row(tag=f"product_row_{index}"):
                    dpg.add_text(product["name"])
                    dpg.add_text(product["price"])
                    dpg.add_text(product["upc"])
                    dpg.add_text(product["exp_date"])
        # Status Text (optional)
        dpg.add_text("", tag="list_status")
    # Variable to store selected row index
    self.selected_row = None

def on_row_click(self, sender, app_data):
    # This method is triggered when a row is clicked
    self.selected_row = app_data[0]  # app_data[0] gives the index of the selected row
    print(f"Row {self.selected_row} selected.")

def update_selected_row(self):
    # Print the data of the selected row when the "Update" button is pressed
    if self.selected_row is not None:
        selected_product = self.product_data[self.selected_row]
        print(f"Updating Product: {selected_product}")
    else:
        print("No row selected.")

def delete_selected_row(self):
    # Delete the selected row and print the deleted product data
    if self.selected_row is not None:
        selected_product = self.product_data.pop(self.selected_row)  # Remove from data list
        print(f"Deleted Product: {selected_product}")
        self.refresh_table()  # Refresh the table after deletion
    else:
        print("No row selected.")

def clear_table_fields(self):
    # Clear all rows in the product table
    self.product_data.clear()
    self.refresh_table()  # Refresh table after clearing
    print("All products deleted.")

def refresh_table(self):
    # This method will clear the table and repopulate it with the updated product data
    dpg.delete_item("product_table", children_only=True)  # Delete all rows
    with dpg.table(tag="product_table", header_row=True,
                   policy=dpg.mvTable_SizingFixedFit,
                   borders_innerH=True, borders_outerH=True,
                   borders_innerV=True, borders_outerV=True,
                   scrollY=True, resizable=True):
        for index, product in enumerate(self.product_data):
            with dpg.table_row(tag=f"product_row_{index}"):
                dpg.add_text(product["name"])
                dpg.add_text(product["price"])
                dpg.add_text(product["upc"])
                dpg.add_text(product["exp_date"])
