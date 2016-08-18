#!/usr/bin/env python
import serial
import time
import gammu
import subprocess
import re
import sqlite3 as lite

ser = serial.Serial('/dev/dylos', 9600, timeout=60)
time.sleep(60)
line = ser.readline() 
now = time.strftime("%Y-%m-%dT%H:%M", time.localtime())
a =  "%s,%s" % (now,line)
print a
ser.close()
SMS = {
        'Class': 1,                            #SMS Class
        'Text': a,     #Message
        'SMSC': {'Location': 1},
        'Number': "+91SIMnumber",              #The phone number
      }
gamu_sm = gammu.StateMachine()
gamu_sm.ReadConfig()              #Read the default config file (~/.gammurc)
gamu_sm.Init()                    #Connect to the phone   
gamu_sm.SendSMS(SMS) 

con = lite.connect('dylos.db')
try:
   with con:
       cur = con.cursor()
       cur.execute("INSERT INTO data3 VALUES(?,?)", a)
finally:
    if con:
       con.close() 
