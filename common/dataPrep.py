import sys
# sys.path.append('../')
sys.path.append('../common')

from common.data import Shapefile

import pandas as pd
import numpy as np

import math
import numbers

def load_data(data_src_file:str):
    """  load data from shapefile

    Args:
        data_src_file (str): path to shapefile

    Returns:
        (pd.DataFrame): data from shapefile
    """
    data_src_shp = Shapefile(data_src_file)
    data_src_shp.load_data()
    
    return pd.DataFrame(data_src_shp.get_data())

def remove_cols(data_src:pd.DataFrame, cols:list):
    """ remove columns from data_src

    Args:
        data_src (pd.DataFrame): data source
        cols (list): list of columns to remove
        
    Returns:
        (pd.DataFrame): data source without cols  
    """
    
    new_data_src = data_src.copy()
    
    for col in cols:
        if col in new_data_src:
            del new_data_src[col]
            
    return new_data_src

def replace_null(data_src:pd.DataFrame, null_vals: list = ['NaN', '<Nul>']):
    """ replace null ['NaN', '<Null>', '', np.nan] or pd.isna(x) values with None

    Args:
        data_src (pd.DataFrame): data source
        null_val (list): list of null values to replace
    Returns:
        (pd.DataFrame): data source after replacing null values
    """
    
    # data_src = data_src.replace(null_vals, None)
    # return data_src.where(math.isnan(data_src), np.nan) # replace where the condition is false
    data_src= data_src.mask(pd.isna(data_src), None) # replace where the condition is true
    return data_src.replace(to_replace= null_vals, value= None)


def select_fields(data_src:pd.DataFrame, fields:list):
    """ select fields from data_src as a new data source

    Args:
        data_src (pd.DataFrame): data source
        fields (list): list of fields to select
    Returns:
        (pd.DataFrame): data source with selected fields
    """
    data_src_selected_fields = data_src.copy()
    
    for field in data_src_selected_fields.columns.tolist():
        if field not in fields:
            del data_src_selected_fields[field]
    return data_src_selected_fields

def split2compeleted(data_src:pd.DataFrame, fields: list = None):
    """ split data_src into completed and uncompleted data, a row is considred if none the fields is None

    Args:
        data_src (pd.DataFrame): data source
        fields (list): list of fields to select
    Returns:
        (pd.DataFrame): completed data source
        (pd.DataFrame): uncompleted data source
    """
    if fields is None:
        fields = data_src.columns.tolist()
    
    data_src_completed = data_src[data_src[fields].notnull().all(axis=1)]
    data_src_uncompleted = data_src[data_src[fields].isnull().any(axis=1)]
    
    return data_src_completed, data_src_uncompleted

def replaceNotNumber(data:pd.DataFrame, features:list):
    """ Replace not numeric values with some numbers, this strategy is useful if the features are categorical.
        Each value in the categorical values is replaced with a numeric value 1,2,3,....

    Args:
        data (pd.DataFrame): data
        features (list): the list of features to use

    Returns:
        pd.DataFrame: the new data frame with replaced values
        dict: a mask with the replaced values
    """
    replace_with = {}

    counter = 1

    for key in features:
        if key in data.keys():
            unqiues = data[key].dropna().unique()
            
            #replace with
            replace_with_map = {}
            for i in unqiues:
                replace_with_map[i] = counter
                counter += 1
            counter = 1
            replace_with[key] = replace_with_map
            
    return data.replace(replace_with), replace_with
    