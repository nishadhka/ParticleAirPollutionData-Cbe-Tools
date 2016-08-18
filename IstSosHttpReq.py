import json
import requests
import time
import decimal
import pandas as pd


def dropzeros(number):
    mynum = decimal.Decimal(number).normalize()
    return mynum.__trunc__() if not mynum % 1 else float(mynum) 

db=pd.read_csv('Stations.csv')
lata=db['Lat'].tolist()
longia=db['Long'].tolist()
addra=db['Name'].tolist()
codea=db['STATION CODE'].tolist()
elea=db['elevation'].tolist()
jsonFile = open("procedure.json", "r")
data1 = json.load(jsonFile)
jsonFile.close()
for lat,longi,addr,code,ele in zip(lata,longia,addra,codea,elea):
    data1['system_id']=str(dropzeros(code))
    data1['system']=str(dropzeros(code))
    data1['description']=str(addr)
    data1['location']['geometry']['coordinates']=[str(longi),str(lat),str(ele)]
    data1['location']['properties']['name']=str(dropzeros(code))
    url = 'http://localhost/istsos/wa/istsos/services/cbed/procedures'
    data_json = json.dumps(data1, sort_keys=True, indent=4, separators=(',', ': '))
    r = requests.post(url, data=data_json)
    print(r.status_code)
