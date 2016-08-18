import pandas as pd

db8=pd.read_csv('Dylos_raw.csv')
db8T=pd.DataFrame(db8.time.str.split("T").tolist())


db8T.columns=['date','time2']
db8['date']=db8T.date
db8['time2']=db8T.time2

hd=pd.read_csv('cbe_wather_2014.csv')
hd["IST"]=pd.to_datetime(hd["IST"])
hd["IST"] = hd['IST'].apply(lambda x: x.strftime("%Y-%m-%d"))

hd1=hd[['IST','Mean Humidity']]
hd1.columns=['date','Hum']

db9=db8.set_index('date')
hd2=hd1.set_index('date')

db10=db9.join(hd2)


db11=db10[~db10.Hum.isnull()]



def switch(x):
    return {  
      0<=x<=19:10.1,
      20<=x<=24:8.75,
      25<=x<=29:8,
      30<=x<=34:8,
      35<=x<=39:8,
      40<=x<=44:7,
      45<=x<=49:6,
      50<=x<=54:5.75,
      55<=x<=59:5.5,
      60<=x<=64:5.5,
      65<=x<=69:3.5,
      70<=x<=74:3.5,
      75<=x<=79:3.75,
      80<=x<=84:2.25,
      85<=x<=89:1.5,
      90<=x<=94:0.825,
      95<=x<=100:0.525
      }[1]


def search_range(char):
    x=char
    return switch(x)



db11['cf'] = db11['Hum'].map(search_range)


db11['PM25']=db11.pm05*3531.5*5.89E-7
db11['PM10']=db11.pm25*3531.5*1.21E-4


db11['CPM25']=db11.PM25*(db11.Hum*0.01)*db11.cf
db11['CPM10']=db11.PM10*(db11.Hum*0.01)*db11.cf


db11.to_csv('Dylos_output.csv')
