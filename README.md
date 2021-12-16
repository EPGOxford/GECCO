Readme file for GECCO, the Geospatial Evaluator for electric vehicle Charging in Car parks Overnight, available on GitHub at: https://github.com/EPGOxford/GECCO

# Geospatial Evaluator for electric vehicle Charging in Car parks Overnight (GECCO)

## Overview
The Geospatial Evaluator for electrice vehicle (EV) Charging in Car parks Overnight (GECCO) was developed by the University of Oxford's Energy and Power Group. GECCO is run in QGIS from the plug-in python console. The visualisation is displayed in QGIS as the output. 

GECCO is designed to identify car park locations where EV chargers will be more valuable in meeting the overnight charging needs of residents without off-street parking. The tool uses geospatial data to evaluate the number of residential buildings without off-street parking within walking distance of the car park, along with the likelihood of competition from on-street charging and other potential nearby car parks with EV charging. 

## Running GECCO
To operate GECCO, download the source code and input files (as described below) into one folder. 

If it is not yet installed, download QGIS (https://qgis.org/en/site/forusers/download.html) and install the python plug-in. Click "show editor" and open the python script **EV_carparks_case.py** downloaded from this GitHub repository. 

Modify 

```
data_dir = <directory of source code>
```
and
```
postdist = <postcode district of interest>
geographicareas = <geographic areas that overlap with above posal district>
```
The way in which the geographic areas are saved will depend on your method of download. Make sure you specify all geographic areas which overlap with the defined postcode district. 

Run the code. The output visualisation will be displayed in QGIS on completion. 

## Input Files
Due to licencing agreements, the input data cannot be shared in this repository and must be downloaded by the user according to their licence. 

In order to run GECCO, the input data must be saved in the following format. In the folder where the python script is saved there must be five additional folders. "Geofabrik", "mm_buildings", "mm_roads", "postaldistricts", and "results". The content of each of these folders must be as follows.

### Geofabrik
This folder contains data on the location of car parks from Geofabrik and OpenStreetMap. The data can be downloaded from http://download.geofabrik.de/europe/great-britain.html and is saved as "carpark.sqlite"

### mm_buildings and mm_roads
These folders contain data layers of buildings and roads from UK Digimap https://digimap.edina.ac.uk. The data must be downloaded as per the licence of the user, through their relevant portal to UK Digimap. Within each folder, subfolders following the following format are expected: 
>mm_buildings/xx_buildings.gdb


>mm_roads/xx_roads.gdb


where xx varies according to the geographic area.

### postaldistricts
Within this folder the shape file of the postal districs is needed. This can be downloaded from the following reference and should include the shape file named "fixedpostdistrict.shp".

Pope, Addy. (2017). GB Postcode Area, Sector, District, Dataset. University of Edinburgh. https://doi.org/10.7488/ds/1947.

### results
In this folder, the results shape files will be saved. It should be created but empty initially. 

## Example output data
An example of the output data **case_output.pdf** is included in this repository as an example. 

## Copyright
GECCO © Copyright, Energy and Power Group, University of Oxford 2021. All Rights Reserved. 
The authors, being Dr Katherine A. Collett and Dr Sivapriya Mothilal Bhagavathy, have asserted their moral rights.
