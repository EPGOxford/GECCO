import os
import processing
import math
import numpy as np


#input variables

### set directory for folder containing data folders ###
data_dir = ('/') 
### set postdist to postcode district of interest and geographicareas to matching OS data
postdist = 'OX2'
geographicareas = ['sp']
### if geographic area is tq, user must define sub-geography (sw,se,nw,ne)
subgeog = 'se'
postdistshpfile = data_dir+'postaldistricts/fixedpostdistrict.shp'

#######################
# intersection to select roads within the given postcode district
geogs = []
for loc in geographicareas:
    output_file = str(data_dir+'results/'+postdist+'_road_intersection_'+loc+'.gpkg')
    if loc == 'tq':
        processing.run("native:intersection", {'INPUT':postdistshpfile+'|layerid=0|subset=\"PostDist\"=\''+postdist+'\'','OVERLAY':data_dir+'mm_roads/'+loc+'_roads_'+subgeog+'.gdb|layername=TopographicArea|subset=\"FeatureCode\"=10172','INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OUTPUT':output_file})
    else: processing.run("native:intersection", {'INPUT':postdistshpfile+'|layerid=0|subset=\"PostDist\"=\''+postdist+'\'','OVERLAY':data_dir+'mm_roads/'+loc+'_roads.gdb|layername=TopographicArea|subset=\"FeatureCode\"=10172','INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OUTPUT':output_file})
    geogs.append(output_file)

parameters = {"LAYERS": geogs,
              "OUTPUT": data_dir+'results/'+postdist+'_road_intersection',
              "CRS":'EPSG:27700'
              }
processing.run("qgis:mergevectorlayers", parameters)
processing.run("qgis:exportaddgeometrycolumns",{'CALC_METHOD' : 0, 'INPUT' : data_dir+'results/'+postdist+'_road_intersection.gpkg|layerid=0', 'OUTPUT' : data_dir+'results/'+postdist+'_road_intersection_geog'})


#calculate road width from road geometry - assuming road is a perfect rectangle
layer=QgsVectorLayer(data_dir+'results/'+postdist+'_road_intersection_geog.gpkg')
features=layer.getFeatures()
layer.startEditing()
layer.addAttribute(QgsField("width", QVariant.Int))
field_idx = layer.fields().indexOf('width')
for f in features:
    id=f.id()
    area = f['area']
    perimeter=f['perimeter']

    a = 2
    b = -perimeter
    c = 2*area
    
    d = b*b - 4*a*c
    
    if d<0:
        width = (-b/(2*a))
    else:
        width = (-b-math.sqrt(d))/(2*a) #only solution for lower width value taken
        
    
    layer.changeAttributeValue(f.id(), field_idx, width)
layer.commitChanges()

# intersection to select buildings within the given postcode district
geogs = []
for loc in geographicareas:
    output_file = str(data_dir+'results/'+postdist+'_building_intersect'+loc+'.gpkg')
    processing.run("native:intersection", {'INPUT':postdistshpfile+'|layerid=0|subset=\"PostDist\"=\''+postdist+'\'','OVERLAY':data_dir+'mm_buildings/'+loc+'_buildings.gdb|layername=TopographicArea|subset=\"CalculatedAreaValue\"<250.0  AND \"CalculatedAreaValue\">17 AND \"DescriptiveGroup\" = \'Building\'','INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OUTPUT':output_file})
    geogs.append(output_file)

parameters = {"LAYERS": geogs,
              "OUTPUT": data_dir+'results/'+postdist+'_building_intersect',
              "CRS":'EPSG:27700'
              }
processing.run("qgis:mergevectorlayers", parameters)

# Intersection of Openstreetmap car parks with postcode district 
processing.run("native:intersection", {'INPUT':data_dir+'Geofabrik/carpark.sqlite|layername=multipolygons|subset= \"amenity\" LIKE \'%parking\' AND NOT \"amenity\" LIKE \'%cycle%\' AND \"carparkare\" >2000.0 AND ((\"other_tags\" NOT LIKE \'%"access"=>"private%\' AND \"other_tags\" NOT LIKE \'%"access"=>"no"%\') OR \"other_tags\" IS NULL)','OVERLAY':postdistshpfile+'|layerid=0|subset=\"PostDist\" = \''+postdist+'\'','OUTPUT':data_dir+'results/'+postdist+'osm.shp'})
processing.run("native:reprojectlayer", {'INPUT':data_dir+'results/'+postdist+'osm.shp','TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:6893'),'OUTPUT':data_dir+'results/'+postdist+'osm_reproj.shp'})


# define locus around the car park
locus = [400]

