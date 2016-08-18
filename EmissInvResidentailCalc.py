#to join census of India 2011 data with shape file features

import pandas as pd


####################
#######STEP1########
####################

#Example for a single district joining poiulation enumeration data PCA-33-632.csv and house lsiting data HL-33-632.csv
db=pd.read_csv('PCA-33-632.csv')
db0=db[['State', 'District', 'Subdistt', 'Town_Village', 'Ward', 'Level', 'Name', 'TRU', 'No of Households']]
db0.columns=[['State', 'District', 'Subdistt', 'Town_Village', 'Ward', 'Level', 'Name', 'TRU', 'No_of_Households']]
ab=pd.read_csv('HL-33-632.csv')
db3 = db0[db0['Town_Village'] == 803984]
db4=db3.set_index('Ward')
db4['Ward']=db4.index
ab3 = ab[ab['7'] == 803984]
ab4=ab3.set_index('8')
ab4['8i']=ab4.index
dbab3=db4.join(ab4)
cb1=pd.concat([dbab0,dbab3],axis=0)


#to join village boiundary feature and census data for village/ward levbel
import geopandas as gp
from geopandas import GeoDataFrame

#importing shape file of village boundaries
sdb = gp.read_file('cbe_map_RESv8.shp')
sdb1=sdb[['Area_Name','Tehsil_Nam','Village_co','wrd']]

sdb2=sdb1.set_index('wrd')
sdb2['wrd1']=sdb2.index

cd1=cb.set_index('tvw')
cd1['tvw1']=cd1.index
cd2=sdb2.join(cd1)

####################
#######STEP2########
####################
#step 2.1:

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

bug = [pol for pol in fiona.open('LU_URBAN.shp')]
gid = [pt for pt in fiona.open('Emis_Inv_centr_1km.shp')]


idx = index.Index()
for pos, poly in enumerate(bug):
      idx.insert(pos, shape(poly['geometry']).bounds)

#rtree index based spatial intersection for finding the grid centroid and get its index number for the overlayed gird values
for i,pt in enumerate(gid):
  point = shape(pt['geometry'])
  # iterate through spatial index
  for j in idx.intersection(point.coords[0]):
      if point.within(shape(bug[j]['geometry'])):
            bug[j]['properties']['gid'] = gid[i]['properties']['gid']


schema = {
    'geometry': 'Polygon',
    'properties': {'test': 'int',
                   'gid': 'int',}} 


with fiona.open ('ubran_Emiss_inv_grid.shp', 'w', 'ESRI Shapefile', schema) as output:
    for poly in bug:
        output.write(poly)

GLR=gp.read_file('ubran_Emiss_inv_grid.shp')
GLR['cen']=GLR.geometry.centroid
GLR1=GLR[['cen','gid']]
GLR1.columns=['geometry','gid']
GLR2=GeoDataFrame(GLR1)
GLR2.to_file('ubran_Emiss_inv_grid_CEN.shp',driver='ESRI Shapefile')


#step2.2: 

bug = [pol for pol in fiona.open('cbe_map_RESv8.shp')]
gid = [pt for pt in fiona.open('ubran_Emiss_inv_grid_CEN.shp')]

idx = index.Index()
for pos, poly in enumerate(bug):
      idx.insert(pos, shape(poly['geometry']).bounds)

#rtree index based spatial intersection for finding the grid centroid and get its index number for the overlayed gird values
for i,pt in enumerate(gid):
  point = shape(pt['geometry'])
  # iterate through spatial index for intersecting centroids of EI grids on each village polygon
  for j in idx.intersection(point.coords[0]):
      if point.within(shape(bug[j]['geometry'])):
            gid[i]['properties']['wrd'] = bug[j]['properties']['wrd']

schema = {
    'geometry': 'Point',
    'properties': {'gid': 'int',
                   'wrd': 'str',}} 

with fiona.open ('ubran_Emiss_inv_grid_CEN_wrd.shp', 'w', 'ESRI Shapefile', schema) as output:
    for point in gid:
        output.write(point)

#step2.4: 
ULR=gp.read_file('ubran_Emiss_inv_grid_CEN_wrd.shp')

