#for road sector emission invnetory calculation
#overlay grids on road network and get the length each cateogry of raods within grids 
import fiona
from shapely.geometry import shape, mapping
import rtree

bufSHP = 'Emis_inv_grid_v1.shp'
intSHP = 'Roadways_gridV6.shp'
#the new shape file going to be created
ctSHP  = 'Roadways_v3.shp'

with fiona.open(bufSHP, 'r') as layer1:
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
                            geom3=geom1.intersection(geom2)
                            props['length']=geom3.length*100
                            # Add the content to the right schema in the new shp
                            layer3.write({
                                'properties': props,
                                'geometry': mapping(geom1.intersection(geom2))
                            })


#emission invnetory calcuation based on assumed vehciluar volume movment proption in each ropad cateopgry 

from geopandas import GeoDataFrame
import pandas as pd
import numpy as np
import geopandas as gp



OLR= gp.read_file('Roadways_gridV6.shp')
OLR1=pd.DataFrame(OLR)


def label_race (row):
   if row['cat'] == 'trunk' :
      tcc=(row.length/263.778046)*0.38
      return tcc
   elif row['cat'] == 'primary' :
      pcc=(row.length/355.954679)*0.28
      return pcc
   elif row['cat'] == 'secondary' :
      pcc=(row.length/368.126161)*0.15
      return pcc
   elif row['cat'] == 'tertiary' :
      pcc=(row.length/2180.144677)*0.13
      return pcc
   elif row['cat'] == 'residential' :
      pcc=(row.length/1334.340583)*0.06
      return pcc
   else:
      pcc=0
      return pcc


OLR1['lpc']=OLR1.apply (lambda row: label_race (row),axis=1)
df4=OLR1.drop_duplicates(subset='gid', take_last=True)
gidL=df4.gid.tolist()
OLR2=OLR1.groupby('gid')



aa=[]
for gL in gidL:
    dL=OLR2.get_group(gL)
    dL1=dL.lpc.sum()
    pm25=dL1*12181409.28378
    pm10=dL1*2783466.98622 
    an=(gL,pm25,pm10)
    aa.append(an)

sdb1=pd.DataFrame(aa)
sdb1.columns=['gid','pm25','pm10']

sdb1['pm10TPY']=(sdb1.pm10*365)/1000000
sdb1['pm25TPY']=(sdb1.pm25*365)/1000000
sdb2=sdb1.set_index('gid')
sdb2['gid2']=sdb1.index


db1= gp.read_file('Emis_inv_grid_v1.shp')
db2=db1.set_index('gid')

db3=db2.join(sdb2)
db3['gid2']=db3.index
db3.replace(to_replace={'pm25': {np.nan: 0}, 'pm10': {np.nan: 0},'pm10TPY': {np.nan: 0},'pm25TPY': {np.nan: 0}}, inplace=True)
db4=db3[['geometry','pm25','pm10','pm10TPY','pm25TPY','gid2']]
db5=GeoDataFrame(db4)
db5.to_file('cbe_Emiss_Inv_Trans_cal.shp',driver='ESRI Shapefile')


#to convert the bus stops into bus route by using geometry of bus stops and list of bus stops in a route which was dictionary replaced by geocordinates and the list of geocoridnates are interjoin to create line feature

df=pd.read_csv('cbe_bus_data.csv')
stli=df.stops.tolist()

stli2=[]
for c1 in stli:
    d1=ast.literal_eval(c1)
    stli2.append(d1)

inp = gp.read_file('cbe_bus_stops.shp')
inp['x'] = None
inp['y'] = None
for i, row in inp.iterrows():
    inp['x'][i] = row['geometry'].x
    inp['y'][i] = row['geometry'].y

inp['xy']='('+inp.x.map(str)+','+inp.y.map(str)+')'
inp2=inp[['original a','xy']]

inp2.columns=['stops','xy']
inp2['stops']=inp2['stops'].str.replace(' ', '')

bus=inp2.set_index('stops')['xy'].to_dict()


a=[]
for lt in stli2:
    L2 = [bus[x] for x in lt]
    a.append(L2)


c=[]
for li in a:
    te=",".join(li)
    c.append(te)

d=[]
for c1 in c:
    d1=ast.literal_eval(c1)
    d.append(d1)


be=[]
for il in d:
    #ls1 = [il]
    #print ls1
    ls2= LineString(il)
    be.append(ls2)

db1=GeoDataFrame(be)
rt=df.rt3.tolist()
ts=df.total_sing.tolist()
db1['route']=GeoDataFrame(rt)
db1['total_sing']=GeoDataFrame(ts)
db1.columns=['geometry','route','total_sing']
db1.to_file('cbe_bus_route_shape1.shp',driver='ESRI Shapefile')