for distance in locus:
    #creating buffer around each of the car park features;
    processing.run("native:buffer", {'INPUT':data_dir+'results/'+postdist+'osm_reproj.shp|layerid=0','DISTANCE':distance,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':data_dir+'results/'+postdist+'_'+str(distance)+'_buffer.shp'})
    processing.run("native:intersection", {'INPUT':data_dir+'results/'+postdist+'_building_intersect.gpkg','OVERLAY':data_dir+'results/'+postdist+'_'+str(distance)+'_buffer.shp','INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'','OUTPUT':data_dir+'results/'+postdist+'_'+str(distance)})

    #ANALYSIS TO DETERMINE RELEVANT HOUSEHOLDS
    #distance between houses
    processing.run("native:joinbynearest", {'INPUT':data_dir+'results/'+postdist+'_'+str(distance)+'.gpkg|layerid=0','INPUT_2':data_dir+'results/'+postdist+'_'+str(distance)+'.gpkg|layerid=0','FIELDS_TO_COPY':[],'DISCARD_NONMATCHING':False,'PREFIX':'','NEIGHBORS':1,'MAX_DISTANCE':None,'OUTPUT':data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings'})
    layer = QgsVectorLayer(data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings.gpkg')
    layer.startEditing()
    layer.selectByExpression('"distance"<\'5\'', QgsVectorLayer.SetSelection)
    length = len(layer.fields())
    num = 6
    delete = list(range(length - num, length))
    layer.deleteAttributes(delete)
    layer.commitChanges()
    writer = QgsVectorFileWriter.writeAsVectorFormat(layer, data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered', 'utf-8', layer.crs(), "ESRI Shapefile", onlySelected = True)

    #distance between houses and road
    processing.run("native:joinbynearest", {'INPUT':data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered.shp','INPUT_2':data_dir+'results/'+postdist+'_road_intersection_geog.gpkg','FIELDS_TO_COPY':[],'DISCARD_NONMATCHING':False,'PREFIX':'','NEIGHBORS':1,'MAX_DISTANCE':None,'OUTPUT':data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered_roads.shp'})
    layer = QgsVectorLayer(data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered_roads.shp')
    layer.selectByExpression('"distance"<\'7\'', QgsVectorLayer.SetSelection) #select buildings without space for off-streeet parking between house and road
    writer = QgsVectorFileWriter.writeAsVectorFormat(layer, data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered_roads_filtered_1', 'utf-8', layer.crs(), "ESRI Shapefile", onlySelected = True)
    
    #highlighting houses on narrow roads
    layer = QgsVectorLayer(data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered_roads_filtered_1.shp')
    layer.selectByExpression('"width"<\'5\'', QgsVectorLayer.SetSelection) #select buildings without space for off-streeet parking between house and road AND takes into account the width of the road
    writer = QgsVectorFileWriter.writeAsVectorFormat(layer, data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered_roads_filtered_2', 'utf-8', layer.crs(), "ESRI Shapefile", onlySelected = True)

#show layers in QGIS
for distance in locus:
    tms = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0'
    osm = QgsRasterLayer(tms,'OSM', 'wms')
    QgsProject.instance().addMapLayer(osm)
    
    layer = QgsVectorLayer(data_dir+'results/'+postdist+'osm_reproj.shp', 'car_parks', 'ogr')
    layer.renderer().symbol().setColor(QColor('orange'))
    QgsProject.instance().addMapLayer(layer)
    
    layer = QgsVectorLayer(data_dir+'results/'+postdist+'_'+str(distance)+'_buffer.shp', str(distance)+'m_from_car_park', 'ogr')
    layer.renderer().symbol().setColor(QColor(166,206,227,40))
    layer.renderer().symbol().symbolLayer(0).setStrokeColor(QColor(166,206,227,255))
    QgsProject.instance().addMapLayer(layer)

    layer = QgsVectorLayer(data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings.gpkg', 'buildings', 'ogr')
    layer.renderer().symbol().setColor(QColor('lightgrey'))
    QgsProject.instance().addMapLayer(layer)
    
    layer = QgsVectorLayer(data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered_roads_filtered_1.shp', 'buildings_filtered', 'ogr')
    layer.renderer().symbol().setColor(QColor('green'))
    QgsProject.instance().addMapLayer(layer)

    layer = QgsVectorLayer(data_dir+'results/'+postdist+'_' +str(distance)+'_NNJoin_buildings_filtered_roads_filtered_2.shp', 'buildings_filtered_and_on_narrow_roads', 'ogr')
    layer.renderer().symbol().setColor(QColor('cyan'))
    QgsProject.instance().addMapLayer(layer)

qgis.utils.iface.setActiveLayer(layer)
qgis.utils.iface.zoomToActiveLayer()