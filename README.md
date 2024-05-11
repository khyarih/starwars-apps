![Star Wars](imgs/starwars+EU.png)

# A set of tools for the analysis of the data in GIS ShapeFiles

This repository contains a set of tools to analyze the data in GIS ShapeFiles. The tools are based on the [geopandas](https://geopandas.org/) library. The tools allow you to explore the attributes of a shapefile, plot the shapefile, and extract the data from the shapefile, working with similarities ...

## ShapeFile explorer

This is a simple tool to explore the attributes of a shapefile. It tool allows you to select a shapefile from your local machine and get the attributes of the shapefile as a table, their types, and the values set for each attribute, max, and min values also the number of filled values.

### How to use it

1. Select the shapefile from your local machine.

```python
from ShpExplorer import ShpExplorer

explo = ShpExplorer()

explo.field_types(shapefile="path/file.shp")
```

2. The tool will display the attributes of the shapefile as a table.

| type              | max                | min                | values set | filled values |
|-------------------|--------------------|--------------------|------------|---------------|
| COMMUNE           | Number             | 34327.0            | 34057.0    | 119/119          |
| MSLINK            | Number             | 301.0              | 3.0        | None          |
| TYPE              | Categorical-String | None               | [Vidange, Ventouse, sonde US, Vanne, debitmetr...]       | 105/119 |
| CODE_CONT         | Categorical-String | None               | [J3561, J3551]   | 119/119 |


## Similarity Measures

This is a tool to calculate the similarity between two vectors. Using basic similarity measures like Euclidean, Manhattan, Cosine, and Jaccard similarity In addition other advanced similarity measures especially for mixed data types, when the data contains both numerical and categorical data and frequency based similarity measures.