#particle Air pollution Data for Coimbatore
##Real time monitoring and modeling tools

This repository contains scripts for following purposes

1. Particulate pollution data collection from Dylos air quality monitor Viz.,DylosDataRecvSMS.py, DylosDataRecvHttp.py, DylosDataCountToMass.py

1. Emission inventory calculation for Coimbatore region from Industry(EmissInvIndustryCalc.py), Resdiential(EmissInvResidentailCalc.py), Transport(EmissInvTransportCalc.py), Windblown dust(EmissInvWindblownCalc.py)

1. Edgar emission inventory processor to make it suitable for WRF CHEM simulation(EdgarEIProcessorNCO.py), to join with Coimbatore region emission inventory (CbeEiEdgarJoin.py)

1. Real time automatic execution of WRF CHEM with ndown based one way nesting option(WrfChemRTExecuter.py)

1. Sample code for accessing IstSOS through HTTP request (IstSosHttpReq.py)

1. R statcial programming code for demonstrating platform independent advantages of sensor observation service (SosAdvantagesExEval.R)