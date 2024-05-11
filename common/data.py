import geopandas as gpd
import numpy as np

class Shapefile:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.fld_names = []
        self.flds_data = {}
    
    def load_data(self):
        self.gdf = gpd.read_file(self.file_path)
        
        if self.gdf.empty:
            print('Could not open file: ' + self.file_path)
            return None, None
        
        self.fld_names = self.gdf.columns.tolist()
        self.flds_data = {fld: self.gdf[fld].values for fld in self.fld_names}
        
        return self
                
    def get_data(self):
        """Returns a dictionary of field names and field data"""
        return self.flds_data
    
    def get_field_names(self):
        """Returns a list of field names"""
        return self.fld_names
    
    def get_field_data(self, field_name):
        """Returns a list of field data"""
        return self.flds_data[field_name]
    
    def get_field_data_by_index(self, field_index):
        return self.flds_data[self.fld_names[field_index]]
    
    def get_geom_data(self):
        return self.gdf['geometry'].values
    
    def dataframe(self):
        return self.gdf
    
    def get_file_path(self):
        return self.file_path