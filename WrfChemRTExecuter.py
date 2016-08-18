 #, it is a modification of WRF only functioning script into complete functional WRF CHEM runnning script
 # This script goes through processing of WPS and WRF (either, or both)
 # And submission of the job to a Rocks cluster if desired (edit to taste) 
 # Run it ("python lazyWRF.py") from your WPS folder.
 
 # John Lawson, Iowa State University 2013
 # Email john.rob.lawson@googlemail.com
 # Enabled WRF CHEM functionality, Nishadh.K.A., SACON 2014
 # Email nishadhka@sacon.in
 # -------------IMPORTANT NOTES---------------
 # Remove met_em files if you don't want them overwritten (or hide them)
 # Make sure all SETTINGS are correct
 # Make sure you've read all the comments down to "Edit above here"
 # Make sure you've set other settings in both namelists that aren't covered in this script
 # (This script won't remove any bogus lines in either namelist, syntax errors etc)
 # Then run this script
 # If job submission is switched on, make sure namelist.input parameterisations are correct
 # This script will sync all namelist.wps settings with namelist.output
 # Submit issues and requests to the GitHub (https://github.com/johnrobertlawson/lazyWRF)
 
 # IMPORTS
 import os
 import sys
 import pdb
 import glob
 import subprocess
 import calendar
 import math
 import datetime
 from datetime import datetime as detit
 import time
 import fileinput
 import logging
 ######################################
 ### EDIT BELOW HERE ##################
 ######################################
 
 ##### Script SETTINGS #####
 # If switched on, this will do pre-processing (WPS)
 WPS = 0
 # If switched on, this will do WRF processing
 WRF = 0
 # If switched on, the script will submit jobs (edit as needed)
 submit_job = 0
 # if switched on, this will do emission invneorty program prep_chem_src
 PREP_CHEM_SRC = 1
 # if switched on, this will do wrfchem processing
 # This switch on requiers PREP_CHEM_SRC = 1
 WRFCHEM = 0
 #if switched on, this will do ndown.exe and nesting
 ndown_d2 = 0
 
 ndown_d3 = 0
 # If switched on, existing wrfout files etc will be moved to a folder
 move_wrfout = 0 # WORK IN PROGRESS
 
 # Path to WRF, WPS folders (absolute) - end in a slash!
 pathtoWPS = '/home/hoopoe/wrfchem341/WRFCHEM_CBE_A9/'
 pathtoWRF = '/home/hoopoe/wrfchem341/WRFV3_mpichA4/WRFV3/test/em_real/'
 pathtoPCS = '/home/hoopoe/wrfchem341/WRFV3_mpichA4/PREP-CHEM-SRC-1.4/bin/'
 #pathtoPWCE = '/home/swl-sacon-dst/Documents/GISE_2013/LAB/WRF-chem/Data/2010/4V'
 pathtoWRFCHEM = '/home/hoopoe/wrfchem341/WRFV3_mpichA4/WRFV3/test/em_real/'
 # Path to move wrfout* files - end in a slash!
 pathtowrfout = '/home/hoopoe/wrfchem341/WRFV3_mpichA4/wrf_output/'
 
 ########################################
 #########logging and tiuming ###########
 #### based on http://stackoverflow.com/questions/1557571/how-to-get-time-of-a-python-program-execution
 ########################################
 start_time = detit.now()
 datew=start_time.strftime('%Y-%m-%d_%H_%M_%S')
 
 logger = logging.getLogger('COSM')
 hdlr = logging.FileHandler('/home/hoopoe/wrfchem341/WRFCHEM_CBE_A9/lazyWRF_WRFCHEM_'+datew+'.log')
 formatter = logging.Formatter('%(asctime)s: %(levelname)s %(message)s')
 hdlr.setFormatter(formatter)
 logger.addHandler(hdlr)
 logger.setLevel(logging.INFO)
 #start_time = time.time()
 logger.info("simulation started on"+ datew)
 ########################################
 # If you want error messages sent to an email, fill it here as a string; otherwise put '0'.
 # email = 'yourname@domain.edu'
 email = 0
 
 ##### WRF run SETTINGS #####
 # Start and end date in (YYYY,MM,DD,H,M,S)
 # for real time purpose always simulate for next six hours
 idatert=datetime.datetime.now()
 iyrt,imrt,idrt,ihrt= idatert.year, idatert.month, idatert.day, idatert.hour
 fdatert=datetime.datetime.now()+datetime.timedelta(hours=6)
 fyrt,fmrt,fdrt,fhrt= fdatert.year, fdatert.month, fdatert.day, fdatert.hour
 
 
 idate = (2014,06,05,0,0,0)
 interval = 3.0 # In hours, as a float
 fdate = (2014,06,05,06,0,0)
 domains = 3
 e_we = (90,76,97,136,) # Needs to be same length as number of domains
 e_sn = (85,73,106,157,)
 dx = 27 # In km; grid spacing of largest domain
 dy = 27 # Ditto
 i_start = (1,26,22,22,) # Same length as num of domains
 j_start = (1,7,15,32,)
 parent_grid_ratio = (1,3,3,3,) # Same length as num of domains; ratio of each parent to its child
 
 
 # Select initial data source
 # 'gfs' = GFS analyses
 # 'nam' = NAM analyses
 # 'gfstr' = real time simulaiton
 init_data = 'gfs'
 # Directory with initialisation data (absolute, or relative to WPS) - end in a slash!
 pathtoinitdata = '/home/hoopoe/wrfchem341/WRFCHEM_CBE_A6/gfs/'
 # Intermediate file prefix (usually no need to change)
 int_prefix = "'FILE'"
 
 ### NOTE:
 # Any settings you want to change that aren't in this box (e.g. time step),
 # you need to manually change yourself in its relevant namelist.
 # Submit a github request if you think it can be automated/is commonly changed
 
 ######################################
 ### EDIT ABOVE HERE ##################
 ######################################
 
 # FUNCTIONS
 
 def edit_namelist(old,new,incolumn=1):
     nwps = open('namelist.wps','r').readlines()
     for idx, line in enumerate(nwps):
         if old in line:
             # Prefix for soil intermediate data filename
             if incolumn==1:
                 nwps[idx] = nwps[idx][:23] + new + " \n"
             else:
                 nwps[idx] = ' ' + old + ' = ' + new + "\n"
             nameout = open('namelist.wps','w')
             nameout.writelines(nwps)
             nameout.close()
             break
     return
 
 def edit_namelist_input(old,new,incolumn=0,pathtoWRF=pathtoWRF):
     ninput = open(pathtoWRFCHEM+'namelist.input','r').readlines()
     for idx, line in enumerate(ninput):
         if old in line:
 	    # Prefix for soil intermediate data filename
             if incolumn==1:
                 ninput[idx] = ninput[idx][:43] + new + " \n"
             else:
                 ninput[idx] = ' ' + old + ' = ' + new + "\n"
             nameout = open(pathtoWRFCHEM+'namelist.input','w')
             nameout.writelines(ninput)
             nameout.close()
             break
     return
 
 def edit_namelist_PCS(old,new,incolumn=0,pathtoPCS=pathtoPCS):
     ninput = open(pathtoPCS+'prep_chem_sources.inp','r').readlines()
     for idx, line in enumerate(ninput):
         if old in line:
 	    # Prefix for soil intermediate data filename
             if incolumn==1:
                 ninput[idx] = ninput[idx][:43] + new + " \n"
             else:
                 ninput[idx] = ' ' + old + ' = ' + new + "\n"
             nameout = open(pathtoPCS+'prep_chem_sources.inp','w')
             nameout.writelines(ninput)
             nameout.close()
             break
     return
 
 def add_namelist_input(old,new):
     for line in fileinput.input(pathtoWRFCHEM+'namelist.input', inplace=1):
         print line,
         if line.startswith(old):
            print new
     return
 
 
 def str_from_date(date,format):
     # date = Input is tuple (yyyy,mm,dd,h,m,s)
     # format = choose 'list' or 'indiv' or...
     # ... year, month, day, hour, minute, second output
     datelist = []
     for n in date:
         datelist.append("%02u" %n)
     if format=='list':
         return datelist
     else:
         year,month,day,hour,minute,second = datelist
         if format=='indiv':
             return year,month,day,hour,minute,second
         else:
             val = eval(format)
             return val
 
 def download_data(date,initdata,pathtoinitdata):
     # Download gfs, nam data from server for a timestamp
     if initdata == 'gfs':
         prefix = 'gfsanl'
         n = '3'
         suffix = '.grb'
     elif initdata == 'nam':
         prefix = 'namanl'
         n = '218'
         suffix = '.grb'
     command = ('wget "http://nomads.ncdc.noaa.gov/data/' + prefix + '/' + date[:6] + '/' + date[:8] + 
                 '/' + prefix + '_' + n + '_' + date + '_000' + suffix + '" -P ' + pathtoinitdata)
     #elif initdata == 'gfstr':
     #    prefix = 'gfs'
     #    nrt=datetime.datetime.now().hour
 	#if 0 <= nrt <= 6:
 	#	cc=00
         #if 6 <= nrt <= 12:
 	#	cc=06
         #if 12 <= nrt <= 18:
         #        cc=12
         #if 18 <= nrt <= 23.5:
         #        cc=18
     #command = ('wget "ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/' + prefix + '.'+date[:8]+cc+
     #           '/'+prefix+'.t'+cc+'z.pgrbf'+date[9:11]+'.grib2')
     os.system(command)
     return
 
 def get_init_files(initdata,idate,interval,fdate,pathtoinitdata):
     # Let's assume all initdata possibilities start at 0000 UTC and the interval is an integer factor
     if initdata=='gfs':
         prefix = 'gfsanl'
     elif initdata=='nam':
         prefix = 'namanl'
     #elif initdata=='gfsrt':
     #    prefix = 'gfs'
 
     # First, convert dates to seconds-from-epoch time
     idaten = calendar.timegm(idate)
     fdaten = calendar.timegm(fdate)
     
     # The initial and final files needed:
     ifiledate = idaten - idaten%(interval*3600)
     ffiledate = fdaten - fdaten%(interval*3600) + (interval*3600)
 
     # Create a range of required file dates
     required_dates = range(int(ifiledate),int(ffiledate),int(interval*3600))
 
     # List all files in initialisation data folder
     initfiles = glob.glob(pathtoinitdata + '*')
 
     # Loop through times and check to see if file exists for initialisation model
     for r in required_dates:
         # Tuple of date (9 items long starting with year, month, etc...)
         longdate = time.gmtime(r)
         fname_date = ''.join(["%02u" %x for x in longdate[0:3]]) + '_' + ''.join(["%02u" %x for x in longdate[3:5]])
         checkfiles_prefix = []
         checkfiles_date = []
         for f in initfiles:
             checkfiles_prefix.append(prefix in f)
             checkfiles_date.append(fname_date in f)
         try:
             checkfiles_prefix.index(1) + checkfiles_date.index(1)
         except ValueError:
             logger.info('Downloading required file for ' + fname_date)
             download_data(fname_date,init_data,pathtoinitdata)
         else:     
             logger.info('Data for ' + fname_date + ' already exists.')
     return
 
 # This function runs a script and checks for errors; raises exception if one exists
 def intelligent_run(executable,email):
     # email = if you want email sent to an address, fill it here
     command = './' + executable + '.exe'
     os.system(command)
     logfile = open(executable + '.log').readlines() 
     if "Successful completion" in logfile[-1]:
         print '>>>>>>>> ' , executable, "has completed successfully. <<<<<<<<"
     else:
         print '!!!!!!!! ' , executable, "has failed. Exiting... !!!!!!!!"
         if email:
             os.system('tail '+logfile+' | mail -s "lazyWRF message: error in '+executable+'." '+email)
         raise Exception
     return
 
 def intelligent_pcsrun(executable):
     # email = if you want email sent to an address, fill it here
     command = './' + executable + '.exe'
     os.system(command)
     return
 
 def intelligent_mpirun(executable):
     # email = if you want email sent to an address, fill it here
     command = 'mpirun -np 3 -host dhcppc3 ./' + executable + '.exe'
     os.system(command)
     return
 
 ###############################
 #### BEGINNING OF CODE ########
 ###############################
 
 y1,mth1,d1,h1,min1,s1 = str_from_date(idate,'indiv')
 y2,mth2,d2,h2,min2,s2 = str_from_date(fdate,'indiv')
 
 if WPS:
     os.system('rm FILE* geo_em* GRIB* met_em* ')
     os.system('cp ' + pathtoWPS +'namelist_DUSTONLY.wps' ' namelist.wps')
     # Open the WPS namelist; copy the old one in case of bugs
     #os.system('cp ' + pathtoWPS + 'namelist.wps' ' namelist.wps.D01_B')
     nwps = open('namelist.wps','r').readlines()
     # Sets values depending on initialisation data
     if init_data == 'gfs':
     	atmos_levs = 27
    	soil_levs = 4
     	Vtable_suffix = 'GFS'
     	init_prefix = 'gfsanl'
     elif init_data == 'nam':
     	atmos_levs = 40
     	soil_levs = 4
     	Vtable_suffix = 'NAM'
     	init_prefix = 'namanl'
 
     # Get nice strings for namelist writing
     y1,mth1,d1,h1,min1,s1 = str_from_date(idate,'indiv')
     y2,mth2,d2,h2,min2,s2 = str_from_date(fdate,'indiv')
     # Prepares namelist.wps
     idate_s = "'"+y1+"-"+mth1+"-"+d1+'_'+h1+':'+min1+":"+s1+"',"
     edit_namelist("start_date",idate_s * domains, incolumn=0)
     fdate_s = "'"+y2+"-"+mth2+"-"+d2+'_'+h2+':'+min2+":"+s2+"',"
     edit_namelist("end_date",fdate_s * domains, incolumn=0)
     #edit_namelist("max_dom",str(domains)+',',incolumn=0)
     edit_namelist("interval_seconds",str(int(interval*3600))+',', incolumn=0)
     edit_namelist("parent_grid_ratio",', '.join([str(p) for p in parent_grid_ratio])+',', incolumn=0)
     edit_namelist("i_parent_start", ', '.join([str(i) for i in i_start])+',', incolumn=0)
     edit_namelist("j_parent_start", ', '.join([str(j) for j in j_start])+',', incolumn=0)
     edit_namelist("dx",str(1000*int(dx))+',',incolumn=0)
     edit_namelist("dy",str(1000*int(dy))+',',incolumn=0)
     edit_namelist("e_we",', '.join([str(w) for w in e_we])+',', incolumn=0)
     edit_namelist("e_sn",', '.join([str(s) for s in e_sn])+',', incolumn=0)
     edit_namelist("prefix",int_prefix+',',incolumn=0)
     edit_namelist("fg_name",int_prefix+',',incolumn=0)
 
     # Add your own here if wanting to change e.g. domain location, dx, dy from here...    
 
     # Run geogrid
     intelligent_run('geogrid',email)
 
     # Check to see if initialisation files exist
     # If they don't, download into data directory
     get_init_files(init_data,idate,interval,fdate,pathtoinitdata)
 
     # Link to, and ungrib, initialisation files
     os.system('./link_grib.csh ' + pathtoinitdata + init_prefix)
     os.system('ln -sf ungrib/Variable_Tables/Vtable.' + Vtable_suffix + ' Vtable')
     intelligent_run('ungrib',email)
     intelligent_run('metgrid',email)
     wps_time = detit.now()
     logger.info('Duration for WPS to complete: {}'.format(wps_time - start_time)) 
 
 # Submit jobs (edit as needed)
 if WRF:
     os.chdir(pathtoWRF)
     # Soft link data netCDFs files from WPS to WRF
     os.system('ln -sf ' + pathtoWPS + 'met_em* ' + pathtoWRF)
     
     ##### Sync namelist.input with namelist.wps
     # Copy original in case of bugs
     os.system('cp ' + pathtoWRF +'namelist.input' ' namelist.input.python_backup')
     
     print 'met_em* linked. Now amending namelist.input.'
     logger.info('met_em* linked. Now amending namelist.input.')
     # Compute run time
     dt_1 = calendar.timegm(idate)
     dt_2 = calendar.timegm(fdate)
     dt = datetime.timedelta(seconds=(dt_2 - dt_1))
     days = dt.days
     hrs = math.floor(dt.seconds/3600.0)
     mins = ((dt.seconds/3600.0) - hrs) * 60.0
     secs = 0 # Assumed!
 
     # Compute dx,dy for each domain
     dxs = [dx*1000]
     if domains != 1:
         for idx in range(1,domains):
             child_dx = dxs[idx-1] * 1.0/parent_grid_ratio[idx]
             dxs.append(child_dx)
     dys = [dy*1000]
     if domains != 1:
         for idx in range(1,domains):
             child_dy = dys[idx-1] * 1.0/parent_grid_ratio[idx]
             dys.append(child_dy)
 
     # If all namelist values begin on column 38:
     edit_namelist_input("run_days","%01u" %days + ',')
     edit_namelist_input("run_hours","%01u" %hrs + ',')
     edit_namelist_input("run_minutes","%01u" %mins + ',')
     edit_namelist_input("run_seconds","%01u" %secs + ',')
     edit_namelist_input("start_year", (y1+', ')*domains)
     edit_namelist_input("start_month", (mth1+', ')*domains)
     edit_namelist_input("start_day", (d1+', ')*domains)
     edit_namelist_input("start_hour", (h1+', ')*domains)
     edit_namelist_input("start_minute", (min1+', ')*domains)
     edit_namelist_input("start_second", (s1+', ')*domains)
     edit_namelist_input("end_year", (y2+', ')*domains)
     edit_namelist_input("end_month", (mth2+', ')*domains)
     edit_namelist_input("end_day", (d2+', ')*domains)
     edit_namelist_input("end_hour", (h2+', ')*domains)
     edit_namelist_input("end_minute", (min2+', ')*domains)
     edit_namelist_input("end_second", (s2+', ')*domains)
     edit_namelist_input("interval_seconds", str(int(interval*3600))+',')
     edit_namelist_input("max_dom",str(domains))
     edit_namelist_input("e_we", ', '.join([str(w) for w in e_we])+',')
     edit_namelist_input("e_sn", ', '.join([str(s) for s in e_sn])+',')
     edit_namelist_input("num_metgrid_levels", str(atmos_levs)+',')
     edit_namelist_input("dx", ', '.join([str(d) for d in dxs])+',')
     edit_namelist_input("dy", ', '.join([str(d) for d in dys])+',')
     edit_namelist_input("i_parent_start", ', '.join([str(i) for i in i_start])+',')
     edit_namelist_input("j_parent_start", ', '.join([str(j) for j in j_start])+',')
     edit_namelist_input("parent_grid_ratio",', '.join([str(p) for p in parent_grid_ratio])+',') 
 
     
     if submit_job:
         logger.info('Namelist edited. Now submitting real.exe.') 
         # Run real, get ID number of job
         # Change name of submission script if needed
         p_real = subprocess.Popen('./real.exe',cwd=pathtoWRF,shell=True,stdout=subprocess.PIPE)
         p_real.wait()
         jobid = p_real.stdout.read()[:5] # Assuming first five digits = job ID.
         # Run WRF but wait until Real has finished without errors
         logger.info('Now submitting wrf.exe.'  )
         # Again, change name of submission script if needed
         p_wrf = subprocess.Popen('./wrf.exe',cwd=pathtoWRF,shell=True,stdout=subprocess.PIPE)
         p_wrf.wait()
         logger.info("real.exe and wrf.exe submitted. Exiting Python script.")
 
 
 
 if PREP_CHEM_SRC:
     os.chdir(pathtoPCS)
     os.system('cp ' + pathtoPCS +'prep_chem_sources.inp' ' PCS_namelist.inp.python_backup')
     edit_namelist_PCS("ihour", h1, incolumn=0)
     edit_namelist_PCS("iday", d1, incolumn=0)
     edit_namelist_PCS("imon", mth1, incolumn=0)
     edit_namelist_PCS("iyear", y1, incolumn=0)
     # for time being other namelist variables are not included
     #edit_namelist_PCS("NGRIDS", domains, incolumn=0)
     #edit_namelist_PCS("NNXP", y1, incolumn=0)
     #edit_namelist_PCS("NNYP", y1, incolumn=0)
     #edit_namelist_PCS("iyear", y1, incolumn=0)
     intelligent_pcsrun('prep_chem_sources_RADM_WRF_FIM')
     prep_time = detit.now()
     #logger.info('Duration for Prep_chem_src to complete: {}'.format(prep_time - wps_time)) 
  
 if WRFCHEM:
     os.chdir(pathtoWRFCHEM)
     os.system('cp ' + pathtoWRFCHEM +'namelist.input_DUSTONLY' ' namelist.input')
     os.system('ln -sf ' + pathtoWPS + 'met_em* ' + pathtoWRFCHEM)
     #os.system('ln -sf ' + pathtoPWCE + 'wrfem_00to12z_d01 emissopt3_d01')
     os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g1-ab.bin emissopt3_d01')
     os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g1-bb.bin emissfire_d01')
     os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g1-gocartBG.bin wrf_gocart_backg')
     logger.info('emission files linked. Now amending namelist.input.')
     # Compute run time
     dt_1 = calendar.timegm(idate)
     dt_2 = calendar.timegm(fdate)
     dt = datetime.timedelta(seconds=(dt_2 - dt_1))
     days = dt.days
     hrs = math.floor(dt.seconds/3600.0)
     mins = ((dt.seconds/3600.0) - hrs) * 60.0
     secs = 0 # Assumed!
 
     # Compute dx,dy for each domain
     dxs = [dx*1000]
     if domains != 1:
         for idx in range(1,domains):
             child_dx = dxs[idx-1] * 1.0/parent_grid_ratio[idx]
             dxs.append(child_dx)
     dys = [dy*1000]
     if domains != 1:
         for idx in range(1,domains):
             child_dy = dys[idx-1] * 1.0/parent_grid_ratio[idx]
             dys.append(child_dy)
    
     # If all namelist values begin on column 38:
     edit_namelist_input("run_days","%01u" %days + ',')
     edit_namelist_input("run_hours",'0,')
     edit_namelist_input("run_minutes","%01u" %mins + ',')
     edit_namelist_input("run_seconds","%01u" %secs + ',')
     edit_namelist_input("start_year", (y1+', ')*domains)
     edit_namelist_input("start_month", (mth1+', ')*domains)
     edit_namelist_input("start_day", (d1+', ')*domains)
     edit_namelist_input("start_hour", (h1+', ')*domains)
     edit_namelist_input("start_minute", (min1+', ')*domains)
     edit_namelist_input("start_second", (s1+', ')*domains)
     edit_namelist_input("end_year", (y2+', ')*domains)
     edit_namelist_input("end_month", (mth2+', ')*domains)
     edit_namelist_input("end_day", (d2+', ')*domains)
     edit_namelist_input("end_hour", (h2+', ')*domains)
     edit_namelist_input("end_minute", (min2+', ')*domains)
     edit_namelist_input("end_second", (s2+', ')*domains)
     edit_namelist_input("interval_seconds", str(int(interval*3600))+',')
     edit_namelist_input("time_step",'180,')
     edit_namelist_input("max_dom",'1,')
     edit_namelist_input("e_we", ', '.join([str(w) for w in e_we])+',')
     edit_namelist_input("e_sn", ', '.join([str(s) for s in e_sn])+',')
     edit_namelist_input("num_metgrid_levels", str(atmos_levs)+',')
     edit_namelist_input("dx", ', '.join([str(d) for d in dxs])+',')
     edit_namelist_input("dy", ', '.join([str(d) for d in dys])+',')
     edit_namelist_input("i_parent_start", ', '.join([str(i) for i in i_start])+',')
     edit_namelist_input("j_parent_start", ', '.join([str(j) for j in j_start])+',')
     edit_namelist_input("parent_grid_ratio",', '.join([str(p) for p in parent_grid_ratio])+',') 
     edit_namelist_input("io_form_auxinput5",'0,')
     edit_namelist_input("io_form_auxinput6",'0,')
     edit_namelist_input("io_form_auxinput7",'0,')
     edit_namelist_input("io_form_auxinput8",'0,')
     edit_namelist_input("io_form_auxinput12",'0,')
     edit_namelist_input("io_form_auxinput13",'0,')
     edit_namelist_input("chem_opt",'401,')
 
     # doing real.exe for convert_emiss.exe
     intelligent_mpirun('real')
     os.system('rm rsl*')
     logger.info('Now cleaning mpi logfiles for real.exe and editing namelist.input for convert.exe.')
     edit_namelist_input("io_form_auxinput5",'2,')
     edit_namelist_input("io_form_auxinput6",'2,')
     edit_namelist_input("io_form_auxinput7",'2,')
     edit_namelist_input("io_form_auxinput8",'2,')
     edit_namelist_input("io_form_auxinput12",'2,')
     edit_namelist_input("io_form_auxinput13",'2,')
     add_namelist_input(" io_form_auxinput13 = 2,", " frames_per_auxinput6 =1,")
     add_namelist_input(" frames_per_auxinput6 =1,"," frames_per_auxinput7 =1,")
     add_namelist_input(" frames_per_auxinput7 =1,"," frames_per_auxinput8 =1,")
     add_namelist_input(" frames_per_auxinput8 =1,"," frames_per_auxinput13 =1,")
     edit_namelist_input("chem_opt",'301',',')
     edit_namelist_input("io_style_emissions",'2,')
     edit_namelist_input("emiss_opt",'5',',')
     intelligent_mpirun('convert_emiss')
     os.system('rm rsl*')
     # doing real.exe and wrf.exe after convert_emiss.exe
     logger.info('editing namelist for final real.exe and wrf.exe for coarsest domain')
     edit_namelist_input("run_hours",'6,')
     edit_namelist_input("frames_per_outfile",'1,')
     edit_namelist_input("io_form_auxinput5",'2,')
     edit_namelist_input("io_form_auxinput6",'0,')
     edit_namelist_input("io_form_auxinput7",'0,')
     edit_namelist_input("io_form_auxinput8",'0,')
     edit_namelist_input("io_form_auxinput12",'0,')
     edit_namelist_input("io_form_auxinput13",'0,')
     edit_namelist_input("frames_per_auxinput6",'0,')
     edit_namelist_input("frames_per_auxinput7",'0,')
     edit_namelist_input("frames_per_auxinput8",'0,')
     edit_namelist_input("frames_per_auxinput13",'0,') 
     edit_namelist_input("e_vert",'31,') 
     add_namelist_input(" smooth_option              = 0"," p_top_requested = 5000,")
     add_namelist_input(" p_top_requested = 5000,","zap_close_levels = 50")
     add_namelist_input("zap_close_levels = 50","interp_type = 1")
     add_namelist_input("interp_type = 1","t_extrap_type = 2")
     add_namelist_input("t_extrap_type = 2","force_sfc_in_vinterp = 0")
     add_namelist_input("force_sfc_in_vinterp = 0","use_levels_below_ground = .true.")
     add_namelist_input("use_levels_below_ground = .true.","use_surface = .true.")
     add_namelist_input("use_surface = .true.","lagrange_order = 1")
     add_namelist_input(" mp_physics                 = 2, 2, 2, 2,","progn = 0")
     edit_namelist_input("ra_sw_physics",'2,')
     edit_namelist_input("radt",'30,')
     edit_namelist_input("cudt",'0')
     add_namelist_input(" cudt = 0","ishallow = 0")
     add_namelist_input(" sf_urban_physics           = 0, 0, 0, 0","mp_zero_out = 2,")
     add_namelist_input("mp_zero_out = 2,","mp_zero_out_thresh = 1.e-12,")
     add_namelist_input("mp_zero_out_thresh = 1.e-12,","maxiens = 1,")
     add_namelist_input("maxiens = 1,","maxens = 3,")
     add_namelist_input("maxens = 3,","maxens2 = 3,")
     add_namelist_input("maxens2 = 3,","maxens3 = 16,")
     add_namelist_input("maxens3 = 16,","ensdim = 144,")
     add_namelist_input("ensdim = 144,","cu_rad_feedback = .true.,")
     add_namelist_input("&dynamics","rk_ord = 3,")
     edit_namelist_input("diff_6th_opt",'0,')
     edit_namelist_input("dampcoef",'0.01,')
     edit_namelist_input("moist_adv_opt",'2,')
     edit_namelist_input("scalar_adv_opt",'2,')
     add_namelist_input(" scalar_adv_opt = 2,","chem_adv_opt = 2, 0, 0,")
     add_namelist_input("chem_adv_opt = 2, 0, 0,","tke_adv_opt = 2, 0, 0,")
     add_namelist_input("tke_adv_opt = 2, 0, 0,","time_step_sound = 4, 4, 4,")
     add_namelist_input("time_step_sound = 4, 4, 4,","h_mom_adv_order = 5, 5, 5,")
     add_namelist_input("h_mom_adv_order = 5, 5, 5,","v_mom_adv_order = 3, 3, 3,")
     add_namelist_input("v_mom_adv_order = 3, 3, 3,","h_sca_adv_order = 5, 5, 5,")
     add_namelist_input("h_sca_adv_order = 5, 5, 5,","v_sca_adv_order = 3, 3, 3,") 
     edit_namelist_input("chemdt",'60,')
     edit_namelist_input("io_style_emissions",'1,')
     edit_namelist_input("dmsemis_opt",'1,')
     edit_namelist_input("seas_opt",'1,')
     edit_namelist_input("plumerisefire_frq",'30,')
     intelligent_mpirun('real')
     #solving the error of opening file wrfchemi_00z_d01
     os.system('cp ' + pathtoWRFCHEM +'wrfchemi_d01' ' wrfchemi_00z_d01')
     os.system('rm rsl*')
     intelligent_mpirun('wrf')
     logger.info('finished real.exe now wrf.exe for domain 1 DO1' )
     wrfd01_time = detit.now()
     logger.info('Duration for WRF D01 to complete: {}'.format(wrfd01_time - prep_time)) 
 
     if ndown_d2:
         #remove the links for met and emiss files
     	os.chdir(pathtoWRFCHEM)
     	os.system('cp ' + pathtoWRFCHEM +'namelist.input_DUSTONLY' ' namelist.input')
         os.system('rm rsl*')
         os.system('rm met_em*')
         #create new links for grid2 met and emiss files
         os.system('rm wrf_gocart_backg emissopt3_d01 emissfire_d01 wrfbdy_d01 wrfinput_d01 wrffirechemi_d01 wrfchemi_gocart_bg_d01 wrfchemi_d01')
     	os.system('ln -sf ' + pathtoWPS + 'met_em.d02* ' + pathtoWRFCHEM)
         [os.rename(f, f.replace('met_em.d02', 'met_em.d01')) for f in glob.glob('met_em.d02*') if not f.startswith('.')]
     	os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g2-ab.bin emissopt3_d01')
     	os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g2-bb.bin emissfire_d01')
     	os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g2-gocartBG.bin wrf_gocart_backg')
         #editing namelist from namelist.inputWRFrun03 to namelist.input_D02 for real.exe
         edit_namelist_input("time_step",'60,')
         edit_namelist_input("s_we",'1, 1, 1')
         edit_namelist_input("e_we",'76, 97, 136')
         edit_namelist_input("s_sn",'1, 1, 1')
         edit_namelist_input("e_sn",'73, 106, 157')
         edit_namelist_input("s_vert",'1, 1, 1')
         edit_namelist_input("dx",'9000.0000, 3000.0000, 1000.0000')
         edit_namelist_input("dy",'9000.0000, 3000.0000, 1000.0000')
         edit_namelist_input("i_parent_start",'26, 22, 22')
         edit_namelist_input("j_parent_start",'7, 15, 32')
         #run first real.exe
         intelligent_mpirun('real')
         os.system('rm rsl*')
         #edit namelist  from namelist.input_D02 to namelist.input_CE_D02 for convert_emiss.exe
         logger.info('Now cleaning mpi logfiles of real.exe and editing namelist.input for convert.exe.')
         edit_namelist_input("io_form_auxinput5",'2,')
         edit_namelist_input("io_form_auxinput6",'2,')
         edit_namelist_input("io_form_auxinput7",'2,')
         edit_namelist_input("io_form_auxinput8",'2,')
         edit_namelist_input("io_form_auxinput12",'2,')
         edit_namelist_input("io_form_auxinput13",'2,')
         add_namelist_input(" io_form_auxinput13 = 2,", " frames_per_auxinput6 =1,")
         add_namelist_input(" frames_per_auxinput6 =1,"," frames_per_auxinput7 =1,")
         add_namelist_input(" frames_per_auxinput7 =1,"," frames_per_auxinput8 =1,")
         add_namelist_input(" frames_per_auxinput8 =1,"," frames_per_auxinput13 =1,")
         edit_namelist_input("chem_opt",'301',',')
         edit_namelist_input("io_style_emissions",'2,')
         edit_namelist_input("emiss_opt",'5',',')
         intelligent_mpirun('convert_emiss')
         os.system('rm rsl*')
         #edit namelist  from namelist.input_CE_D02 to namelist.input_D02 for second real.exe
         logger.info('now running real.exe beofre ndown.exe')
         edit_namelist_input("io_form_auxinput5",'2,')
         edit_namelist_input("io_form_auxinput6",'0,')
         edit_namelist_input("io_form_auxinput7",'0,')
         edit_namelist_input("io_form_auxinput8",'0,')
         edit_namelist_input("io_form_auxinput12",'0,')
         edit_namelist_input("io_form_auxinput13",'0,')
         edit_namelist_input("frames_per_auxinput6",'0,')
         edit_namelist_input("frames_per_auxinput7",'0,')
         edit_namelist_input("frames_per_auxinput8",'0,')
         edit_namelist_input("frames_per_auxinput13",'0,')
         intelligent_mpirun('real')
         os.system('rm rsl*')
         #rename real.exe for ndown.exe
         os.system('cp ' + pathtoWRFCHEM +'wrfinput_d01' ' wrfndi_d02')
         #edit namelist  from namelist.input_D02 to namelist.inputNdown_D01D02 for ndown.exe 
         edit_namelist_input("time_step",'180,')
         edit_namelist_input("max_dom",'2,')
         edit_namelist_input("s_we",'1, 1, 1, 1')
         edit_namelist_input("e_we",'90, 76, 97, 136')
         edit_namelist_input("s_sn",'1, 1, 1, 1')
         edit_namelist_input("e_sn",'85, 73, 106, 157')
         edit_namelist_input("s_vert",'1, 1, 1, 1')
         edit_namelist_input("dx",'27000.0000, 9000.0000, 3000.0000, 1000.0000')
         edit_namelist_input("dy",'27000.0000, 9000.0000, 3000.0000, 1000.0000')
         edit_namelist_input("i_parent_start",'1, 26, 22, 22')
         edit_namelist_input("j_parent_start",'1, 7, 15, 32')
         intelligent_mpirun('ndown')
         #moving wrfoutput of D01 into a seprate directory
         os.system('mv ' + pathtoWRFCHEM +'wrfout* ' + pathtowrfout)
         os.chdir(pathtowrfout)
         [os.rename(f, f.replace('wrfout_d01', 'wrfout_D01')) for f in glob.glob('wrfout_d01*') if not f.startswith('.')]
         os.chdir(pathtoWRFCHEM)
         #edit namelist  from namelist.inputNdown_D01D02 to namelist.input_D02 for final wrf.exe
         os.system('rm wrfinput_d01 wrfbdy_d01 wrfndi_d02')
         os.system('mv ' + 'wrfinput_d02' ' wrfinput_d01')
         os.system('mv ' + 'wrfbdy_d02' ' wrfbdy_d01')
         logger.info('now editing namelist for wrf.exe')
         edit_namelist_input("time_step",'60,')
         edit_namelist_input("max_dom",'1,')
         edit_namelist_input("s_we",'1, 1, 1')
         edit_namelist_input("e_we",'76, 97, 136')
         edit_namelist_input("s_sn",'1, 1, 1')
         edit_namelist_input("e_sn",'73, 106, 157')
         edit_namelist_input("s_vert",'1, 1, 1')
         edit_namelist_input("dx",'9000.0000, 3000.0000, 1000.0000')
         edit_namelist_input("dy",'9000.0000, 3000.0000, 1000.0000')
         edit_namelist_input("i_parent_start",'26, 22, 22')
         edit_namelist_input("j_parent_start",'7, 15, 32')
         edit_namelist_input("run_hours",'6,')
         edit_namelist_input("frames_per_outfile",'1,')
         edit_namelist_input("io_form_auxinput5",'2,')
         edit_namelist_input("io_form_auxinput6",'0,')
         edit_namelist_input("io_form_auxinput7",'0,')
         edit_namelist_input("io_form_auxinput8",'0,')
         edit_namelist_input("io_form_auxinput12",'0,')
         edit_namelist_input("io_form_auxinput13",'0,')
         edit_namelist_input("frames_per_auxinput6",'0,')
         edit_namelist_input("frames_per_auxinput7",'0,')
         edit_namelist_input("frames_per_auxinput8",'0,')
         edit_namelist_input("frames_per_auxinput13",'0,') 
         edit_namelist_input("e_vert",'31,') 
         add_namelist_input(" smooth_option              = 0"," p_top_requested = 5000,")
         add_namelist_input(" p_top_requested = 5000,","zap_close_levels = 50")
         add_namelist_input("zap_close_levels = 50","interp_type = 1")
         add_namelist_input("interp_type = 1","t_extrap_type = 2")
         add_namelist_input("t_extrap_type = 2","force_sfc_in_vinterp = 0")
         add_namelist_input("force_sfc_in_vinterp = 0","use_levels_below_ground = .true.")
         add_namelist_input("use_levels_below_ground = .true.","use_surface = .true.")
         add_namelist_input("use_surface = .true.","lagrange_order = 1")
         add_namelist_input(" mp_physics                 = 2, 2, 2, 2,","progn = 0")
         edit_namelist_input("ra_sw_physics",'2,')
         edit_namelist_input("radt",'30,')
         edit_namelist_input("cudt",'0')
         add_namelist_input(" cudt = 0","ishallow = 0")
         add_namelist_input(" sf_urban_physics           = 0, 0, 0, 0","mp_zero_out = 2,")
         add_namelist_input("mp_zero_out = 2,","mp_zero_out_thresh = 1.e-12,")
         add_namelist_input("mp_zero_out_thresh = 1.e-12,","maxiens = 1,")
         add_namelist_input("maxiens = 1,","maxens = 3,")
         add_namelist_input("maxens = 3,","maxens2 = 3,")
         add_namelist_input("maxens2 = 3,","maxens3 = 16,")
         add_namelist_input("maxens3 = 16,","ensdim = 144,")
         add_namelist_input("ensdim = 144,","cu_rad_feedback = .true.,")
         add_namelist_input("&dynamics","rk_ord = 3,")
         edit_namelist_input("diff_6th_opt",'0,')
         edit_namelist_input("dampcoef",'0.01,')
         edit_namelist_input("moist_adv_opt",'2,')
         edit_namelist_input("scalar_adv_opt",'2,')
         add_namelist_input(" scalar_adv_opt = 2,","chem_adv_opt = 2, 0, 0,")
         add_namelist_input("chem_adv_opt = 2, 0, 0,","tke_adv_opt = 2, 0, 0,")
         add_namelist_input("tke_adv_opt = 2, 0, 0,","time_step_sound = 4, 4, 4,")
         add_namelist_input("time_step_sound = 4, 4, 4,","h_mom_adv_order = 5, 5, 5,")
         add_namelist_input("h_mom_adv_order = 5, 5, 5,","v_mom_adv_order = 3, 3, 3,")
         add_namelist_input("v_mom_adv_order = 3, 3, 3,","h_sca_adv_order = 5, 5, 5,")
         add_namelist_input("h_sca_adv_order = 5, 5, 5,","v_sca_adv_order = 3, 3, 3,") 
         edit_namelist_input("chemdt",'60,')
         edit_namelist_input("io_style_emissions",'1,')
         edit_namelist_input("dmsemis_opt",'1,')
         edit_namelist_input("seas_opt",'1,')
         edit_namelist_input("plumerisefire_frq",'30,')
         os.system('mv ' +'wrfchemi_d01' ' wrfchemi_00z_d01')
         intelligent_mpirun('wrf')
         logger.info('finished wrf.exe for domain 2 DO2' )
         wrfd02_time = detit.now()
         logger.info('Duration for WRF D02 to complete: {}'.format(wrfd02_time - wrfd01_time)) 
 
     if ndown_d3:
         #remove the links for met and emiss files
     	os.chdir(pathtoWRFCHEM)
     	os.system('cp ' + pathtoWRFCHEM +'namelist.input_DUSTONLY' ' namelist.input')
         os.system('rm rsl*')
         os.system('rm met_em*')
         #create new links for grid2 met and emiss files
         os.system('rm wrf_gocart_backg emissopt3_d01 emissfire_d01 wrfbdy_d01 wrfinput_d01 wrffirechemi_d01 wrfchemi_gocart_bg_d01 wrfchemi_d01')
     	os.system('ln -sf ' + pathtoWPS + 'met_em.d03* ' + pathtoWRFCHEM)
         [os.rename(f, f.replace('met_em.d03', 'met_em.d01')) for f in glob.glob('met_em.d03*') if not f.startswith('.')]
     	os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g3-ab.bin emissopt3_d01')
     	os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g3-bb.bin emissfire_d01')
     	os.system('ln -sf ' + pathtoPCS + 'FIRE-RRCH-T-'+y1+'-'+mth1+'-'+d1+'-000000-g3-gocartBG.bin wrf_gocart_backg')
         #editing namelist from namelist.inputWRFrun03 to namelist.input_D02 for real.exe
         edit_namelist_input("time_step",'18,')
         edit_namelist_input("s_we",'1, 1, 1')
         edit_namelist_input("e_we",'97, 136')
         edit_namelist_input("s_sn",'1, 1, 1')
         edit_namelist_input("e_sn",'106, 157')
         edit_namelist_input("s_vert",'1, 1, 1')
         edit_namelist_input("dx",'3000.0000, 1000.0000')
         edit_namelist_input("dy",'3000.0000, 1000.0000')
         edit_namelist_input("i_parent_start",'22, 22')
         edit_namelist_input("j_parent_start",'15, 32')
         #run first real.exe
         intelligent_mpirun('real')
         os.system('rm rsl*')
         #edit namelist  from namelist.input_D02 to namelist.input_CE_D02 for convert_emiss.exe
         logger.info('Now cleaning mpi logfiles of real.exe and editing namelist.input for convert.exe.')
         edit_namelist_input("io_form_auxinput5",'2,')
         edit_namelist_input("io_form_auxinput6",'2,')
         edit_namelist_input("io_form_auxinput7",'2,')
         edit_namelist_input("io_form_auxinput8",'2,')
         edit_namelist_input("io_form_auxinput12",'2,')
         edit_namelist_input("io_form_auxinput13",'2,')
         add_namelist_input(" io_form_auxinput13 = 2,", " frames_per_auxinput6 =1,")
         add_namelist_input(" frames_per_auxinput6 =1,"," frames_per_auxinput7 =1,")
         add_namelist_input(" frames_per_auxinput7 =1,"," frames_per_auxinput8 =1,")
         add_namelist_input(" frames_per_auxinput8 =1,"," frames_per_auxinput13 =1,")
         edit_namelist_input("chem_opt",'301',',')
         edit_namelist_input("io_style_emissions",'2,')
         edit_namelist_input("emiss_opt",'5',',')
         intelligent_mpirun('convert_emiss')
         os.system('rm rsl*')
         #edit namelist  from namelist.input_CE_D02 to namelist.input_D02 for second real.exe
         logger.info('now running real.exe beofre ndown.exe')
         edit_namelist_input("io_form_auxinput5",'2,')
         edit_namelist_input("io_form_auxinput6",'0,')
         edit_namelist_input("io_form_auxinput7",'0,')
         edit_namelist_input("io_form_auxinput8",'0,')
         edit_namelist_input("io_form_auxinput12",'0,')
         edit_namelist_input("io_form_auxinput13",'0,')
         edit_namelist_input("frames_per_auxinput6",'0,')
         edit_namelist_input("frames_per_auxinput7",'0,')
         edit_namelist_input("frames_per_auxinput8",'0,')
         edit_namelist_input("frames_per_auxinput13",'0,')
         intelligent_mpirun('real')
         os.system('rm rsl*')
         #rename real.exe for ndown.exe
         os.system('cp ' + pathtoWRFCHEM +'wrfinput_d01' ' wrfndi_d02')
         #edit namelist  from namelist.input_D02 to namelist.inputNdown_D01D02 for ndown.exe 
         edit_namelist_input("time_step",'180,')
         edit_namelist_input("max_dom",'2,')
         edit_namelist_input("s_we",'1, 1, 1')
         edit_namelist_input("e_we",'76, 97, 136')
         edit_namelist_input("s_sn",'1, 1, 1')
         edit_namelist_input("e_sn",'73, 106, 157')
         edit_namelist_input("s_vert",'1, 1, 1')
         edit_namelist_input("dx",'9000.0000, 3000.0000, 1000.0000')
         edit_namelist_input("dy",'9000.0000, 3000.0000, 1000.0000')
         edit_namelist_input("i_parent_start",'26, 22, 22')
         edit_namelist_input("j_parent_start",'7, 15, 32')
         intelligent_mpirun('ndown')
         #moving wrfoutput of D01 into a seprate directory
         os.system('mv ' + pathtoWRFCHEM +'wrfout* ' + pathtowrfout)
         os.chdir(pathtowrfout)
         [os.rename(f, f.replace('wrfout_d01', 'wrfout_D02')) for f in glob.glob('wrfout_d01*') if not f.startswith('.')]
         os.chdir(pathtoWRFCHEM)
         #edit namelist  from namelist.inputNdown_D01D02 to namelist.input_D02 for final wrf.exe
         os.system('rm wrfinput_d01 wrfbdy_d01 wrfndi_d02')
         os.system('mv ' + 'wrfinput_d02' ' wrfinput_d01')
         os.system('mv ' + 'wrfbdy_d02' ' wrfbdy_d01')
         logger.info('now editing namelist for wrf.exe')
         edit_namelist_input("time_step",'18,')
         edit_namelist_input("max_dom",'1,')
         edit_namelist_input("s_we",'1, 1')
         edit_namelist_input("e_we",'97, 136')
         edit_namelist_input("s_sn",'1, 1')
         edit_namelist_input("e_sn",'106, 157')
         edit_namelist_input("s_vert",'1, 1')
         edit_namelist_input("dx",'3000.0000, 1000.0000')
         edit_namelist_input("dy",'3000.0000, 1000.0000')
         edit_namelist_input("i_parent_start",'22, 22')
         edit_namelist_input("j_parent_start",'15, 32')
         edit_namelist_input("run_hours",'6,')
         edit_namelist_input("frames_per_outfile",'1,')
         edit_namelist_input("io_form_auxinput5",'2,')
         edit_namelist_input("io_form_auxinput6",'0,')
         edit_namelist_input("io_form_auxinput7",'0,')
         edit_namelist_input("io_form_auxinput8",'0,')
         edit_namelist_input("io_form_auxinput12",'0,')
         edit_namelist_input("io_form_auxinput13",'0,')
         edit_namelist_input("frames_per_auxinput6",'0,')
         edit_namelist_input("frames_per_auxinput7",'0,')
         edit_namelist_input("frames_per_auxinput8",'0,')
         edit_namelist_input("frames_per_auxinput13",'0,') 
         edit_namelist_input("e_vert",'31,') 
         add_namelist_input(" smooth_option              = 0"," p_top_requested = 5000,")
         add_namelist_input(" p_top_requested = 5000,","zap_close_levels = 50")
         add_namelist_input("zap_close_levels = 50","interp_type = 1")
         add_namelist_input("interp_type = 1","t_extrap_type = 2")
         add_namelist_input("t_extrap_type = 2","force_sfc_in_vinterp = 0")
         add_namelist_input("force_sfc_in_vinterp = 0","use_levels_below_ground = .true.")
         add_namelist_input("use_levels_below_ground = .true.","use_surface = .true.")
         add_namelist_input("use_surface = .true.","lagrange_order = 1")
         add_namelist_input(" mp_physics                 = 2, 2, 2, 2,","progn = 0")
         edit_namelist_input("ra_sw_physics",'2,')
         edit_namelist_input("radt",'30,')
         edit_namelist_input("cudt",'0')
         add_namelist_input(" cudt = 0","ishallow = 0")
         add_namelist_input(" sf_urban_physics           = 0, 0, 0, 0","mp_zero_out = 2,")
         add_namelist_input("mp_zero_out = 2,","mp_zero_out_thresh = 1.e-12,")
         add_namelist_input("mp_zero_out_thresh = 1.e-12,","maxiens = 1,")
         add_namelist_input("maxiens = 1,","maxens = 3,")
         add_namelist_input("maxens = 3,","maxens2 = 3,")
         add_namelist_input("maxens2 = 3,","maxens3 = 16,")
         add_namelist_input("maxens3 = 16,","ensdim = 144,")
         add_namelist_input("ensdim = 144,","cu_rad_feedback = .true.,")
         add_namelist_input("&dynamics","rk_ord = 3,")
         edit_namelist_input("diff_6th_opt",'0,')
         edit_namelist_input("dampcoef",'0.01,')
         edit_namelist_input("moist_adv_opt",'2,')
         edit_namelist_input("scalar_adv_opt",'2,')
         add_namelist_input(" scalar_adv_opt = 2,","chem_adv_opt = 2, 0, 0,")
         add_namelist_input("chem_adv_opt = 2, 0, 0,","tke_adv_opt = 2, 0, 0,")
         add_namelist_input("tke_adv_opt = 2, 0, 0,","time_step_sound = 4, 4, 4,")
         add_namelist_input("time_step_sound = 4, 4, 4,","h_mom_adv_order = 5, 5, 5,")
         add_namelist_input("h_mom_adv_order = 5, 5, 5,","v_mom_adv_order = 3, 3, 3,")
         add_namelist_input("v_mom_adv_order = 3, 3, 3,","h_sca_adv_order = 5, 5, 5,")
         add_namelist_input("h_sca_adv_order = 5, 5, 5,","v_sca_adv_order = 3, 3, 3,") 
         edit_namelist_input("chemdt",'60,')
         edit_namelist_input("io_style_emissions",'1,')
         edit_namelist_input("dmsemis_opt",'1,')
         edit_namelist_input("seas_opt",'1,')
         edit_namelist_input("plumerisefire_frq",'30,')
         os.system('mv ' +'wrfchemi_d01' ' wrfchemi_00z_d01')
         intelligent_mpirun('wrf')
         os.system('mv ' + pathtoWRFCHEM +'wrfout* ' + pathtowrfout)
         os.chdir(pathtowrfout)
         [os.rename(f, f.replace('wrfout_d01', 'wrfout_D03')) for f in glob.glob('wrfout_d01*') if not f.startswith('.')]
         os.chdir(pathtoWRFCHEM)
         logger.info('finished wrf.exe for domain 3 DO3 and outputs are transfered' )
         wrfd03_time = detit.now()
         logger.info('Duration for WRF D03 to complete: {}'.format(wrfd03_time - wrfd02_time)) 
         logger.info('Duration for whole simulation to complete: {}'.format(wrfd03_time - start_time)) 
              
 #edit namelist
 #run ndown.exe
 #edit namelist
 #mv wrfoutput of past domain
 #run wrf.exe
 	
 
 
 else:
     print "Pre-processing complete. Exiting Python script."