#to assign grid to each bus routes and calutate the meison invnetory 
OLR= gp.read_file('cbe_bus_route_shape1.shp')
GLR=gp.read_file('Emis_Inv_grid_1km.shp')
OLR3=OLR.geometry.tolist()

te3=[]
for tee in OLR3:
    holes = GLR['geometry'].intersects(tee)
    db1=GeoDataFrame(holes)
    #db2=db1.T
    GLR['sel']=db1
    GLR1=GLR[~(GLR.sel ==False)]
    GLR2=GeoDataFrame(GLR1.geometry)
    bus=GLR1.set_index('ad')['xy2'].to_dict()
    GLR3=GLR2.geometry.tolist()
    a=MultiPolygon(GLR3)
    #GLR3=GLR2.geometry.union
    te3.append(a)

OLR['grid_sel']=te3
OLR2=OLR[['route','total_sing','grid_sel']]
OLR2.columns=['rt','ts','geometry']
OLR4=GeoDataFrame(OLR2)
OLR4.to_file('cbe_bus_route_gridV1.shp',driver='ESRI Shapefile')

#finding contains of polygone between single part of cbe_bus_route_grid and emiss_grid_1km and add the gid into it
import numpy as np
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import MultiPoint
import geopandas as gp
import ast
import fiona
from shapely.geometry import shape, mapping,LineString
from shapely.ops import cascaded_union, unary_union
import fiona
from shapely.geometry import shape
from rtree import index

GLR=gp.read_file('Emis_Inv_grid_1km.shp')
GLR['cen']=GLR.geometry.centroid
GLR1=GLR[['cen']]
GLR1['gid']=np.arange(1,3001)
GLR2=GeoDataFrame(GLR1)
GLR2.to_file('Emis_Inv_centr_1km.shp',driver='ESRI Shapefile')

#the shape file cbe_bus_route_gridV1.shp was saved as multipart into single part that file(cbe_bus_grid_sp.shp) is having all the grif feartue with route and ts id intact
bug = [pol for pol in fiona.open('cbe_bus_grid_sp.shp')]
gid = [pt for pt in fiona.open('Emis_Inv_centr_1km.shp')]

#to get teh schema of shape files and its attributs

c = fiona.open('cbe_bus_grid_sp.shp')
c.schema

idx = index.Index()
for pos, poly in enumerate(bug):
      idx.insert(pos, shape(poly['geometry']).bounds)

#rtree index based spatial intersection for finding the grid centroid and get its index number for the overlayed gird values of line features
for i,pt in enumerate(gid):
  point = shape(pt['geometry'])
  # iterate through spatial index
  for j in idx.intersection(point.coords[0]):
      if point.within(shape(bug[j]['geometry'])):
            bug[j]['properties']['gid'] = gid[i]['properties']['gid']


schema = {
    'geometry': 'Polygon',
    'properties': {'rt': 'str',
                   'ts': 'int',
                   'gid': 'int',}} 


with fiona.open ('cbe_bus_grid_ID.shp', 'w', 'ESRI Shapefile', schema) as output:
    for poly in bug:
        output.write(poly)


#to do the aggregationb of grid absed on index

DB=gp.read_file('cbe_bus_grid_ID.shp')
#the above file was opened in converted the multipart shape file into single part named as cbe_bus_grid_IDshp.shp
DB=gp.read_file('cbe_bus_grid_IDshp.shp')


DB1=DB.drop_duplicates(subset='gid', take_last=True)
DB2=DB1.set_index('gid')
DB2['gid']=DB2.index
db1=DB.groupby(by=['gid'])['ts'].sum()
db2=pd.DataFrame(db1)

DB2=db2.join(DB2[['geometry','rt','gid']])
DB3=GeoDataFrame(DB2)
DB3.to_file('CBE_bus_emiss_inv_data.shp',driver='ESRI Shapefile')


DB6=gp.read_file('CBE_bus_emiss_inv_data.shp')

db7=DB6.drop_duplicates(subset='gid', take_last=True)
db7['PM']=db7.ts*1.075
db7['PMPY']=db7.PM*365
db7['PM25TPY']=(db7.PMPY*0.814)/1000000
db7['PM10TPY']=(db7.PMPY*0.278)/1000000
db8=db7.set_index('gid')
db9=db8[['PM25TPY','PM10TPY']]


db1= gp.read_file('Emis_inv_grid_v1.shp')
db2=db1.set_index('gid')
db2['gid2']=db2.index

db3=db2.join(db9)
db3.replace(to_replace={'PM10TPY': {np.nan: 0},'PM25TPY': {np.nan: 0}}, inplace=True)
db4=db3[['geometry','PM10TPY','PM25TPY','gid2']]
db5=GeoDataFrame(db4)
db5.to_file('CBE_bus_emiss_inv_dataV1.shp',driver='ESRI Shapefile')