db1=ULR.groupby(by=['wrd'])['wrd'].count()
db2=pd.DataFrame(db1)
db2['wrdProp']=1/db2.wrd
db2.columns=['gridCount','wrdProp']

ULR1=ULR.set_index('wrd')
ULR1['wrd']=ULR1.index
ULR2=ULR1.join(db2)
ULR2['sn']=np.arange(1,1124)
ULR3=ULR2.set_index('sn')

DB3=GeoDataFrame(ULR3)
DB3.to_file('ubran_Emiss_inv_grid_CEN_wrd.shp',driver='ESRI Shapefile')


####################
#######STEP3########
####################

#step 3: To get data for number of households, propotion of number of persons per household, proption of fuels usage, per capita fuel consumption per 30 days
import geopandas as gp
from geopandas import GeoDataFrame
sdb = gp.read_file('ubran_Emiss_inv_grid_CEN_wrd.shp')

sdb2=sdb.set_index('wrd')
sdb2['wrd1']=sdb2.index

cd1=cd.set_index('tvw')
cd1['tvw1']=cd1.index
cd2=sdb2.join(cd1)


cd3=cd2[['gid','wrd1','10','No_of_Households','14','56','57','58','59','60','61','62','86','87','88','89','109','110','111','112','113','114','115','116','117']]


#to equally divide the number of household into each grid within each village
#segrgating number of houses based on size of house


cd3['noh0']=cd3.No_of_Households/cd3.groupby(by=['wrd1'])['wrd1'].count()
cd3['noh']=cd3.noh0.apply(np.round)


cd3['nohs1']=cd3.noh*(cd3['56']/100)
cd3['nohs2']=cd3.noh*(cd3['57']/100)
cd3['nohs3']=cd3.noh*(cd3['58']/100)
cd3['nohs4']=cd3.noh*(cd3['59']/100)
cd3['nohs5']=cd3.noh*(cd3['60']/100)
cd3['nohs6']=cd3.noh*(cd3['61']/100)
cd3['nohs7']=cd3.noh*(cd3['62']/100)


#To cal;cualte per capita consumption of particualr fule type per house holds in each grids

#kerosens

def label_race (row):
   if row['10'] == 'Rural' :
      pcc=((row.noh*(row['nohs1']/100))*0.613)+((row.noh*(row['nohs2']/100))*0.613*2)+((row.noh*(row['nohs3']/100))*0.613*3)+((row.noh*(row['nohs4']/100))*0.613*4)+((row.noh*(row['nohs5']/100))*0.613*5)+((row.noh*(row['nohs6']/100))*0.613*6)+((row.noh*(row['nohs1']/100))*0.613*9)
      return pcc
   else:
      ccc=((row.noh*(row['nohs1']/100))*0.551)+((row.noh*(row['nohs2']/100))*0.551*2)+((row.noh*(row['nohs3']/100))*0.551*3)+((row.noh*(row['nohs4']/100))*0.551*4)+((row.noh*(row['nohs5']/100))*0.551*5)+((row.noh*(row['nohs6']/100))*0.551*6)+((row.noh*(row['nohs1']/100))*0.551*9)
      return ccc


cd3['kpc']=cd3.apply (lambda row: label_race (row),axis=1)



#firewood and crop residuals


def label_race (row):
   if row['10'] == 'Rural' :
      pcc=((row.noh*(row['nohs1']/100))*19.271)+((row.noh*(row['nohs2']/100))*19.271*2)+((row.noh*(row['nohs3']/100))*19.271*3)+((row.noh*(row['nohs4']/100))*19.271*4)+((row.noh*(row['nohs5']/100))*19.271*5)+((row.noh*(row['nohs6']/100))*19.271*6)+((row.noh*(row['nohs1']/100))*19.271*9)
      return pcc
   else:
      ccc=((row.noh*(row['nohs1']/100))*3.686)+((row.noh*(row['nohs2']/100))*3.686*2)+((row.noh*(row['nohs3']/100))*3.686*3)+((row.noh*(row['nohs4']/100))*3.686*4)+((row.noh*(row['nohs5']/100))*3.686*5)+((row.noh*(row['nohs6']/100))*3.686*6)+((row.noh*(row['nohs1']/100))*3.686*9)
      return ccc


