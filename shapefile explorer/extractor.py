import os
import concurrent.futures
from osgeo import ogr


# Set global variables
root_dir = '../data_sets/' # Root directory
dirs = ['dataset I/','dataset II/','dataset III/','dataset IV/'] # List of directories to be searched
# dirs = ['dataset IV/'] # List of directories to be searched
out_tex_file = 'report/attributes.tex'

field_names_in_file = {} # List to hold the field names
data = {} # Dictionary to hold the data

comp_file_dict = {
    'Pipe':['dataset I/EST_OUEST/canalisations_EO',
            'dataset I/RESEAU_MAERA/canalisations',
            'dataset I/RESEAU/canalisations',
            'dataset II/A_TRONCON',
            'dataset III/M3M/A_TRONCON',
            'dataset IV/ass_rassa',
            'dataset IV/ReseauMarcheTopo',
            ],
    'Service Line':['dataset I/EST_OUEST/canalisations_de_branchement_EO', 
                    'dataset I/RESEAU/canalisations_de_branchement',
                    'dataset II/A_BRANCHEMENT_LINE', 
                    'dataset III/M3M/A_BRANCHEMENT',
                    'dataset IV/ass_brat'
                    ],
    'Connection Point':['dataset I/EST_OUEST/branchements_EO', 
                        'dataset I/RESEAU/branchements',
                        'dataset II/A_BRANCHEMENT_POINT',
                        'dataset IV/ass_bran'
                        ],
    'Manhole':['dataset I/EST_OUEST/regards_EO', 
               'dataset I/RESEAU_MAERA/regards_contrat_maera',
               'dataset I/RESEAU/regards',
               'dataset II/A_REGARD', 
               'dataset III/M3M/A_REGARD', 
               'dataset IV/REG'
               ],
    'Fitting':['dataset I/EST_OUEST/raccords_EO', 
               'dataset I/RESEAU_MAERA/raccords_contrat_maera',
               'dataset I/RESEAU/raccords',
               'dataset IV/RAC'
               ],
    'Pump Stattion':['dataset I/EST_OUEST/pompages_EO', 
                     'dataset I/RESEAU_MAERA/pompages_contrat_maera', 
                     'dataset I/RESEAU/pompages', 
                     'dataset IV/PMP'
                     ],
    'Sewage Treatment':['dataset I/EST_OUEST/station_de_traitement_EO', 
                        'dataset I/RESEAU_MAERA/station_de_traitement_contrat_maera', 
                        'dataset I/RESEAU/station_de_traitement',
                        'dataset IV/TRA'
                        ],
    'Structure':['dataset I/EST_OUEST/ouvrages_EO', 
                 'dataset I/RESEAU_MAERA/ouvrages_contrat_maera', 
                 'dataset I/RESEAU/ouvrages', 
                 'dataset II/A_OUVRAGE', 
                 'dataset III/M3M/A_OUVRAGE', 
                 'dataset IV/OUV'
                 ],
    'Accessories': ['dataset II/A_ACCESSOIRE', 
                   'dataset III/M3M/A_ACCESSOIRE'
                   ],
    'Others':['dataset IV/CommuneExploitant',
              'dataset IV/recolementEU'
              ]
    } # Dictionary to hold the file names


# Gather all shapefile paths
shapefiles = []
for comp, files in comp_file_dict.items():
    for f in files:
        shapefiles.append(root_dir + f +'.shp')
        
for shapefile in shapefiles:
    # Open the shapefile
    ds = ogr.Open(shapefile)
    
    if ds is None:
        print('Could not open file: ' + shapefile)
        continue
    
    lyr = ds.GetLayer()
    
    # Get the field names
    field_names_in_file[shapefile] = [field.name for field in lyr.schema]
        
    # Close the shapefile
    ds = None
    
# Load the shapefile data in root directory and subdirectories

# The function to be run in parallel
def process_shapefile(file_path):
    print('Processing %s' % file_path)
    # Get the field names
    # Open the shapefile
    ds = ogr.Open(file_path)
    
    if ds is None:
        print('Could not open file: ' + file_path)
        return None, None
    
    lyr = ds.GetLayer()
    fld_names = [field.name for field in lyr.schema]

    flds_data = {}
    # Get the data
    lyr.ResetReading()
    for feat in lyr: # For each feature
        for fld in fld_names:
            if fld not in flds_data:
                flds_data[fld] = []
            flds_data[fld].append(feat.GetField(fld))

    return fld_names, flds_data

# Process all shapefiles in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_to_file = {executor.submit(process_shapefile, shp): shp for shp in shapefiles}
    for future in concurrent.futures.as_completed(future_to_file):
        file = future_to_file[future]
        # fname = os.path.basename(file)
        fname = file.removeprefix(root_dir)
        try:
            fld_names, flds_data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (file, exc))
        else:
            field_names_in_file[fname] = fld_names
            data[fname] = flds_data


# Data types utils

