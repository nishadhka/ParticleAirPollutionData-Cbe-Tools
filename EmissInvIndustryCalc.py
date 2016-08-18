import geopandas as gp
from geopandas import GeoDataFrame
import pandas as pd
import numpy as np
import fiona
from shapely.geometry import shape, mapping
import rtree

bufSHP = 'Emis_inv_grid_v1.shp'#layer1
intSHP = 'Emiss_IND_data_v2.shp'#layer3,ouput
#the new shape file going to be created
ctSHP  = 'Emiss_IND_data_v1.shp'#layer2

with fiona.open(bufSHP, 'r') as layer1:
    schema = layer2.schema.copy()
    schema['properties']['gid'] = 'int:10'
    with fiona.open(ctSHP, 'r') as layer2:
        # We copy schema and add the  new property for the new resulting shp
        schema = layer2.schema.copy()
        schema['properties']['gid'] = 'int:10'
        # We open a first empty shp to write new content from both others shp
        with fiona.open(intSHP, 'w', 'ESRI Shapefile', schema) as layer3:
            index = rtree.index.Index()
            for feat1 in layer1:
                fid = int(feat1['id'])
                geom1 = shape(feat1['geometry'])
                index.insert(fid, geom1.bounds)
            for feat2 in layer2:
                geom2 = shape(feat2['geometry'])
                for fid in list(index.intersection(geom2.bounds)):
                    if fid != int(feat2['id']):
                        feat1 = layer1[fid]
                        geom1 = shape(feat1['geometry'])
                        if geom1.intersects(geom2):
                            # We take attributes from ctSHP
                            props = feat2['properties']
                            # Then append the uid attribute we want from the other shp
                            props['gid'] = feat1['properties']['gid']
                            #geom3=geom1.intersection(geom2)
                            #props['length']=geom3.length*100
                            # Add the content to the right schema in the new shp
                            layer3.write({
                                'properties': props,
                                'geometry': mapping(geom1.intersection(geom2))
                            })


gb= gp.read_file('Emis_inv_grid_v1.shp')
gb1=gb.set_index('gid')


sb= gp.read_file('Emiss_IND_data_v2.shp')

sb1=sb.drop_duplicates(subset='gid', take_last=True)
sb2=sb1.set_index('gid')



sb2['pm10_emiss_s']=sb.groupby(by=['gid'])['PM10_emiss'].sum()
sb2['pm25_emiss_s']=sb.groupby(by=['gid'])['PM25_emiss'].sum()




sb3=sb2[['pm10_emiss_s', 'pm25_emiss_s']]


gb2=gb1.join(sb3)

gb2.replace(to_replace={'pm10_emiss_s': {np.nan: 0},'pm25_emiss_s': {np.nan: 0}}, inplace=True)
gb2['gid2']=gb2.index
gb3=gb2[['geometry','gid2','pm10_emiss_s','pm25_emiss_s']]
gb3['PM25TPY']=(gb3.pm25_emiss_s*365)/1000000
gb3['PM10TPY']=(gb3.pm10_emiss_s*365)/1000000


gb4=GeoDataFrame(gb3)

gb4.to_file('Emiss_IND_data_v2_grid.shp',driver='ESRI Shapefile')
