library("sos4R"); library("xts");library("openair")

# 1. step
ist.converters <- SosDataFieldConvertingFunctions("urn:...:time:iso8601" = sosConvertTime)

monitorSOS.get <- SOS(url = "http://localhost/istsos/apm", dataFieldConverters = ist.converters)

modelSOS.get <- SOS(url = "http://localhost/istsos/wcoi", dataFieldConverters = ist.converters)


# 2. step

monitorSOS.timeperiod <- sosCreateEventTimeList(sosCreateTimePeriod(sos = monitorSOS.get,
begin = as.POSIXct("2015-01-14 00:00"),
end = as.POSIXct("2015-01-19 00:00")))
modelSOS.timeperiod <- sosCreateEventTimeList(sosCreateTimePeriod(sos = modelSOS.get,
begin = as.POSIXct("2015-01-14 00:00"),
end = as.POSIXct("2015-01-19 00:00")))


monitorSOS.offering <- sosOfferings(monitorSOS.get)[[1]]
modelSOS.offering <- sosOfferings(modelSOS.get)[[1]]


# 3. step


monitorSOS.obs <- getObservation(sos = monitorSOS.get, verbose = TRUE,
offering = monitorSOS.offering,
observedProperty = list("urn:ogc:def:parameter:x-istsos:1.0:dylos:pm25"),
eventTime = monitorSOS.timeperiod)
modelSOS.obs <- getObservation(sos = modelSOS.get, verbose = TRUE,
offering = modelSOS.offering,
observedProperty = list("urn:ogc:def:parameter:x-istsos:1.0:wrfchemaoi:pm25"),
eventTime = modelSOS.timeperiod)


monitorSOSD <- sosResult(monitorSOS.obs)
modelSOSD <- sosResult(modelSOS.obs)


# 4. step

cbind(a = x, monitorSOSD)
cbind(a = y, modelSOSD)

dat<-merge(monitorSOSD, modelSOSD)

a<-modStats(dat, obs = "y", mod = "x", type = "level_1")
write.csv(format(a, digits=2),'Evaluation_output.csv')
