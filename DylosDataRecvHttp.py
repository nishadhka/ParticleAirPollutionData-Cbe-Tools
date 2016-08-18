# Send Dylos\texttrademark data into Think Speak internet of things service
#!/usr/bin/python
import sqlite3 as lite
import logging
import httplib, urllib
from time import localtime, strftime
import time

logger = logging.getLogger('lbm1')
hdlr = logging.FileHandler('pyts.log')
formatter = logging.Formatter('%(asctime)s: %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
logger.info("tss")

con = lite.connect('dylos.db')
try:
  with con:
    cur = con.cursor()
    cur.execute("SELECT * FROM data ORDER BY SNo DESC LIMIT 1")
    a= [str(i[1]) for i in cur.fetchall()]
    b = map(str.strip,a)
    c= str(b).strip("[']") 
    d= c.split(',')
    logger.info("dfdb")
except:
    logger.exception('dbyr')
finally:
   if con:
      con.close() 

def doit():
        #a =1234
        #b =123456
        params = urllib.urlencode({'field1': d[1], 'field2': d[2],'key':'1ACXSOW1ZFCYWGZF'})
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("api.thingspeak.com:80")

        try:
                conn.request("POST", "/update", params, headers)
                response = conn.getresponse()
                data = response.read()
                conn.close()
                logger.info('sdf')
        except:
                #print "connection failed"
                logger.exception('cf')
#sleep for 16 seconds (api limit of 15 secs)
if __name__ == "__main__":
#    dbit()
    doit()