import datetime
from dateutil.parser import parse
import dateparser
import numpy as np
from collections import Counter

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def is_date(s):
    strict_settings = {'STRICT_PARSING': True}
    return bool(dateparser.parse(s, settings=strict_settings))
    
def is_time(s):
    try:
        datetime.datetime.strptime(s, '%H:%M:%S')
        return True
    except ValueError:
        return False
    
def is_datetime(s):
    try:
        datetime.datetime.strptime(s, '%d/%m/%Y %H:%M:%S')
        return True
    except ValueError:
        return False
    
def is_bool(s):
    if s.lower() == 'true' or s.lower() == 'false':
        return True
    else:
        return False
    
def is_null(s):
    if s.lower() == '<null>' or s == None or s.upper() == 'INCONNU':
        return True
    else:
        return False


STRING = 'String'
NUMBER = 'Number'
NULL = 'Null'
DATE = 'Date'
TIME = 'Time'
DATETIME = 'Datetime'
BOOL = 'Bool'
CATEGORICAL = 'Categorical'
UNKNOWN = 'Unknown'

def get_type_of_value(value):
    if is_number(value):
        return NUMBER
    elif is_date(value):
        return DATE
    # elif is_time(value):
    #     return TIME
    # elif is_datetime(value):
    #     return DATETIME
    # elif is_bool(value):
    #     return BOOL
    # elif is_null(value):
    #     return NULL
    else:
        return STRING    
    
    
# Get the type from an attribute values list
def get_type(list, threshold=0.9, caterogical_threshold=0.2, categorical_max_values=100, null_values=[None]):
    """Get the type from an attribute values list

    Args:
        list (Any): list of values to be analyzed
        threshold (float, optional): if the number of occurences of a type is greater than the threshold, then it's the type of the attribute. Defaults to 0.9.
        caterogical_threshold (float, optional): number of unique values by the number of elements is less than the threshold, it's an Categorical attribute. Defaults to 0.2.
        categorical_max_values (int, optional): the maximum number that a categorical attribute can have. Defaults to 100.
        null_values (list, optional): list of null values. Defaults to [None].

    Returns:
        [list]: [type, max_value, min_value, values_list]
    """
    
    data_ = np.array(list)
    data_occurence = Counter(data_)
    
    # remove null values
    for key in null_values:
        if key in data_occurence:
            del data_occurence[key]
            
    # nbr of elements
    nbr_of_elemenst = data_occurence.total()
    
    if(nbr_of_elemenst == 0):
        return [UNKNOWN, None, None, None, "0/"+str(len(list))]
    
    # return vars
    type = UNKNOWN
    max_val = None
    min_val = None
    values_list = None
    
    types_dict = {STRING:0, NUMBER:0, NULL:0, DATE:0}
    
    values_count = len(data_occurence)
    
    # this takes a lot of time
    for val,occ in data_occurence.items():
        val_type = get_type_of_value(val)
        types_dict[val_type] += occ
        
        # if the number of occurences of STRING is greater than the (1 - threshold), then it's the type could be STRING or CATEGORICAL
        if val_type == STRING and types_dict[STRING] / nbr_of_elemenst > (1 - threshold):
            type = STRING
            break
        
        # if the number of occurences of a type is greater than the threshold, then it's the type
        if types_dict[val_type] / nbr_of_elemenst > threshold :
            type = val_type
            if val_type == NUMBER:
                numbers = [k for (k,v) in data_occurence.items() if is_number(k)]
                max_val = max(numbers)
                min_val = min(numbers)
            break
    
    
    if nbr_of_elemenst > 0 and (values_count / nbr_of_elemenst) < caterogical_threshold and values_count <= categorical_max_values:
        if type != None:
            type = CATEGORICAL + '-' + type
        else:
            type = CATEGORICAL
            
        values_list = []
        for val,occ in data_occurence.items():
            values_list.append(val)
        
    return [type, max_val, min_val, values_list, str(nbr_of_elemenst)+"/"+str(len(list))]


# Get the types of all fields in parallel

from concurrent.futures import ProcessPoolExecutor, as_completed

def process_field(fname, fld):
    attr_type, max_val, min_val, values_list, not_null_values = get_type(data[fname][fld], threshold=0.9, caterogical_threshold=0.2, categorical_max_values=10, null_values=['<Nul>', None, 'INCONNU'])
    type = {'type': attr_type, 'max': max_val, 'min': min_val, 'values': values_list, 'not_null_values':not_null_values}
        
    return [fname, fld, type]

fld_types = {}
with ProcessPoolExecutor() as executor:
    futures = []
    for fname in data:
        for fld in data[fname]:
            # print('Processing field {} of file {}'.format(fld, fname))
            futures.append(executor.submit(process_field, fname, fld))
            
    for type in as_completed(futures):
        fname, fld, result = type.result()
        if fname not in fld_types:
            fld_types[fname] = {}
        fld_types[fname][fld] = result
