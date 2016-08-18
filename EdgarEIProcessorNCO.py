from subprocess import call
import glob
from fnmatch import fnmatch
import os

diri=['bc','co','nh3','nmvoc','NOx','oc','pm10','pm25','so2']
fln=['BC','CO','NH3','NMVOC','NOx','OC','PM10','PM2.5','SO2']
#call(['mkdir','oc'])

#to movce the edgar files based on folders
for dr,fli in zip(diri,fln):
    call(['mkdir',dr])
    fl=glob.glob('*'+fli+'_*')
    for fli in fl:
       call(['mv',fli,dr])

#to unzip all the file in the folder

#first collecting all the files
pattern = "*.zip"
roots='/home/ubuntu/wrfout/edgar/co'

pap=[]
for path, subdirs, files in os.walk(roots):
    for name in files:
       if fnmatch(name, pattern):
           a=os.path.join(path, name)
           pap.append(a)


for pa in pap:
    call(['unzip',pa,'-d',os.path.dirname(pa)])


#find the space constriants in unzip, so deletin gthe unziped files and rmeoving it
pattern = "*.nc"
roots='/home/ubuntu/wrfout/edgar/'

pap=[]
for path, subdirs, files in os.walk(roots):
    for name in files:
       if fnmatch(name, pattern):
           a=os.path.join(path, name)
           pap.append(a)

fl=glob.glob('*0.1.nc')

for pa in pap:
    call(['rm',pa,])


#now forlooping and creating the nco
for dr,flt in zip(diri,fln):
   os.chdir('/home/ubuntu/wrfout/edgar/'+dr)
   fl=glob.glob('*_1.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_1.nc'],shell=True)
   fl=glob.glob('*_2.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_2.nc'],shell=True)
   fl=glob.glob('*_3.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_3.nc'],shell=True)
   fl=glob.glob('*_4.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_4.nc'],shell=True)
   fl=glob.glob('*_5.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_5.nc'],shell=True)
   fl=glob.glob('*_6.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_6.nc'],shell=True)
   fl=glob.glob('*_7.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_7.nc'],shell=True)
   fl=glob.glob('*_8.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_8.nc'],shell=True)
   fl=glob.glob('*_9.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_9.nc'],shell=True)
   fl=glob.glob('*_10.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_10.nc'],shell=True)
   fl=glob.glob('*_11.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_11.nc'],shell=True)
   fl=glob.glob('*_12.0.1x0.1.nc')
   call(['nces --op_typ=ttl ' +fl[0]+' '+fl[1]+' '+fl[2]+' '+fl[3]+' -o edgar_HTAP_'+flt+'_emi_2010_12.nc'],shell=True)
   call(['ncecat edgar_HTAP_'+flt+'_emi_2010_1.nc edgar_HTAP_'+flt+'_emi_2010_2.nc edgar_HTAP_'+flt+'_emi_2010_3.nc edgar_HTAP_'+flt+'_emi_2010_4.nc edgar_HTAP_'+flt+'_emi_2010_5.nc edgar_HTAP_'+flt+'_emi_2010_6.nc edgar_HTAP_'+flt+'_emi_2010_7.nc edgar_HTAP_'+flt+'_emi_2010_8.nc edgar_HTAP_'+flt+'_emi_2010_9.nc edgar_HTAP_'+flt+'_emi_2010_10.nc edgar_HTAP_'+flt+'_emi_2010_11.nc edgar_HTAP_'+flt+'_emi_2010_12.nc  edgar_HTAP_'+flt+'_emi_2010.nc'],shell=True)
   call(['ncap2 -Oh -s ''defdim("time",12); time[time]={14610,14641,14669,14700,14730,14761,14791,14822,14853,14883,14914,14944}; time@standard_name="time";time@long_name="time";time@units="days since 1970-01-01T00:00:00";time@calendar="standard";'' edgar_HTAP_'+flt+'_emi_2010.nc edgar_HTAP_'+flt+'_emi_2010_time.nc'],shell=True)
   call(['ncrename -v emi_co,emi_pm edgar_HTAP_'+flt+'_emi_2010_time.nc'],shell=True) 
