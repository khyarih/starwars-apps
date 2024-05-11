import os
from osgeo import ogr
import datetime
from dateutil.parser import parse
import dateparser
import numpy as np
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd

import concurrent.futures

import dateparser
import numpy as np
import pandas as pd
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

class ShpExplorer:
    """
    A class for exploring shapefiles and analyzing attribute data.

    Attributes:
        None

    Methods:
        load_shapefile(file_path): Loads a shapefile and returns the field names and field data.
        is_number(s): Checks if a string can be converted to a number.
        is_date(s): Checks if a string can be parsed as a date.
        get_type_of_value(value): Determines the type of a value (Number, Date, or String).
        get_type(lst, threshold, caterogical_threshold, categorical_max_values, null_values): 
            Determines the type of a list of values based on the occurrence of different value types.
        process_field(fldname, fldata): Processes a field and determines its type.
        field_types(shapefile): Returns a DataFrame with the field names and their corresponding types.
        format_field_types(shapefile): Returns a dictionary with the field names and their formatted types.
    """

    def load_shapefile(self, file_path):
        """
        Loads a shapefile and returns the field names and field data.

        Args:
            file_path (str): The path to the shapefile.

        Returns:
            tuple: A tuple containing the field names and field data.
        """
        print('Processing %s' % file_path)
        ds = ogr.Open(file_path)
        if ds is None:
            print('Could not open file: ' + file_path)
            return None, None
        lyr = ds.GetLayer()
        fld_names = [field.name for field in lyr.schema]
        flds_data = {}
        lyr.ResetReading()
        for feat in lyr:
            for fld in fld_names:
                if fld not in flds_data:
                    flds_data[fld] = []
                flds_data[fld].append(feat.GetField(fld))
        return fld_names, flds_data

    def is_number(self, s):
        """
        Checks if a string can be converted to a number.

        Args:
            s (str): The string to check.

        Returns:
            bool: True if the string can be converted to a number, False otherwise.
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_date(self, s):
        """
        Checks if a string can be parsed as a date.

        Args:
            s (str): The string to check.

        Returns:
            bool: True if the string can be parsed as a date, False otherwise.
        """
        strict_settings = {'STRICT_PARSING': True}
        return bool(dateparser.parse(s, settings=strict_settings))

    def get_type_of_value(self, value):
        """
        Determines the type of a value (Number, Date, or String).

        Args:
            value: The value to determine the type of.

        Returns:
            str: The type of the value.
        """
        if self.is_number(value):
            return 'Number'
        elif self.is_date(value):
            return 'Date'
        else:
            return 'String'

    def get_type(self, lst, threshold=0.9, caterogical_threshold=0.2, categorical_max_values=100, null_values=[None]):
        """
        Determines the type of a list of values based on the occurrence of different value types.

        Args:
            lst (list): The list of values.
            threshold (float): The threshold for determining the dominant value type.
            caterogical_threshold (float): The threshold for determining if the values are categorical.
            categorical_max_values (int): The maximum number of unique values for considering the values as categorical.
            null_values (list): The list of values to be considered as null.

        Returns:
            list: A list containing the type, max value, min value, values list, and occurrence count.
        """
        data_ = np.array(lst)
        data_occurence = Counter(data_)
        for key in null_values:
            if key in data_occurence:
                del data_occurence[key]
        nbr_of_elemenst = data_occurence.total()
        if nbr_of_elemenst == 0:
            return ['Unknown', None, None, None, "0/" + str(len(lst))]
        type = 'Unknown'
        max_val = None
        min_val = None
        values_list = None
        types_dict = {'String': 0, 'Number': 0, 'Null': 0, 'Date': 0}
        values_count = len(data_occurence)
        for val, occ in data_occurence.items():
            val_type = self.get_type_of_value(val)
            types_dict[val_type] += occ
            if val_type == 'String' and types_dict['String'] / nbr_of_elemenst > (1 - threshold):
                type = 'String'
                break
            if types_dict[val_type] / nbr_of_elemenst > threshold:
                type = val_type
                if val_type == 'Number':
                    numbers = [k for (k, v) in data_occurence.items() if self.is_number(k)]
                    max_val = max(numbers)
                    min_val = min(numbers)
                break
        if nbr_of_elemenst > 0 and (values_count / nbr_of_elemenst) < caterogical_threshold and values_count <= categorical_max_values:
            if type != None:
                type = 'Categorical-' + type
            else:
                type = 'Categorical'
            values_list = []
            for val, occ in data_occurence.items():
                values_list.append(val)
        return [type, max_val, min_val, values_list, str(nbr_of_elemenst) + "/" + str(len(lst))]

    def process_field(self, fldname, fldata):
        """
        Processes a field and determines its type.

        Args:
            fldname (str): The name of the field.
            fldata (list): The list of values for the field.

        Returns:
            tuple: A tuple containing the field name and its type.
        """
        attr_type, max_val, min_val, values_list, not_null_values = self.get_type(fldata, threshold=0.9, caterogical_threshold=0.2, categorical_max_values=10, null_values=['<Nul>', None, 'INCONNU'])
        type = {'type': attr_type, 'max': max_val, 'min': min_val, 'values set': values_list, 'filled values': not_null_values}
        return fldname, type
    
    def field_types(self, shapefile:str):
        """
        Returns a DataFrame with the field names and their corresponding types.

        Args:
            shapefile (str): The path to the shapefile.

        Returns:
            DataFrame: A DataFrame with the field names and their corresponding types.
        """
        fld_names, flds_data = self.load_shapefile(shapefile)
        fld_types = {}
        with ProcessPoolExecutor() as executor:
            futures = []
            for fldname in fld_names:
                futures.append(executor.submit(self.process_field, fldname, flds_data[fldname]))
            for type in as_completed(futures):
                fldname, type = type.result()
                if fldname not in fld_types:
                    fld_types[fldname] = {}
                fld_types[fldname] = type
                
        df = pd.DataFrame(fld_types).T
        return df
    
    def format_field_types(self, shapefile:str):
        """
        Returns a dictionary with the field names and their formatted types.

        Args:
            shapefile (str): The path to the shapefile.

        Returns:
            dict: A dictionary with the field names and their formatted types.
        """
        df = self.field_types(shapefile)
        return df.to_dict(orient='index')


