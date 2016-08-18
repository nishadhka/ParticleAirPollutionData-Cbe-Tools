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
    pm25=dL1*918115910.4
    pm10=dL1*3842589254.4 
    an=(gL,pm25,pm10)
    aa.append(an)

sdb1=pd.DataFrame(aa)
sdb1.columns=['gid','pm25','pm10']

sdb1['pm10TPY']=(sdb1.pm10)/1000000
sdb1['pm25TPY']=(sdb1.pm25)/1000000
sdb2=sdb1.set_index('gid')
sdb2['gid2']=sdb1.index


db1= gp.read_file('Emis_inv_grid_v1.shp')
db2=db1.set_index('gid')

db3=db2.join(sdb2)
db3['gid2']=db3.index
db3.replace(to_replace={'pm25': {np.nan: 0}, 'pm10': {np.nan: 0},'pm10TPY': {np.nan: 0},'pm25TPY': {np.nan: 0}}, inplace=True)
db4=db3[['geometry','pm25','pm10','pm10TPY','pm25TPY','gid2']]
db5=GeoDataFrame(db4)
db5.to_file('cbe_Emiss_Inv_Road_cal.shp',driver='ESRI Shapefile')

