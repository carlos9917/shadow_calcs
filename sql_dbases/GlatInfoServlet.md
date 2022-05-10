# Summary on the possible parameters

GlatInfoServlet glat information service version 1.12, 2021-02-17 14:52

No data fetched!

You must specify one of the commands:
  command=stationlist: To obtain a list of stations.
  command=parameterlist: To obtain a list of parameters.
  command=datatypelist: To obtain a list of datatypes.
  command=metlist: To obtain a list of meteorologists.
  command=brandlist: To obtain a list of station brands.
  command=roadsensortypes: To obtain a list of road sensor types.
  command=status: To get some status and statistic information about the service.
  command=loaddata: To load data for a specific station and datatype. Station MUST be specified.
  command=observations: To dump recent observations.
  command=latesttime: To get information about data availability. Station MUST be specified.

Additional commands available:
  station=<id> The station to get data or information for.
  datatype=<number> The datatype to get data for, default is observations.
  time=<time> The time to use, default is now. Timeformat command will be used.
  formatter=name: Name of the formatter to use. Default format is a simple comma separated format.
    If formatter=full is specified additional information is supplied in csv format.
  stationtypes= Any comma separated combination of road,synop,test,wind,ice,radar,region,weatherarea,webcam,stretch,forecastimage,all:
    Used to specify the stationtypes to select, default is road.
  stations=id|id-id[{,id|id-id}]: Used to select specific stations, default all stations for the stationstype will be used.
  stationgroup=id Return only the stations from the specified station group. The output will be sorted according to the station group
    If the subcommand "user=" is specified id is the name of a station group owned by user, otherwise id is the id of a global station group
  timeformat=format: The time format to use in the output. Follows SimpleDateFormat. Default is yyyyMMddHHmm.
  parameters=id|id-id[{,id|id-id}]: Used to select specific parameters, default all parameters will be used. Currently ignored by the loaddata command.
  period=n[H|M|S]: Used to specify how far back to fetch the observations, default is 4 hours, maximum 25 hours.

Example: http://vejvejr.dk:443/glatinfoservice/GlatInfoServlet?command=stationList&formatter=full

Note that this service is quite quiet, which means if something wrong is specified defaults will be used and if nothing could be retrived you will see this message.
