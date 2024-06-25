import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
import geopandas as gpd
from ShpExplorer import ShpExplorer
import json

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

# Now import the SimilarityCalculator
from similarity.Similarity import SimilarityCalculator

class ShapefileApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shapefile Explorer")
        self.root.configure(bg="white")

        # Create Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Upload and Display Field Types
        self.tab1 = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab1, text="Field Types")

        
        self.logo_image = tk.PhotoImage(file="/home/hamza/Data/phd/STARWARS/apps/imgs/starwars+EU.png")
        self.logo_image = self.logo_image.subsample(4)
        self.logo_label = tk.Label(self.tab1, image=self.logo_image, bg="white")
        self.logo_label.place(x=10, y=10)

        self.label = tk.Label(self.tab1, text="Upload a Shapefile", bg="white")
        self.label.pack(pady=10)

        self.upload_button = tk.Button(self.tab1, text="Upload", command=self.upload_file, bg="white")
        self.upload_button.pack(pady=10)

        self.tree_frame = tk.Frame(self.tab1, bg="white", bd=2, relief="sunken")
        self.tree_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Tab 2: Display Shapefile Content and Similarity Calculation
        self.tab2 = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab2, text="Shapefile Content")

        self.content_label = tk.Label(self.tab2, text="Shapefile Content", bg="white")
        self.content_label.pack(pady=10)

        self.tree_content_frame = tk.Frame(self.tab2, bg="white", bd=2, relief="sunken")
        self.tree_content_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.tree_content = ttk.Treeview(self.tree_content_frame, selectmode="extended")
        self.tree_content.pack(fill=tk.BOTH, expand=True)

        # Dropdown for similarity function
        self.similarity_label = tk.Label(self.tab2, text="Select Similarity Function:", bg="white")
        self.similarity_label.pack(pady=5)

        self.similarity_function = tk.StringVar()
        self.similarity_combobox = ttk.Combobox(self.tab2, textvariable=self.similarity_function)
        self.similarity_combobox['values'] = ("Cosine Similarity", "Euclidean Distance", "Jaccard Similarity")
        self.similarity_combobox.pack(pady=5)

        # Checkboxes for column selection
        self.columns_frame = tk.Frame(self.tab2, bg="white")
        self.columns_frame.pack(pady=10)

        self.column_vars = {}

        self.calculate_button = tk.Button(self.tab2, text="Calculate Similarity", command=self.calculate_similarity, bg="white")
        self.calculate_button.pack(pady=10)

        self.result_label = tk.Label(self.tab2, text="", bg="white")
        self.result_label.pack(pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Shapefiles", "*.shp")])
        if file_path:
            try:
                explo = ShpExplorer()
                field_types = explo.field_types(shapefile=file_path)
                self.display_table(field_types)

                gdf = gpd.read_file(file_path)
                self.display_shapefile_content(gdf)
                self.create_column_checkboxes(gdf)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def display_table(self, field_types):
        field_types.reset_index(inplace=True)
        field_types.rename(columns={'index': 'Attribute'}, inplace=True)

        for i in self.tree.get_children():
            self.tree.delete(i)

        self.tree["column"] = list(field_types.columns)
        self.tree["show"] = "headings"
        for column in self.tree["columns"]:
            self.tree.heading(column, text=column)

        for _, row in field_types.iterrows():
            self.tree.insert("", "end", values=list(row))

    def display_shapefile_content(self, gdf):
        gdf = gdf.drop(columns='geometry')  # Exclude the geometry column

        for i in self.tree_content.get_children():
            self.tree_content.delete(i)

        self.tree_content["column"] = list(gdf.columns)
        self.tree_content["show"] = "headings"
        for column in self.tree_content["columns"]:
            self.tree_content.heading(column, text=column)

        for _, row in gdf.iterrows():
            self.tree_content.insert("", "end", values=list(row))

    def create_column_checkboxes(self, gdf):
        for widget in self.columns_frame.winfo_children():
            widget.destroy()

        columns = gdf.columns.drop('geometry')
        self.column_vars = {}
        for column in columns:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.columns_frame, text=column, variable=var, bg="white")
            chk.pack(anchor='w')
            self.column_vars[column] = var

    def calculate_similarity(self):
        selected_items = self.tree_content.selection()
        if len(selected_items) != 2:
            messagebox.showerror("Error", "Please select exactly two rows.")
            return

        row1 = self.tree_content.item(selected_items[0])['values']
        row2 = self.tree_content.item(selected_items[1])['values']

        columns_to_include = [col for col, var in self.column_vars.items() if var.get()]

        if not columns_to_include:
            messagebox.showerror("Error", "Please select at least one column for similarity calculation.")
            return

        df = pd.DataFrame([row1, row2], columns=self.tree_content["column"])
        df = df[columns_to_include].apply(pd.to_numeric, errors='coerce').fillna(0)  # Ensure numeric

        calculator = SimilarityCalculator(df)

        function = self.similarity_function.get()
        if function == "Cosine Similarity":
            result = calculator.compute_cosine_similarity().iloc[0, 1]
        elif function == "Euclidean Distance":
            result = calculator.compute_euclidean_distance().iloc[0, 1]
        elif function == "Jaccard Similarity":
            result = calculator.compute_jaccard_similarity().iloc[0, 1]
        else:
            messagebox.showerror("Error", "Please select a valid similarity function.")
            return

        self.result_label.config(text=f"Similarity Result: {result}")
        
        # Save result as JSON
        self.save_result_as_json(result, function)

    def save_result_as_json(self, result, function_name):
        result_dict = {
            "similarity_function": function_name,
            "result": result,
            "selected_columns": [col for col, var in self.column_vars.items() if var.get()]
        }
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(result_dict, f, indent=4)
            messagebox.showinfo("Success", f"Result saved to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShapefileApp(root)
    root.geometry("800x600")  # Set the window size
    root.mainloop()
