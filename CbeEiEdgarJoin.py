from netCDF4 import Dataset
 import numpy as np
 import pandas as pd
 import os
 import numpy.lib.recfunctions as rfn
 import geopandas as gp
 from geopandas import GeoDataFrame
 
 #EDGAR HTAP EI in netcdf file formate
 fh = Dataset('edgar_HTAP_PM10_emi_2010_time.nc', mode='r')
 #the data unit is kg/m2/s
 
 #CBE EI  in shape file formate
 sdb = gp.read_file('cbe_Emiss_Inv_TotalV1.shp')
 #the data unit is ton/km2/year
 
 sdb['cen']=sdb.geometry.centroid
 
 #units conversion to match the values of EDGAR HTAP, from ton/km2/year to kg/m2/s
 sdb['pm10TOTkgM2S']=((sdb['pm10TOT']*907.185)/3.15569e7)/1000000
 sdb['pm25TOTkgM2S']=((sdb['pm10TOT']*907.185)/3.15569e7)/1000000
 
 #genareting numpy array from CBE EI
 
 sdbT=sdb[['pm10TOTkgM2S','pm25TOTkgM2S','cen']]
 
 sdbT['x'] = None
 sdbT['y'] = None
 for i, row in sdbT.iterrows():
     sdbT['x'][i] = row['cen'].x
     sdbT['y'][i] = row['cen'].y
 
 
 pm10A=sdbT['pm10TOTkgM2S'].values
 pm25A=sdbT['pm25TOTkgM2S'].values
 lat=sdbT['y'].values
 lon=sdbT['x'].values
 
 pm10A1=pm10A.reshape(60,50)
 pm25A1=pm25A.reshape(60,50)
 lat1=lat.reshape(60,50)
 lon1=lon.reshape(60,50)
 
 pm10A2=pm10A1.T
 pm25A2=pm25A1.T
 lat2=lat1.T
 lon2=lon1.T
 
 #upscaling the EI for matching resolution
 
 Nbigr=50
 Nsmallr=5
 
 Nbigc=60
 Nsmallc=6
 
 
 pm10A3=pm10A2.reshape([Nsmallr, Nbigr/Nsmallr, Nsmallc, Nbigc/Nsmallc]).sum(3).sum(1)
 pm25A3=pm25A2.reshape([Nsmallr, Nbigr/Nsmallr, Nsmallc, Nbigc/Nsmallc]).sum(3).sum(1)
 lat3=lat2.reshape([Nsmallr, Nbigr/Nsmallr, Nsmallc, Nbigc/Nsmallc]).mean(3).mean(1)
 lon3=lon2.reshape([Nsmallr, Nbigr/Nsmallr, Nsmallc, Nbigc/Nsmallc]).mean(3).mean(1)
 
 lat4=lat3.reshape(30)
 lon4=lon3.reshape(30)
 pm10A4=pm10A3.reshape(30)
 pm25A4=pm25A3.reshape(30)
 
 
 b=np.arange(30)
 db=pd.DataFrame(b)
 db['lon']=pd.DataFrame(lon4)
 db['lat']=pd.DataFrame(lat4)
 db['pm10A4']=pd.DataFrame(pm10A4)
 db['pm25A4']=pd.DataFrame(pm25A4)
 
 
 from shapely.geometry import Polygon, Point
 from geopandas import GeoDataFrame
 #creating upscaled shape file
 
 db['geometry'] = None
 for i, row in db.iterrows():
     db['geometry'][i] = Point(row['lon'], row['lat'])
 
 db1 = GeoDataFrame(db, columns=['geometry','lat','lon','pm10A4','pm25A4'], index=db.index)
 db1.to_file('cbe_emis_10KM.shp',driver='ESRI Shapefile')
 
 #summign the shape file value on EDGAR HTAP
 
 from netCDF4 import Dataset
 import numpy as np
 import pandas as pd
 import os
 import numpy.lib.recfunctions as rfn
 import geopandas as gp
 from geopandas import GeoDataFrame
 from numpy import array, arange, ix_
 
 
 ###getting and making the array to add into the netcdf array
 sdbT = gp.read_file('cbe_emis_10KM.shp')
 #this shape file contain emission ifo pm10 and pm25 in kg/m2/s
 pm10=sdb.pm10A4.tolist()
 pm25=sdb.pm25A4.tolist()
 
 pm10A=np.array(pm10).reshape(5,6)
 pm25A=np.array(pm25).reshape(5,6)
 
 sdbT['x'] = None
 sdbT['y'] = None
 for i, row in sdbT.iterrows():
     sdbT['x'][i] = row['geometry'].x
     sdbT['y'][i] = row['geometry'].y
 
 
 ab=sdbT.x.tolist()
 ac=sdbT.y.tolist()
 
 #prepaing the grid location in netcdf grid
 
 def find_closest(A, target):
     #A must be sorted
     idx = A.searchsorted(target)
     idx = np.clip(idx, 1, len(A)-1)
     left = A[idx-1]
     right = A[idx]
     idx -= target - left < right - target
     return idx
 
 
 lat10k=find_closest(lati, ac)
 lon10k=find_closest(loni, ab)
 
 lat10k1=np.unique(lat10k) 
 lon10k1=np.unique(lon10k) 
 
 
 
 
 ###preparing netcdf data
 
 fh = Dataset('edgar_HTAP_PM10_emi_2010_time.nc', mode='r')
 
 #now collecting the data
 timei=fh.variables['time'][:]
 lati=fh.variables['lat'][:]
 loni=fh.variables['lon'][:]
 emi_pmi=fh.variables['emi_pm'][:]
 
 #for pm10
 
 arm1=emi_pmi[0,:,:]
 arm1[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm2=emi_pmi[1,:,:]
 arm2[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm3=emi_pmi[2,:,:]
 arm3[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm4=emi_pmi[3,:,:]
 arm4[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm5=emi_pmi[4,:,:]
 arm5[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm6=emi_pmi[5,:,:]
 arm6[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm7=emi_pmi[6,:,:]
 arm7[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm8=emi_pmi[7,:,:]
 arm8[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm9=emi_pmi[8,:,:]
 arm9[ix_(lat10k1, lon10k1)]+=pm10A
 
 
 arm10=emi_pmi[9,:,:]
 arm10[ix_(lat10k1, lon10k1)]+=pm10A
 
 arm11=emi_pmi[10,:,:]
 arm11[ix_(lat10k1, lon10k1)]+=pm10A
 
 
 arm12=emi_pmi[11,:,:]
 arm12[ix_(lat10k1, lon10k1)]+=pm10A
 
 
 arm=[arm1,arm2,arm3,arm4,arm5,arm6,arm7,arm8,arm9,arm10,arm11,arm12]
 
 arm1=np.dstack(arm)
 
 armD=np.rollaxis(arm1,-1)
 
 dataset = Dataset('edgar_HTAP_PM10_emi_2010_timeCBE.nc', 'w',format='NETCDF3_CLASSIC')
 time  = dataset.createDimension('time', 12)
 lat   = dataset.createDimension('lat', 1800)
 lon   = dataset.createDimension('lon', 3600)
 
 
 times      = dataset.createVariable('time',np.float64, ('time',))
 latitudes  = dataset.createVariable('lat',np.float32, ('lat',))
 longitudes = dataset.createVariable('lon',np.float32, ('lon',))
 emi_pms = dataset.createVariable('emi_pm',np.float32,('time','lat','lon'))
 
 dataset.Conventions = 'CF-1.0'
 
 times.calender='standard'
 times.long_name='time'
 times.standard_name='time'
 times.units='days since 1970-01-01T00:00:00'
 
 latitudes.standard_name= 'latitude'
 latitudes.long_name= 'latitude'
 latitudes.units= 'degrees_north'
 latitudes.comment= 'cbe ei created'
 
 longitudes.standard_name= 'longitude'
 longitudes.long_name= 'longitude'
 longitudes.units= 'degrees_east'
 longitudes.comment= 'cbe ei created'
 
 emi_pms.standard_name='pm10_aerosol_due_to_emission'
 emi_pms.long_name= 'Emissions of PM10' 
 emi_pms.units= 'kg m-2 s-1'
 emi_pms.cell_method= 'time: mean (interval: 1 month,  31 days)'
 emi_pms.total_emi_pm10=    '5.11591e+008 kg/month'
 emi_pms.comment= 'cbe ei created'
 
 times[:]=timei
 latitudes[:]=lati
 longitudes[:]=loni
 emi_pms[:]=armD
 
 #generating netcdf file integrated with CBE EI
 dataset.close()
 
 #for pm25
 fh = Dataset('edgar_HTAP_PM2.5_emi_2010_time.nc', mode='r')
 
 timei=fh.variables['time'][:]
 lati=fh.variables['lat'][:]
 loni=fh.variables['lon'][:]
 emi_pmi=fh.variables['emi_pm'][:]
 
 
 
 arm1=emi_pmi[0,:,:]
 arm1[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm2=emi_pmi[1,:,:]
 arm2[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm3=emi_pmi[2,:,:]
 arm3[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm4=emi_pmi[3,:,:]
 arm4[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm5=emi_pmi[4,:,:]
 arm5[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm6=emi_pmi[5,:,:]
 arm6[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm7=emi_pmi[6,:,:]
 arm7[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm8=emi_pmi[7,:,:]
 arm8[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm9=emi_pmi[8,:,:]
 arm9[ix_(lat10k1, lon10k1)]+=pm25A
 
 
 arm10=emi_pmi[9,:,:]
 arm10[ix_(lat10k1, lon10k1)]+=pm25A
 
 arm11=emi_pmi[10,:,:]
 arm11[ix_(lat10k1, lon10k1)]+=pm25A
 
 
 arm12=emi_pmi[11,:,:]
 arm12[ix_(lat10k1, lon10k1)]+=pm25A
 
 
 arm=[arm1,arm2,arm3,arm4,arm5,arm6,arm7,arm8,arm9,arm10,arm11,arm12]
 
 arm1=np.dstack(arm)
 
 armD=np.rollaxis(arm1,-1)
 
 dataset = Dataset('edgar_HTAP_PM25_emi_2010_timeCBE.nc', 'w',format='NETCDF3_CLASSIC')
 time  = dataset.createDimension('time', 12)
 lat   = dataset.createDimension('lat', 1800)
 lon   = dataset.createDimension('lon', 3600)
 
 
 times      = dataset.createVariable('time',np.float64, ('time',))
 latitudes  = dataset.createVariable('lat',np.float32, ('lat',))
 longitudes = dataset.createVariable('lon',np.float32, ('lon',))
 emi_pms = dataset.createVariable('emi_pm',np.float32,('time','lat','lon'))
 
 dataset.Conventions = 'CF-1.0'
 
 times.calender='standard'
 times.long_name='time'
 times.standard_name='time'
 times.units='days since 1970-01-01T00:00:00'
 
 latitudes.standard_name= 'latitude'
 latitudes.long_name= 'latitude'
 latitudes.units= 'degrees_north'
 latitudes.comment= 'cbe ei created'
 
 longitudes.standard_name= 'longitude'
 longitudes.long_name= 'longitude'
 longitudes.units= 'degrees_east'
 longitudes.comment= 'cbe ei created'
 
 emi_pms.standard_name='pm10_aerosol_due_to_emission'
 emi_pms.long_name= 'Emissions of PM10' 
 emi_pms.units= 'kg m-2 s-1'
 emi_pms.cell_method= 'time: mean (interval: 1 month,  31 days)'
 emi_pms.total_emi_pm10=    '5.11591e+008 kg/month'
 emi_pms.comment= 'cbe ei created'
 
 times[:]=timei
 latitudes[:]=lati
 longitudes[:]=loni
 emi_pms[:]=armD
 
 dataset.close()