cd3['fpc']=cd3.apply (lambda row: label_race (row),axis=1)


#no percapita data for cowdung and gobar gas for Tamil Nadu NSS 2011-2012


#coal/lignite/charcoal


def label_race (row):
   if row['10'] == 'Rural' :
      pcc=((row.noh*(row['nohs1']/100))*0.002)+((row.noh*(row['nohs2']/100))*0.002*2)+((row.noh*(row['nohs3']/100))*0.002*3)+((row.noh*(row['nohs4']/100))*0.002*4)+((row.noh*(row['nohs5']/100))*0.002*5)+((row.noh*(row['nohs6']/100))*0.002*6)+((row.noh*(row['nohs1']/100))*0.002*9)
      return pcc
   else:
      ccc=0
      return ccc


cd3['cpc']=cd3.apply (lambda row: label_race (row),axis=1)


#LPG/PNG

def label_race (row):
   if row['10'] == 'Rural' :
      pcc=((row.noh*(row['nohs1']/100))*0.948)+((row.noh*(row['nohs2']/100))*0.948*2)+((row.noh*(row['nohs3']/100))*0.948*3)+((row.noh*(row['nohs4']/100))*0.948*4)+((row.noh*(row['nohs5']/100))*0.948*5)+((row.noh*(row['nohs6']/100))*0.948*6)+((row.noh*(row['nohs1']/100))*0.948*9)
      return pcc
   else:
      ccc=((row.noh*(row['nohs1']/100))*2.17)+((row.noh*(row['nohs2']/100))*2.17*2)+((row.noh*(row['nohs3']/100))*2.17*3)+((row.noh*(row['nohs4']/100))*2.17*4)+((row.noh*(row['nohs5']/100))*2.17*5)+((row.noh*(row['nohs6']/100))*2.17*6)+((row.noh*(row['nohs1']/100))*2.17*9)
      return ccc


cd3['lpc']=cd3.apply (lambda row: label_race (row),axis=1)

cd3.to_csv('cbe_Emiss_Inv_Resi_cal_v1.csv')


####################
#######STEP4########
####################
#step 4: compute between fuel usage(emission activity) and emission factor, get values per 30 days as per consumption data


cd3['pm25']= (cd3.fpc*1.50)+(cd3.lpc*0.33)+(cd3.cpc*12.20)+(cd3.kpc*1.9)
cd3['pm10']= (cd3.fpc*15.30)+(cd3.lpc*2.1)+(cd3.cpc*20)+(cd3.kpc*1.95)


cd4=cd3[['gid','wrd1','pm25','pm10']]
cd5=cd4.set_index('gid')


sdb = gp.read_file('ubran_Emiss_inv_grid_CEN_wrd.shp')
sdb1=sdb.set_index('gid')
sdb1['gid1']=sdb1.index

sdb2=sdb1.join(cd5)

sdb3=GeoDataFrame(sdb2)


sdb3.to_file('cbe_Emiss_Inv_Resi_cal.shp',driver='ESRI Shapefile')


sdb4=sdb3.set_index('gid1')
sdb5=sdb4[['wrd1','pm25','pm10']]

sb = gp.read_file('Emis_inv_grid_v1.shp')
sb1=sb.set_index('gid')
sb1['gid2']=sb1.index

sb2=sb1.join(sdb5)

sb3=sb2[['geometry','gid2','pm25','pm10']]
sb3.replace(to_replace={'pm25': {np.nan: 0}, 'pm10': {np.nan: 0}}, inplace=True)
sb4=GeoDataFrame(sb3)
sb4.to_file('cbe_Emiss_Inv_Resi_cal.shp',driver='ESRI Shapefile')

sdb1 = gp.read_file('cbe_Emiss_Inv_Resi_cal.shp')
sdb1['pm10TPY']=(sdb1.pm10*12.16)/1000000
sdb1['pm25TPY']=(sdb1.pm25*12.16)/1000000
sdb2=GeoDataFrame(sdb1)
sdb2.to_file('cbe_Emiss_Inv_Resi_calV1.shp',driver='ESRI Shapefile')
